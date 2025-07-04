import pandas as pd
import requests
import json
from tqdm import tqdm
import time
import argparse
import threading
import concurrent.futures
from typing import Dict, Any, List
import os

# ANSI颜色代码
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"

# 全局变量
all_results = []
results_lock = threading.Lock()
processed_count = 0
processed_count_lock = threading.Lock()

def make_api_request(endpoint, params, max_retries=3, retry_delay=1):
    """通用API请求函数，带重试机制"""
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, params=params, timeout=60)
            if response.status_code == 200:
                return response.json(), None
            else:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                if attempt == max_retries - 1:
                    return None, error_msg
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            if attempt == max_retries - 1:
                return None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "连接错误，请检查API服务器是否启动"
            if attempt == max_retries - 1:
                return None, error_msg
        except Exception as e:
            error_msg = f"请求异常: {str(e)}"
            if attempt == max_retries - 1:
                return None, error_msg

        if attempt < max_retries - 1:
            time.sleep(retry_delay * (attempt + 1))  # 递增延迟

    return None, "达到最大重试次数"

def evaluate_content_score(toxic_sentence, neutral_sentence):
    """评估内容相似度"""
    api_url = "http://localhost:3000"
    endpoint = f"{api_url}/api/evaluateContentScore"
    params = {
        "toxic_sentence": toxic_sentence,
        "neutral_sentence": neutral_sentence
    }

    result, error = make_api_request(endpoint, params)
    if result:
        return result
    else:
        print(f"{Colors.RED}内容相似度评估失败: {error}{Colors.RESET}")
        return {"content_score": 3, "reason": f"评估失败: {error}"}

def evaluate_neutral_fluency(neutral_sentence):
    """评估句子流畅性"""
    api_url = "http://localhost:3000"
    endpoint = f"{api_url}/api/evaluateNeutralFluency"
    params = {
        "neutral_sentence": neutral_sentence
    }

    result, error = make_api_request(endpoint, params)
    if result:
        return result
    else:
        print(f"{Colors.RED}流畅性评估失败: {error}{Colors.RESET}")
        return {"neutral_fluency": 0.5}

def evaluate_toxic_pairwise(toxic_sentence, neutral_sentence):
    """评估冒犯性对比"""
    api_url = "http://localhost:3000"
    endpoint = f"{api_url}/api/evaluateToxicPairwise"
    params = {
        "toxic_sentence": toxic_sentence,
        "neutral_sentence": neutral_sentence
    }

    result, error = make_api_request(endpoint, params)
    if result:
        return result
    else:
        print(f"{Colors.RED}冒犯性对比评估失败: {error}{Colors.RESET}")
        return {"toxic_pairwise_score": 3}

def process_single_row(row_data):
    """处理单行数据的评分"""
    index, toxic_sentence, neutral_sentence = row_data

    try:
        # 输入验证
        if not toxic_sentence or not neutral_sentence:
            print(f"{Colors.YELLOW}警告: 第 {index+1} 行数据包含空值{Colors.RESET}")
            return {
                'index': index,
                'content_score': 3,
                'content_reason': '输入数据为空',
                'neutral_fluency': 0.5,
                'toxic_pairwise_score': 3
            }

        # 并行评估三个指标
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # 提交三个评估任务
            content_future = executor.submit(evaluate_content_score, toxic_sentence, neutral_sentence)
            fluency_future = executor.submit(evaluate_neutral_fluency, neutral_sentence)
            pairwise_future = executor.submit(evaluate_toxic_pairwise, toxic_sentence, neutral_sentence)

            # 获取结果
            content_result = content_future.result()
            fluency_result = fluency_future.result()
            pairwise_result = pairwise_future.result()

        result = {
            'index': index,
            'content_score': content_result['content_score'],
            'content_reason': content_result['reason'],
            'neutral_fluency': fluency_result['neutral_fluency'],
            'toxic_pairwise_score': pairwise_result['toxic_pairwise_score']
        }

        print(f"{Colors.GREEN}第 {index+1} 行评分完成{Colors.RESET}")
        return result

    except Exception as e:
        print(f"{Colors.RED}处理第 {index+1} 行时发生错误: {str(e)}{Colors.RESET}")
        return {
            'index': index,
            'content_score': 3,
            'content_reason': f'处理错误: {str(e)}',
            'neutral_fluency': 0.5,
            'toxic_pairwise_score': 3
        }

def save_progress(df, file_path, results):
    """保存进度"""
    global processed_count

    with results_lock:
        # 更新DataFrame
        for result in results:
            idx = result['index']
            df.at[idx, 'content_score'] = result['content_score']
            df.at[idx, 'content_reason'] = result['content_reason']
            df.at[idx, 'neutral_fluency'] = result['neutral_fluency']
            df.at[idx, 'toxic_pairwise_score'] = result['toxic_pairwise_score']

        # 保存文件
        output_file = file_path.replace('.tsv', '_scored.tsv')
        df.to_csv(output_file, sep='\t', index=False)

        with processed_count_lock:
            processed_count += len(results)
            print(f"{Colors.CYAN}已处理 {processed_count} 条数据，结果已保存{Colors.RESET}")

def process_data_concurrent(file_path, start_idx=0, end_idx=None, max_workers=4, batch_size=10):
    """使用多线程并发处理数据集评分"""
    global all_results, processed_count

    # 读取数据
    print(f"{Colors.YELLOW}正在读取文件: {file_path}{Colors.RESET}")
    df = pd.read_csv(file_path, sep='\t')

    # 设置结束索引
    if end_idx is None or end_idx > len(df):
        end_idx = len(df)

    # 验证必要的列
    required_columns = ['toxic_sentence', 'neutral_sentence']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"缺少必要的列: {missing_columns}")

    # 创建结果列
    for col in ['content_score', 'content_reason', 'neutral_fluency', 'toxic_pairwise_score']:
        if col not in df.columns:
            df[col] = None

    # 准备数据
    total_rows = end_idx - start_idx
    print(f"{Colors.YELLOW}总共需要处理 {total_rows} 行数据{Colors.RESET}")

    # 重置计数器
    processed_count = 0
    all_results = []

    # 准备行数据
    row_data_list = []
    for i in range(start_idx, end_idx):
        row = df.iloc[i]
        row_data_list.append((i, row['toxic_sentence'], row['neutral_sentence']))

    # 使用线程池处理数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 分批处理
        batch_results = []

        with tqdm(total=total_rows, desc="评分进度") as pbar:
            # 提交所有任务
            future_to_index = {executor.submit(process_single_row, row_data): row_data[0]
                             for row_data in row_data_list}

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    result = future.result()
                    batch_results.append(result)
                    pbar.update(1)

                    # 批量保存
                    if len(batch_results) >= batch_size:
                        save_progress(df, file_path, batch_results)
                        batch_results = []

                except Exception as e:
                    index = future_to_index[future]
                    print(f"{Colors.RED}处理第 {index+1} 行时发生异常: {str(e)}{Colors.RESET}")
                    pbar.update(1)

            # 保存剩余结果
            if batch_results:
                save_progress(df, file_path, batch_results)

    # 最终保存
    output_file = file_path.replace('.tsv', '_scored.tsv')
    df.to_csv(output_file, sep='\t', index=False)
    print(f"{Colors.GREEN}评分完成！结果已保存到 {output_file}{Colors.RESET}")

    return df

def process_data(file_path, start_idx=0, end_idx=None, save_interval=10):
    """兼容性函数：使用原始的串行处理方式"""
    print(f"{Colors.YELLOW}使用串行处理模式（兼容性模式）{Colors.RESET}")

    # 读取数据
    df = pd.read_csv(file_path, sep='\t')

    # 设置结束索引
    if end_idx is None or end_idx > len(df):
        end_idx = len(df)

    # 创建结果列
    if 'content_score' not in df.columns:
        df['content_score'] = None
    if 'content_reason' not in df.columns:
        df['content_reason'] = None
    if 'neutral_fluency' not in df.columns:
        df['neutral_fluency'] = None
    if 'toxic_pairwise_score' not in df.columns:
        df['toxic_pairwise_score'] = None

    # 处理指定范围的数据
    for i in tqdm(range(start_idx, end_idx), desc="评分进度"):
        row = df.iloc[i]
        toxic_sentence = row['toxic_sentence']
        neutral_sentence = row['neutral_sentence']

        print(f"\n{Colors.CYAN}处理第 {i+1} 条数据:{Colors.RESET}")
        print(f"有毒句子: {toxic_sentence}")
        print(f"无毒句子: {neutral_sentence}")

        # 评估内容相似度
        content_result = evaluate_content_score(toxic_sentence, neutral_sentence)
        df.at[i, 'content_score'] = content_result['content_score']
        df.at[i, 'content_reason'] = content_result['reason']

        # 评估句子流畅性
        fluency_result = evaluate_neutral_fluency(neutral_sentence)
        df.at[i, 'neutral_fluency'] = fluency_result['neutral_fluency']

        # 评估冒犯性对比
        pairwise_result = evaluate_toxic_pairwise(toxic_sentence, neutral_sentence)
        df.at[i, 'toxic_pairwise_score'] = pairwise_result['toxic_pairwise_score']

        # 每处理一定数量的数据保存一次
        if (i + 1) % save_interval == 0 or i == end_idx - 1:
            output_file = file_path.replace('.tsv', '_scored.tsv')
            df.to_csv(output_file, sep='\t', index=False)
            print(f"{Colors.GREEN}已保存结果到 {output_file}{Colors.RESET}")

        # 添加短暂延迟，避免API请求过于频繁
        time.sleep(0.5)  # 减少延迟时间

    # 最终保存
    output_file = file_path.replace('.tsv', '_scored.tsv')
    df.to_csv(output_file, sep='\t', index=False)
    print(f"{Colors.GREEN}评分完成！结果已保存到 {output_file}{Colors.RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="评估句子对的相似度、流畅性和冒犯性")
    parser.add_argument("--file", type=str, required=True, help="TSV文件路径")
    parser.add_argument("--start", type=int, default=0, help="起始索引")
    parser.add_argument("--end", type=int, default=None, help="结束索引")
    parser.add_argument("--save_interval", type=int, default=10, help="保存间隔（仅串行模式）")
    parser.add_argument("--max_workers", type=int, default=10, help="最大并发线程数")
    parser.add_argument("--batch_size", type=int, default=10, help="批量保存大小")
    parser.add_argument("--concurrent", action="store_true", help="使用并发处理模式（推荐）")
    parser.add_argument("--serial", action="store_true", help="使用串行处理模式（兼容性）")

    args = parser.parse_args()

    # 记录开始时间
    start_time = time.time()

    try:
        if args.concurrent or (not args.serial and not args.concurrent):
            # 默认使用并发模式
            print(f"{Colors.CYAN}使用并发处理模式，线程数: {args.max_workers}{Colors.RESET}")
            process_data_concurrent(
                args.file,
                args.start,
                args.end,
                args.max_workers,
                args.batch_size
            )
        else:
            # 使用串行模式
            process_data(args.file, args.start, args.end, args.save_interval)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}用户中断处理{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}处理过程中发生错误: {str(e)}{Colors.RESET}")
    finally:
        # 计算总时间
        end_time = time.time()
        total_time = end_time - start_time
        print(f"{Colors.BLUE}总处理时间: {total_time:.2f} 秒{Colors.RESET}")
