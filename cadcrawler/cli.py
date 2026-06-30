"""
命令行接口
"""

import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="通用CAD文件爬虫 - 可配置、资源友好",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有可用配置
  python main.py --list

  # 使用树莓派5配置运行
  python main.py --config raspberry-pi5

  # 使用自定义配置文件
  python main.py --config ./my-config.yaml

  # 查看当前状态
  python main.py --config raspberry-pi5 --status

  # 从头开始（不恢复）
  python main.py --config raspberry-pi5 --no-resume
        """
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用配置"
    )

    parser.add_argument(
        "--config", "-c",
        help="使用的配置名称或路径"
    )

    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="查看当前配置的状态"
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="从头开始，不恢复进度"
    )

    parser.add_argument(
        "--create-config",
        help="创建一个示例配置文件"
    )

    args = parser.parse_args()

    # 导入在这里避免循环依赖
    from .config import ConfigManager, CrawlerConfig
    from .core import CrawlerEngine

    configs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
    manager = ConfigManager(configs_dir)

    # 列出配置
    if args.list:
        configs = manager.list_configs()
        print("可用配置:")
        for cfg in configs:
            print(f"  - {cfg}")
        if not configs:
            print("  (暂无配置文件)")
        return

    # 创建示例配置
    if args.create_config:
        example_config = CrawlerConfig(
            name=args.create_config,
            base_keywords=["my-project"],
            product_types=["case", "enclosure"],
            file_types=["dxf", "stl"],
            materials=["acrylic"],
            processes=["laser cut"],
        )
        manager.save_config(example_config)
        print(f"配置已创建: {args.create_config}.yaml")
        return

    # 必须指定配置
    if not args.config:
        parser.print_help()
        print("\n错误: 请指定 --config 参数")
        return

    # 加载配置
    try:
        config = manager.load_config(args.config)
    except ValueError as e:
        print(f"错误: {e}")
        print(f"\n使用 --list 查看可用配置")
        return

    # 查看状态
    if args.status:
        engine = CrawlerEngine(config)
        engine.print_status()
        return

    # 运行爬虫
    engine = CrawlerEngine(config)
    engine.run(resume=not args.no_resume)
