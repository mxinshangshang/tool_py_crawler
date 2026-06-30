"""
资源友好的下载器
"""

import os
import time
import requests
from datetime import datetime
from typing import Optional
from .storage import FileRecord
from .utils import (
    get_extension_from_url,
    extract_filename,
    get_file_category,
    compute_file_hash,
    AdaptiveDelayer,
)
from .validators import validate_file


class Downloader:
    """资源友好的下载器"""

    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.headers = {"User-Agent": config.user_agent}
        self.delayer = AdaptiveDelayer(
            base_delay=config.request_delay,
            min_delay=config.min_delay,
            max_delay=config.max_delay,
        )

        # 统计
        self.stats = {
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "invalid": 0,
            "duplicate": 0,
        }

    def download(self, url: str, source: str = "") -> Optional[FileRecord]:
        """下载单个文件"""
        self.stats["total"] += 1

        # 检查URL是否已处理
        if self.storage.is_url_processed(url):
            self.stats["skipped"] += 1
            return None

        ext = get_extension_from_url(url)
        if ext not in self.config.target_extensions:
            self.stats["skipped"] += 1
            self.storage.mark_url_processed(url)
            return None

        # 提取文件名
        filename = extract_filename(url)
        if not filename:
            filename = f"file_{int(time.time())}{ext}"

        category = get_file_category(ext, self.config.target_extensions)
        filepath = self.storage.get_filepath(filename, category)

        try:
            self.delayer.wait()

            response = requests.get(url, headers=self.headers, timeout=self.config.timeout)
            response.raise_for_status()
            self.delayer.success()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            # 验证文件
            if self.config.verify_files:
                if not validate_file(filepath, ext):
                    os.remove(filepath)
                    self.stats["invalid"] += 1
                    self.storage.mark_url_processed(url)
                    return None

            # 检查重复
            file_hash = compute_file_hash(filepath)
            if self.config.deduplicate and file_hash:
                if self.storage.is_hash_exists(file_hash):
                    os.remove(filepath)
                    self.stats["duplicate"] += 1
                    self.storage.mark_url_processed(url)
                    return None

            # 保存记录
            record = FileRecord(
                url=url,
                filepath=filepath,
                filename=os.path.basename(filepath),
                category=category,
                file_hash=file_hash or "",
                downloaded_at=datetime.now().isoformat(),
                source=source,
                size=os.path.getsize(filepath),
            )

            self.storage.add_file(record, file_hash)
            self.storage.mark_url_processed(url)

            self.stats["downloaded"] += 1
            return record

        except Exception as e:
            self.delayer.failure()
            self.stats["failed"] += 1
            self.storage.mark_url_processed(url)

            # 清理可能的部分文件
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return None

    def get_current_delay(self) -> float:
        """获取当前延迟"""
        return self.delayer.get_current_delay()
