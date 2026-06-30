"""
解析器基类
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from typing import List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..utils import (
    is_valid_url,
    normalize_url,
    get_extension_from_url,
    github_to_raw,
    AdaptiveDelayer,
)


class BaseParser:
    """解析器基类"""

    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.headers = {"User-Agent": config.user_agent}
        self.delayer = AdaptiveDelayer(
            base_delay=config.request_delay,
            min_delay=config.min_delay,
            max_delay=config.max_delay,
        )

    def search(self, query: str) -> List[str]:
        """搜索，返回文件链接列表"""
        return []

    def extract_files_from_page(self, url: str, depth: int = 0) -> Tuple[List[str], List[str]]:
        """从页面提取文件链接和其他链接"""
        cad_links = []
        other_links = []

        try:
            self.delayer.wait()
            response = requests.get(url, headers=self.headers, timeout=self.config.timeout)
            self.delayer.success()
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = normalize_url(urljoin(url, href))
                ext = get_extension_from_url(full_url)

                if ext in self.config.target_extensions:
                    full_url = github_to_raw(full_url)
                    if full_url not in cad_links:
                        cad_links.append(full_url)
                elif is_valid_url(full_url) and depth < self.config.max_depth:
                    if full_url not in other_links:
                        other_links.append(full_url)

        except Exception as e:
            self.delayer.failure()

        return cad_links, other_links

    def _get(self, url: str, params=None):
        """发送GET请求"""
        self.delayer.wait()
        response = requests.get(url, headers=self.headers, params=params, timeout=self.config.timeout)
        if response.status_code == 200:
            self.delayer.success()
        else:
            self.delayer.failure()
        return response
