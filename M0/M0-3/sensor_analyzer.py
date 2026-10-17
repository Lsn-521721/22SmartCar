#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensor_analyzer.py  —— 上一届学长留下的"能用"的脚本

注释（学长原话）：
    "处理一下传感器数据就能用"

原本意图：
    1. 读取 sensor_data.csv（列：time, value）
    2. 计算 value 的平均值、标准差
    3. 剔除离群值（|value - mean| > 2 * std）
    4. 把清洗后的数据保存为 cleaned_data.csv
    5. 打印一份统计摘要

现状：跑不通 / 跑出来数不对。就交给你了。
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensor_analyzer.py —— 修复版
原脚本存在 8 处缺陷（详见 README.md 问题报告），已全部修复并补充 CLI 与异常处理。
"""
import csv
import math
import os        #内置标准库：和操作系统交互
import sys
import argparse


def read_data(input_path):
    """读取 CSV，返回 (times, values)。异常输入给出可读报错 Traceback。"""
    if not os.path.exists(input_path):
        print("错误：输入文件不存在：%s" % input_path)
        sys.exit(1)
    try:
        with open(input_path, "r") as f:
            reader = csv.DictReader(f)
            times = []
            values = []
            for row in reader:
                t = float(row["time"])
                v = float(row["value"])
                times.append(t)
                values.append(v)
    except KeyError as e:
        print("错误：CSV 缺少列 %s（需要 time 和 value）" % e)
        sys.exit(1)
    except ValueError as e:
        print("错误：数据含非数值内容：%s" % e)
        sys.exit(1)
    except Exception as e:
        print("错误：读取文件失败：%s" % e)
        sys.exit(1)
    if len(values) == 0:
        print("错误：数据为空")
        sys.exit(1)
    return times, values


def calc_mean(values):
    return sum(values) / len(values)


def calc_std(values, mean):
    n = len(values)
    acc = sum((v - mean) ** 2 for v in values)
    return math.sqrt(acc / n)


def remove_outliers(times, values, mean, std):
    """剔除 |value - mean| > 2*std 的离群值（双侧判定）。"""
    clean_times = []
    clean_values = []
    for t, v in zip(times, values):
        if abs(v - mean) <= 2 * std:
            clean_times.append(t)
            clean_values.append(v)
    return clean_times, clean_values


def main():
    parser = argparse.ArgumentParser(description="传感器数据分析与离群值清洗")
    parser.add_argument("--input", default="sensor_data.csv",
                        help="输入 CSV 路径（默认 sensor_data.csv）")
    parser.add_argument("--output", default="cleaned_data.csv",
                        help="输出 CSV 路径（默认 cleaned_data.csv）")
    args = parser.parse_args()

    times, values = read_data(args.input)
    mean = calc_mean(values)
    std = calc_std(values, mean)
    clean_times, clean_values = remove_outliers(times, values, mean, std)

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "value"])
        for t, v in zip(clean_times, clean_values):
            writer.writerow([t, v])

    print("=== 传感器数据分析 ===")
    print("共读取 %d 条数据" % len(values))
    print("均值 mean = %.4f" % mean)
    print("标准差 std = %.4f" % std)
    print("清洗后剩余 %d 条" % len(clean_values))
    print("已保存到 %s" % args.output)


if __name__ == "__main__":
    main()
