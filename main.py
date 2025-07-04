import threading
from model_detoxify import localDetoxify, remoteNormalDetoxify, remoteReasoningDetoxify
import pandas as pd
import concurrent.futures
import time
from tqdm import tqdm


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
all_local_results = []
all_results_length = 0
all_process_length = 0
process_length_lock = threading.Lock() # 新增锁


def process_local():
    batch_size = 4500
    first_half = all_local_results[:batch_size]  # 前4500条数据
    second_half = all_local_results[batch_size:]  # 后4500条数据

    # 计算两部分中较长的长度，确保所有数据都被处理
    max_length = max(len(first_half), len(second_half))
    total_processed = 0

    # 使用tqdm显示总体进度
    with tqdm(total=len(first_half) + len(second_half), desc="处理本地") as pbar:
        for i in range(max_length):
            try:
                # 处理第一部分的数据（如果还有）
                if i < len(first_half):
                    item = first_half[i]
                    index = item["index"]
                    text = item["toxic_sentence"]
                    lang = item["lang"]
                    local_result = localDetoxify(text, lang)
                    all_local_results[index]["local_result"] = local_result
                    print(
                        f"{Colors.GREEN}本地处理完成，index: {index}（前半部分）{Colors.RESET}"
                    )
                    total_processed += 1
                    pbar.update(1)

                # 处理第二部分的数据（如果还有）
                if i < len(second_half):
                    item = second_half[i]
                    index = item["index"]
                    text = item["toxic_sentence"]
                    lang = item["lang"]
                    local_result = localDetoxify(text, lang)
                    all_local_results[index]["local_result"] = local_result
                    print(
                        f"{Colors.GREEN}本地处理完成，index: {index}（后半部分）{Colors.RESET}"
                    )
                    total_processed += 1
                    pbar.update(1)
            except Exception as e:
                print(
                    f"{Colors.RED}处理数据时发生错误，index: {index}, 错误: {str(e)}{Colors.RESET}"
                )
                # 出错时，将原始文本作为结果
                all_local_results[index]["local_result"] = text
                total_processed += 1
                pbar.update(1)

    print(f"{Colors.BLUE}本地处理完成，共处理 {total_processed} 条数据{Colors.RESET}")


def process_remote_normal_part1():
    """处理远程普通解毒任务 - 第一部分 (1-4500行)"""
    for item in tqdm(all_local_results[:4500], desc="远程普通处理(1-4500)"):
        try:
            index = item["index"]
            text = item["toxic_sentence"]
            lang = item["lang"]
            remote_result = remoteNormalDetoxify(text, lang)
            all_local_results[index]["remote_normal_result"] = remote_result
            print(
                f"{Colors.CYAN}远程普通处理完成(1-4500)，index: {index}{Colors.RESET}"
            )
        except Exception as e:
            print(
                f"{Colors.RED}远程普通处理出错(1-4500)，index: {index}, 错误: {str(e)}{Colors.RESET}"
            )
            all_local_results[index][
                "remote_normal_result"
            ] = text  # 使用原始文本作为结果
    print(f"{Colors.BLUE}远程普通处理(1-4500)完成{Colors.RESET}")


def process_remote_normal_part2():
    """处理远程普通解毒任务 - 第二部分 (4500行到最后)"""
    for item in tqdm(all_local_results[4500:], desc="远程普通处理(4500+)"):
        try:
            index = item["index"]
            text = item["toxic_sentence"]
            lang = item["lang"]
            remote_result = remoteNormalDetoxify(text, lang)
            all_local_results[index]["remote_normal_result"] = remote_result
            print(f"{Colors.CYAN}远程普通处理完成(4500+)，index: {index}{Colors.RESET}")
        except Exception as e:
            print(
                f"{Colors.RED}远程普通处理出错(4500+)，index: {index}, 错误: {str(e)}{Colors.RESET}"
            )
            all_local_results[index][
                "remote_normal_result"
            ] = text  # 使用原始文本作为结果
    print(f"{Colors.BLUE}远程普通处理(4500+)完成{Colors.RESET}")


def process_remote_reasoning_part1():
    global all_process_length
    with tqdm(total=4500, desc="深度思考处理(1-4500)") as pbar:
        index = 0
        while index < 4500:
            if (
                all_local_results[index]["local_result"] != ""
                and all_local_results[index]["remote_normal_result"] != ""
            ):
                try:
                    remote_reasoning_result = remoteReasoningDetoxify(
                        all_local_results[index]["toxic_sentence"],
                        all_local_results[index]["lang"],
                        all_local_results[index]["local_result"],
                        all_local_results[index]["remote_normal_result"],
                    )
                    all_local_results[index][
                        "remote_reasoning_result"
                    ] = remote_reasoning_result
                    print(
                        f"{Colors.PURPLE}深度思考处理完成(1-4500)，index: {index}{Colors.RESET}"
                    )
                except Exception as e:
                    print(
                        f"{Colors.RED}深度思考处理出错(1-4500)，index: {index}, 错误: {str(e)}{Colors.RESET}"
                    )
                    all_local_results[index]["remote_reasoning_result"] = (
                        all_local_results[index]["remote_normal_result"]
                    )
                finally:
                    index += 1
                    with process_length_lock:
                        all_process_length += 1
                    pbar.update(1)
            else:
                time.sleep(3)


def process_remote_reasoning_part2():
    global all_process_length
    with tqdm(
        total=all_results_length - 4500,
        desc="深度思考处理(4500+)",
        initial=all_process_length,
    ) as pbar:
        index = 4500
        while index < all_results_length:
            if (
                all_local_results[index]["local_result"] != ""
                and all_local_results[index]["remote_normal_result"] != ""
            ):
                try:
                    remote_reasoning_result = remoteReasoningDetoxify(
                        all_local_results[index]["toxic_sentence"],
                        all_local_results[index]["lang"],
                        all_local_results[index]["local_result"],
                        all_local_results[index]["remote_normal_result"],
                    )
                    all_local_results[index][
                        "remote_reasoning_result"
                    ] = remote_reasoning_result
                    print(
                        f"{Colors.PURPLE}深度思考处理完成(4500+)，index: {index}{Colors.RESET}"
                    )
                except Exception as e:
                    print(
                        f"{Colors.RED}深度思考处理出错(4500+)，index: {index}, 错误: {str(e)}{Colors.RESET}"
                    )
                    all_local_results[index]["remote_reasoning_result"] = (
                        all_local_results[index]["remote_normal_result"]
                    )
                finally:
                    index += 1
                    with process_length_lock:
                        all_process_length += 1
                    pbar.update(1)
            else:
                time.sleep(3)


def save_file():
    global all_process_length
    global all_local_results
    global all_results_length
    while all_process_length < all_results_length:
        time.sleep(1800)  # 每30分钟检测一次
        # 创建临时结果列表
        temp_results = []
        for item in all_local_results:
            neutral_sentence = (
                item["remote_reasoning_result"]
            )
            temp_results.append(
                {
                    "toxic_sentence": item["toxic_sentence"],
                    "neutral_sentence": neutral_sentence,
                    "lang": item["lang"],
                }
            )

        # 创建临时DataFrame并保存
        temp_df = pd.DataFrame(temp_results)
        temp_output_file = f"temp_results_{len(all_local_results)}.tsv"
        temp_df.to_csv(temp_output_file, sep="\t", index=False)
        print(f"{Colors.YELLOW}临时结果已保存到: {temp_output_file}{Colors.RESET}")
        # 保存全部数据
        all_data_df = pd.DataFrame(all_local_results)
        all_data_output_file = f"temp_all_results_{len(all_local_results)}.tsv"
        all_data_df.to_csv(all_data_output_file, sep="\t", index=False)
        print(f"{Colors.YELLOW}全部数据已保存到: {all_data_output_file}{Colors.RESET}")

    print(f"{Colors.GREEN}所有处理已完成，退出保存临时文件循环{Colors.RESET}")


def process(df):
    """
    处理数据函数

    初始化数据并启动处理线程：本地处理、远程普通处理和深度思考处理
    在处理一部分数据后就开始深度思考处理
    返回线程池和各个任务的Future对象，以便在主函数中管理其生命周期
    """
    # 初始化全局结果列表
    global all_local_results
    global all_results_length
    all_local_results = []

    # 预先初始化all_local_results列表，确保有足够的元素
    total_rows = len(df)
    all_results_length = total_rows
    for i in range(total_rows):
        all_local_results.append(
            {
                "index": i,
                "toxic_sentence": df.iloc[i]["toxic_sentence"],
                "lang": df.iloc[i]["lang"],
                "local_result": "",
                "remote_normal_result": "",
                "remote_reasoning_result": "",
            }
        )

    # 创建线程池
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)

    # 提交本地处理任务
    local_future = executor.submit(process_local)
    # 提交远程普通处理任务
    remote1_feature = executor.submit(process_remote_normal_part1)
    remote2_feature = executor.submit(process_remote_normal_part2)
    reasoning1_feature = executor.submit(process_remote_reasoning_part1)
    reasoning2_feature = executor.submit(process_remote_reasoning_part2)
    save_feature = executor.submit(save_file)
    all_features = [
        local_future,
        remote1_feature,
        remote2_feature,
        reasoning1_feature,
        reasoning2_feature,
        save_feature,
    ]
    return all_features


def main():
    """主函数，处理TSV文件并保存结果"""
    # 输入和输出文件路径
    input_file = "test_inputs_upd.tsv"  # 相对于NewPickMethod目录的路径
    output_file = "detoxified_new_output_results1.tsv"
    output_all_data_file = "detoxified_new_output_results1_all.tsv"
    global all_local_results

    # 读取TSV文件
    print(f"{Colors.YELLOW}正在读取文件: {input_file}{Colors.RESET}")
    df = pd.read_csv(input_file, sep="\t")
    total_rows = len(df)
    print(f"{Colors.YELLOW}总共需要处理 {total_rows} 行数据{Colors.RESET}")

    try:
        # 调用process函数处理数据，获取线程池和Future对象
        all_features = process(df)

        concurrent.futures.wait(all_features)
        print(f"{Colors.GREEN}所有处理已完成{Colors.RESET}")

        # 创建最终结果列表
        all_results = []
        for item in all_local_results:
            # 如果深度思考结果为空，使用其他可用结果
            neutral_sentence = item["remote_reasoning_result"]
            if neutral_sentence == "":
                if item["remote_normal_result"] != "":
                    neutral_sentence = item["remote_normal_result"]
                elif item["local_result"] != "":
                    neutral_sentence = item["local_result"]
                else:
                    neutral_sentence = item[
                        "toxic_sentence"
                    ]  # 如果没有任何结果，使用原始文本

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

        # 保存所有数据到TSV文件
        all_data_df = pd.DataFrame(all_local_results)
        all_data_df.to_csv(output_all_data_file, sep="\t", index=False)
        print(f"{Colors.GREEN}所有数据已保存到: {output_all_data_file}{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.RED}处理过程中发生错误: {str(e)}{Colors.RESET}")


if __name__ == "__main__":
    # 启动时间
    start_time = time.time()

    main()

    # 结束时间
    end_time = time.time()
    print(f"{Colors.BLUE}总处理时间: {end_time - start_time:.2f} 秒{Colors.RESET}")
