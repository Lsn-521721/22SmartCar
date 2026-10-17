# M0-3 代码排查报告

## 修复的 8 处缺陷

| # | 位置 | 现象 | 原因 | 修复方式 |
| --- | --- | --- | --- | --- |
| 1 | `row["Value"]`（读取数据处） | 运行报 `KeyError: 'Value'` | CSV 表头是小写 `value`，原代码写成了大写 `Value` | 改为 `row["value"]` |
| 2 | `acc += (v - mean)`（标准差累加） | 标准差计算结果异常 | 方差公式漏了平方 | 改为 `acc += (v - mean) ** 2` |
| 3 | `std = acc / len(data)` | 标准差不是标准差的量级 | 缺开根号 | 改为 `std = math.sqrt(acc / n)` |
| 4 | `if v > mean + 2 * std` | 只剔除了偏大的离群值 | 判定只写了单侧 | 改为 `abs(v - mean) > 2 * std`（双侧） |
| 5 | `for v in data: data.remove(v)` | 剔除不干净、元素被跳过 | 边遍历边删除，修改了正在迭代的列表 | 改用新列表收集清洗结果 |
| 6 | `os.path.join("/", "out", OUTPUT_FILE)` | 输出路径写死为绝对路径 `/out/` | 输出目录写死 | 输出到当前工作目录（--output） |
| 7 | `for v in cleaned` 写入 | 输出文件只有表头、没有数据 | `cleaned` 列表从未被填充 | 用清洗后的数据写 `time,value` 两列 |
| 8 | 无任何异常处理 | 文件不存在/空文件/缺列/非数值直接抛 Traceback | 无判空与异常处理 | 增加文件检查与 try/except，可读报错并以非 0 退出 |

## 验证结果

- 正常运行：`python3 sensor_analyzer.py --input sensor_data.csv --output cleaned_data.csv`，退出码 0
- 异常输入（文件不存在）：可读报错，无 Traceback，退出码 1

## 运行方式

```bash
# 方式一：显式指定输入输出
python3 sensor_analyzer.py --input sensor_data.csv --output cleaned_data.csv
# 方式二：无参数，默认当前目录读写
python3 sensor_analyzer.py
