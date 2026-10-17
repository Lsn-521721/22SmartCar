# M0-1 开发环境搭建记录

## 环境信息
- 操作系统：Ubuntu 22.04.5 LTS（物理机双系统）
- 内核：6.8.0-40-generic x86_64
- 主机：lsn07125-Legion-R9000P-ADR10

## 安装清单
- ROS2 Humble（/opt/ros/humble，已写入 ~/.bashrc）
- Python 3.10.12 + pip
- uv 0.13.1（虚拟环境管理）
- build-essential / git / cmake / make / gcc / g++
- VS Code 1.142.0
- Git + SSH 公钥（已配置 GitHub）

## 验收结果
- check_env.sh：PASS=22 FAIL=0 WARN=3（最终通过）
- 修复项：pip 不可用（apt 安装）、脚本需在仓库目录内运行

## 遗留 WARN（现场注意）
- known_hosts 为空：现场需实际 ssh 登录开发板/服务器一次
- VS Code 插件 headless 无法列出（桌面环境正常）

## AI 使用披露
环境搭建与排错过程中部分使用AI辅助
