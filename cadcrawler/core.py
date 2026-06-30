"""
核心爬虫引擎
"""

import os
import sys
import random
from typing import List

from .config import CrawlerConfig
from .storage import StorageManager
from .downloader import Downloader
from .parsers import get_parser
from .progress import ProgressDisplay


class CrawlerEngine:
    """爬虫引擎"""

    def __init__(self, config: CrawlerConfig, data_dir: str = None):
        self.config = config

        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

        self.storage = StorageManager(data_dir, config.name)
        self.downloader = Downloader(config, self.storage)
        self.progress = None

    def run(self, resume: bool = True):
        """运行爬虫"""
        print("=" * 70)
        print(f"CAD文件爬虫 - {self.config.name}")
        print("=" * 70)
        print(f"  数据源: {', '.join(self.config.sources)}")
        print(f"  请求延迟: {self.config.request_delay}s")
        print(f"  文件验证: {'启用' if self.config.verify_files else '禁用'}")
        print(f"  文件去重: {'启用' if self.config.deduplicate else '禁用'}")
        print("=" * 70)

        # 生成搜索词
        all_queries = self.config.generate_search_queries()

        # 获取待处理的搜索词
        if resume:
            queries = self.storage.get_pending_queries(all_queries)
            if len(queries) < len(all_queries):
                print(f"\n恢复进度: 剩余 {len(queries)}/{len(all_queries)} 个搜索词\n")
        else:
            queries = all_queries

        if not queries:
            print("没有待处理的搜索词，已全部完成！")
            return

        # 随机打乱，避免每次顺序相同
        random.shuffle(queries)

        # 初始化进度
        self.progress = ProgressDisplay(len(queries))
        self.storage.start_session()

        # 开始搜索
        try:
            for source_name in self.config.sources:
                parser_cls = get_parser(source_name)
                parser = parser_cls(self.config, self.storage)

                for query in queries:
                    self.progress.start_query(query, source_name)

                    # 搜索
                    try:
                        file_links = parser.search(query)

                        if file_links:
                            # 下载文件
                            for link in file_links:
                                record = self.downloader.download(link, source_name)
                                if record:
                                    self.progress.update_file(record.filename, f"当前延迟: {self.downloader.get_current_delay():.1f}s")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                            pass

                    # 标记完成
                    self.storage.mark_query_completed(query)
                    self.progress.finish_query(self.downloader.stats)

        except KeyboardInterrupt:
            print("\n\n用户中断，进度已保存。")

        # 显示总结
        self.progress.summary(self.downloader.stats)

        # 显示下载位置
        print(f"\n下载目录: {self.storage.downloads_dir}")
        print(f"状态文件: {self.storage.state_file}")

    def print_status(self):
        """打印当前状态"""
        stats = self.storage.get_stats()
        print("=" * 70)
        print(f"配置: {self.config.name}")
        print("=" * 70)
        print(f"  已完成搜索词: {stats.get('queries_completed', 0)}")
        print(f"  已处理URL: {stats.get('urls_processed', 0)}")
        print(f"  已下载文件: {stats.get('files_downloaded', 0)}")
        print("=" * 70)
        print(f"\n下载目录: {self.storage.downloads_dir}")
        if self.storage.state.files:
            print("\n最近下载的文件:")
            for f in self.storage.state.files[-5:]:
                print(f"  - {f.filename}")
