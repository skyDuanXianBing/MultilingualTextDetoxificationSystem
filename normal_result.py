import threading
import pandas as pd
import time
from tqdm import tqdm
from model_detoxify import  remoteNormalDetoxify


# ANSI颜色代码
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"


def process_range(start_idx, end_idx, all_data):
    """处理指定范围内的远程普通解毒任务"""
    with tqdm(
        total=end_idx - start_idx, desc=f"远程普通处理({start_idx}-{end_idx})"
    ) as pbar:
        for i in range(start_idx, end_idx):
            try:
                item = all_data[i]
                remote_normal_result = remoteNormalDetoxify(
                    item["toxic_sentence"], item["lang"]
                )
                all_data[i]["remote_normal_result"] = remote_normal_result
                print(f"{Colors.CYAN}远程普通处理完成，index: {i}{Colors.RESET}")
            except Exception as e:
                print(
                    f"{Colors.RED}远程普通处理出错，index: {i}, 错误: {str(e)}{Colors.RESET}"
                )
                # 出错时，使用原始文本作为结果
                all_data[i]["remote_normal_result"] = item["toxic_sentence"]
            finally:
                pbar.update(1)

def main():
    # 启动时间
    start_time = time.time()

    # 输入和输出文件路径
    input_file = "test_inputs_upd.tsv"
    output_file = "ailiyun_new_prompt_normal_results.tsv"

    # 读取TSV文件
    print(f"{Colors.YELLOW}正在读取文件: {input_file}{Colors.RESET}")
    all_data = pd.read_csv(input_file, sep="\t").to_dict("records")

    # 设置处理范围
    total_records = len(all_data)

    # 创建12个线程，分别处理数据
    thread_count = 20
    chunk_size = total_records // thread_count
    threads = []

    for i in range(thread_count):
        thread_start = i * chunk_size
        thread_end = (
            thread_start + chunk_size if i < thread_count - 1 else total_records
        )
        thread = threading.Thread(
            target=process_range, args=(thread_start, thread_end, all_data)
        )
        threads.append(thread)

    # 启动线程
    print(f"{Colors.GREEN}启动处理线程...{Colors.RESET}")
    for thread in threads:
        thread.start()

    # 等待线程完成
    for thread in threads:
        thread.join()

    # 创建最终结果列表
    all_results = []
    for item in all_data:
        neutral_sentence = item["remote_normal_result"]
        if neutral_sentence == "":
            neutral_sentence = item["toxic_sentence"]  # 如果没有结果，使用原始文本

        all_results.append(
            {
                "toxic_sentence": item["toxic_sentence"],
                "neutral_sentence": neutral_sentence,
                "lang": item["lang"],
            }
        )

    # 创建最终结果DataFrame
    result_df = pd.DataFrame(all_results)

    # 保存结果到TSV文件
    result_df.to_csv(output_file, sep="\t", index=False)
    print(f"{Colors.GREEN}最终结果已保存到: {output_file}{Colors.RESET}")
    # 结束时间
    end_time = time.time()
    print(f"{Colors.BLUE}总处理时间: {end_time - start_time:.2f} 秒{Colors.RESET}")


if __name__ == "__main__":
    main()
