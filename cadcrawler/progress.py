"""
进度显示
"""

import sys
import time
from typing import Dict


class ProgressDisplay:
    """进度显示"""

    def __init__(self, total_queries: int):
        self.total_queries = total_queries
        self.start_time = time.time()
        self.current_query = 0
        self.last_update = 0

    def start_query(self, query: str, source: str):
        """开始新搜索"""
        self.current_query += 1
        self.last_update = time.time()
        print(f"\r[{self.current_query}/{self.total_queries}] [{source}] 搜索: {query:<40}", end="", flush=True)

    def update_file(self, filename: str, status: str = ""):
        """更新文件下载状态"""
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        status_str = f" | {status}" if status else ""
        print(f"\r[{self.current_query}/{self.total_queries}] 已运行 {mins:02d}:{secs:02d} | 下载: {filename[:30]:<30}{status_str}", end="", flush=True)

    def finish_query(self, stats: Dict[str, int]):
        """完成搜索词"""
        print(f"\r[{self.current_query}/{self.total_queries}] 完成 | 下载: {stats.get('downloaded', 0)} | 跳过: {stats.get('skipped', 0)}", flush=True)

    def summary(self, stats: Dict[str, int]):
        """显示总结"""
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)

        print("\n" + "=" * 70)
        print("运行总结")
        print("=" * 70)
        print(f"  运行时间: {mins:02d}:{secs:02d}")
        print(f"  搜索词: {self.current_query}/{self.total_queries}")
        print(f"  成功下载: {stats.get('downloaded', 0)}")
        print(f"  跳过: {stats.get('skipped', 0)}")
        print(f"  无效文件: {stats.get('invalid', 0)}")
        print(f"  重复文件: {stats.get('duplicate', 0)}")
        print(f"  失败: {stats.get('failed', 0)}")
        print("=" * 70)
