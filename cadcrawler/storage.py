"""
存储和状态管理
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict


@dataclass
class FileRecord:
    """文件记录"""
    url: str
    filepath: str
    filename: str
    category: str
    file_hash: str
    downloaded_at: str
    source: str = ""
    size: int = 0


@dataclass
class CrawlerState:
    """爬虫状态"""
    config_name: str = ""
    started_at: str = ""
    last_updated: str = ""
    completed_queries: List[str] = field(default_factory=list)
    processed_urls: List[str] = field(default_factory=list)
    files: List[FileRecord] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlerState':
        files_data = data.pop('files', [])
        files = [FileRecord(**f) for f in files_data]
        return cls(files=files, **data)

    def to_dict(self) -> Dict[str, Any]:
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['files'] = [asdict(f) for f in self.files]
        return d


class StorageManager:
    """存储管理器"""

    def __init__(self, data_dir: str, config_name: str):
        self.config_name = config_name
        self.data_dir = os.path.join(data_dir, self._sanitize_name(config_name))
        self.downloads_dir = os.path.join(self.data_dir, "downloads")
        self.cache_dir = os.path.join(self.data_dir, "cache")
        self.state_file = os.path.join(self.data_dir, "state.json")
        self.hash_file = os.path.join(self.data_dir, "hashes.txt")

        # 确保目录存在
        self._ensure_dirs()

        # 加载状态
        self.state = self._load_state()
        self.hashes = self._load_hashes()

    def _sanitize_name(self, name: str) -> str:
        """清理文件名"""
        return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)

    def _ensure_dirs(self):
        """确保目录存在"""
        for d in [self.data_dir, self.downloads_dir, self.cache_dir]:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

    def _load_state(self) -> CrawlerState:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return CrawlerState.from_dict(json.load(f))
            except:
                pass
        return CrawlerState(config_name=self.config_name)

    def _save_state(self):
        """保存状态"""
        self.state.last_updated = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)

    def _load_hashes(self) -> Set[str]:
        """加载已下载的文件哈希"""
        hashes = set()
        if os.path.exists(self.hash_file):
            try:
                with open(self.hash_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        h = line.strip()
                        if h:
                            hashes.add(h)
            except:
                pass
        return hashes

    def _save_hashes(self):
        """保存哈希"""
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            for h in self.hashes:
                f.write(f"{h}\n")

    def is_url_processed(self, url: str) -> bool:
        """检查URL是否已处理"""
        return url in self.state.processed_urls

    def mark_url_processed(self, url: str):
        """标记URL为已处理"""
        if url not in self.state.processed_urls:
            self.state.processed_urls.append(url)
            self._save_state()

    def is_query_completed(self, query: str) -> bool:
        """检查搜索词是否已完成"""
        return query in self.state.completed_queries

    def mark_query_completed(self, query: str):
        """标记搜索词为已完成"""
        if query not in self.state.completed_queries:
            self.state.completed_queries.append(query)
            self._save_state()

    def is_hash_exists(self, file_hash: str) -> bool:
        """检查文件哈希是否已存在"""
        return file_hash in self.hashes

    def get_filepath(self, filename: str, category: str) -> str:
        """获取保存文件的路径"""
        category_dir = os.path.join(self.downloads_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir, exist_ok=True)

        filepath = os.path.join(category_dir, filename)
        # 处理重名
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(category_dir, f"{base}_{counter}{ext}")):
                counter += 1
            filepath = os.path.join(category_dir, f"{base}_{counter}{ext}")

        return filepath

    def add_file(self, record: FileRecord, file_hash: str):
        """添加文件记录"""
        self.state.files.append(record)
        if file_hash:
            self.hashes.add(file_hash)
        self._save_state()
        self._save_hashes()

    def start_session(self):
        """开始新会话"""
        if not self.state.started_at:
            self.state.started_at = datetime.now().isoformat()
        self._save_state()

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "queries_completed": len(self.state.completed_queries),
            "urls_processed": len(self.state.processed_urls),
            "files_downloaded": len(self.state.files),
        }

    def get_pending_queries(self, all_queries: List[str]) -> List[str]:
        """获取待处理的搜索词"""
        return [q for q in all_queries if q not in self.state.completed_queries]
