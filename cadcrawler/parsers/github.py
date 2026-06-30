"""
GitHub解析器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base import BaseParser
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from ..utils import github_to_raw


class GitHubParser(BaseParser):
    """GitHub解析器"""

    def search(self, query: str) -> list:
        """在GitHub搜索"""
        results = []

        # 搜索每种目标文件类型
        for ext in [e for e in self.config.target_extensions if e in ('.dxf', '.stl', '.step', '.stp', '.svg')]:
            search_query = f"{query} {ext.lstrip('.')}"
            url = f"https://github.com/search?q={quote(search_query)}&type=code"

            try:
                response = self._get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '/blob/' in href and ext.lower() in href.lower():
                        full_url = urljoin("https://github.com", href)
                        raw_url = github_to_raw(full_url)
                        if raw_url not in results:
                            results.append(raw_url)

            except Exception as e:
                pass

        return results[:15]  # 限制数量
