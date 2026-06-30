#!/usr/bin/env python3
"""
CAD文件爬虫 - 主入口
"""

import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cadcrawler.cli import main

if __name__ == "__main__":
    main()
