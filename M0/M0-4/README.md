# M0-4 TaskScheduler 任务调度模拟器

## 简介
按依赖顺序（拓扑排序）执行任务的命令行模拟器，支持失败重试、跳过传播、超时控制，输出彩色日志与 report.json。

## 参数说明

| 参数 | 必填 | 说明 |
| :-- | :--: | :-- |
| `--config <path>` | 是 | 任务配置文件（.yaml / .yml / .json） |
| `--timeout <float>` | 否 | 覆盖配置文件中的 timeout（秒） |
| `--report <path>` | 否 | 报告输出路径，默认 report.json |
| `--seed <int>` | 否 | 随机种子，便于复现同一结果 |

## 运行示例

示例 1：默认运行，seed 固定复现
```bash
python3 scheduler.py --config tasks_demo.yaml --report report.json --seed 42
示例 2：强制 3 秒超时
python3 scheduler.py --config tasks_demo.yaml --timeout 3 --report report_timeout.json --seed 42
示例 3：不设种子，随机运行
python3 scheduler.py --config tasks_demo.yaml
## 调度规则

- 按依赖拓扑排序执行，正确支持分叉 / 汇合
- 任务失败最多重试 2 次（共 3 次尝试），仍失败标记 FAILED 并跳过
- 任一前置为 FAILED / SKIPPED 的任务标记为 SKIPPED
- 超过 timeout 立即终止，剩余未执行任务标记为 TIMEOUT
