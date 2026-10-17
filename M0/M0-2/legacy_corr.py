import yaml
import csv
import math
import argparse
import sys

def load_config(path):
    # 把"读 yaml"的代码放这里
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg

def read_data(csv_path, col_x, col_y):
    # 把"读 csv 两列"的代码放这里，返回 (xs, ys)
    xs = []
    ys = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row[col_x]))
            ys.append(float(row[col_y]))
    return xs, ys

def calc_corr(xs, ys):
    # 把"算 n / mean_x / mean_y / r"的代码放这里
    n = len(xs)
    sum_x = 0.0
    sum_y = 0.0
    for i in range(n):
        sum_x = sum_x + xs[i]
        sum_y = sum_y + ys[i]
    mean_x = sum_x / n
    mean_y = sum_y / n
    dx = 0.0
    dy = 0.0
    prod = 0.0
    for i in range(n):
        a = xs[i] - mean_x
        b = ys[i] - mean_y
        dx = dx + a * a
        dy = dy + b * b
        prod = prod + a * b
    r = prod / math.sqrt(dx * dy)
    return n, mean_x, mean_y, r

def main(config_path):
    cfg = load_config(config_path)
    xs, ys = read_data(cfg["input_csv"], cfg["columns"]["x"], cfg["columns"]["y"])
    n, mean_x, mean_y, r = calc_corr(xs, ys)
    print("n =", n)
    print("mean_x =", mean_x)
    print("mean_y =", mean_y)
    print("r =", r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    main(args.config)