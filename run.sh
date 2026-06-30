#!/bin/bash
# 运行脚本

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，先运行 ./setup.sh"
    exit 1
fi

source venv/bin/activate
python3 main.py "$@"
