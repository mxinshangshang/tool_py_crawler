#!/bin/bash
# 设置脚本

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "设置完成！"
echo ""
echo "使用方法："
echo "  ./run.sh --list"
echo "  ./run.sh --config raspberry-pi5"
