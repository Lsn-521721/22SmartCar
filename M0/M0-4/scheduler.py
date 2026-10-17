#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskScheduler —— 命令行任务调度模拟器
按依赖顺序（拓扑排序）执行任务，支持失败重试、SKIPPED 传播、超时控制，
运行结束生成 report.json。
"""
import argparse
import json         #Python字典列表相互转换
import os
import random
import sys
import time

try:
    import yaml
except ImportError:
    print("错误：缺少 PyYAML，请先激活虚拟环境并安装依赖（pip install pyyaml）")
    sys.exit(1)


def _supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_COLORS = {
    "SUCCESS": "\033[32m",
    "FAILED": "\033[31m",
    "RETRY": "\033[33m",
    "SKIPPED": "\033[34m",
    "TIMEOUT": "\033[35m",
    "RESET": "\033[0m",
}


def colorize(text, status):
    """非 TTY 环境（重定向到文件）自动降级为无色。"""
    if not _supports_color():
        return text
    return _COLORS.get(status, "") + text + _COLORS["RESET"]


def load_tasks(config_path):
    """读取 yaml/json 配置，返回 (timeout, tasks)。异常给出可读报错并不抛 Traceback。"""
    if not os.path.exists(config_path):
        print("错误：配置文件不存在：%s" % config_path)
        sys.exit(1)
    try:
        if config_path.endswith((".yaml", ".yml")):
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        else:
            with open(config_path, "r") as f:
                data = json.load(f)
    except Exception as e:
        print("错误：配置文件解析失败：%s" % e)
        sys.exit(1)
    if not isinstance(data, dict) or "tasks" not in data:
        print("错误：配置缺少 tasks 字段")
        sys.exit(1)
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list) or len(tasks) == 0:
        print("错误：任务列表为空")
        sys.exit(1)
    names = set()
    for t in tasks:
        name = t.get("name")
        if not name:
            print("错误：任务缺少 name 字段")
            sys.exit(1)
        if name in names:
            print("错误：任务名重复：%s" % name)
            sys.exit(1)
        names.add(name)
        sr = t.get("success_rate", 1.0)
        if not (0.0 <= sr <= 1.0):
            print("错误：任务 %s 的 success_rate 越界（应为 0~1）" % name)
            sys.exit(1)
        if t.get("duration", 0) < 0:
            print("错误：任务 %s 的 duration 为负数" % name)
            sys.exit(1)
    timeout = data.get("timeout")
    return timeout, tasks


def topo_sort(tasks):
    """Kahn 拓扑排序；检测依赖不存在与依赖环。返回执行顺序（任务名列表）。"""
    deps_map = {t["name"]: list(t.get("dependencies", [])) for t in tasks}
    names = set(deps_map.keys())
    for name, deps in deps_map.items():
        for d in deps:
            if d not in names:
                print("错误：任务 %s 依赖不存在的任务 %s" % (name, d))
                sys.exit(1)
    in_degree = {name: len(deps) for name, deps in deps_map.items()}
    children = {name: [] for name in deps_map}
    for name, deps in deps_map.items():
        for d in deps:
            children[d].append(name)
    queue = [n for n, deg in in_degree.items() if deg == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for c in children[n]:
            in_degree[c] -= 1
            if in_degree[c] == 0:
                queue.append(c)
    if len(order) != len(deps_map):
        print("错误：检测到依赖环")
        sys.exit(1)
    return order


def run_scheduler(tasks, timeout, seed, report_path):
    random.seed(seed)
    start = time.time()
    tasks_map = {t["name"]: t for t in tasks}
    deps_map = {t["name"]: list(t.get("dependencies", [])) for t in tasks}
    order = topo_sort(tasks)

    status = {}
    attempts = {}
    durations = {}
    started_at = {}
    ended_at = {}
    timed_out = False

    for name in order:
        # 执行前超时检查
        if timeout is not None and time.time() - start >= timeout:
            timed_out = True
            break
        t = tasks_map[name]
        # 依赖传播：任一前置为 FAILED / SKIPPED，本任务 SKIPPED
        if any(status.get(d) in ("FAILED", "SKIPPED") for d in deps_map[name]):
            status[name] = "SKIPPED"
            attempts[name] = 0
            durations[name] = 0.0
            started_at[name] = time.time()
            ended_at[name] = time.time()
            print(colorize("SKIPPED  %s" % name, "SKIPPED"))
            continue
        # 执行任务（最多 3 次尝试）
        for attempt in range(1, 4):
            st = time.time()
            time.sleep(t.get("duration", 0.0))
            et = time.time()
            # 每个任务 sleep 后做一次超时检查
            if timeout is not None and time.time() - start >= timeout:
                timed_out = True
                started_at[name] = st
                ended_at[name] = et
                break
            if random.random() < t.get("success_rate", 1.0):
                status[name] = "SUCCESS"
                attempts[name] = attempt
                durations[name] = et - st
                started_at[name] = st
                ended_at[name] = et
                print(colorize("SUCCESS  %s (第 %d 次尝试)" % (name, attempt), "SUCCESS"))
                break
            if attempt < 3:
                print(colorize("RETRY    %s (第 %d 次失败，准备重试)" % (name, attempt), "RETRY"))
            else:
                status[name] = "FAILED"
                attempts[name] = attempt
                durations[name] = et - st
                started_at[name] = st
                ended_at[name] = et
                print(colorize("FAILED   %s (3 次尝试均失败)" % name, "FAILED"))
        if timed_out:
            break

    if timed_out:
        # 标记剩余未执行任务为 TIMEOUT（report 必须包含全部任务）
        for name in order:
            if name not in status:
                status[name] = "TIMEOUT"
                attempts[name] = 0
                durations[name] = 0.0
                started_at[name] = time.time()
                ended_at[name] = time.time()
                print(colorize("TIMEOUT  %s" % name, "TIMEOUT"))

    total_duration = time.time() - start
    report = {
        "timeout": timed_out,
        "total_duration": round(total_duration, 2),
        "tasks": [
            {
                "name": name,
                "status": status[name],
                "attempts": attempts[name],
                "duration": round(durations[name], 2),
                "started_at": round(started_at[name], 2),
                "ended_at": round(ended_at[name], 2),
            }
            for name in order
        ],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("总耗时 %.2f 秒" % total_duration)
    print("结果：%s" % ("TIMEOUT" if timed_out else "完成"))


def main():
    parser = argparse.ArgumentParser(description="任务调度模拟器 TaskScheduler")
    parser.add_argument("--config", required=True, help="任务配置文件（yaml/yml/json）")
    parser.add_argument("--timeout", type=float, default=None, help="覆盖配置中的 timeout（秒）")
    parser.add_argument("--report", default="report.json", help="报告输出路径（默认 report.json）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（便于复现）")
    args = parser.parse_args()

    timeout, tasks = load_tasks(args.config)
    if args.timeout is not None:
        timeout = args.timeout
    run_scheduler(tasks, timeout, args.seed, args.report)


if __name__ == "__main__":
    main()
