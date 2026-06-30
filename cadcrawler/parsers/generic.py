"""
通用解析器 - 适用于Google等搜索
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base import BaseParser
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from ..utils import is_valid_url, get_extension_from_url


class GenericParser(BaseParser):
    """通用解析器"""

    def search(self, query: str) -> list:
        """通用搜索 - 使用Google"""
        results = []
        url = f"https://www.google.com/search?q={quote(query)}"

        try:
            response = self._get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/url?q='):
                    actual_url = href[7:].split('&')[0]
                    if is_valid_url(actual_url):
                        # 先检查直接是否是文件
                        ext = get_extension_from_url(actual_url)
                        if ext in self.config.target_extensions:
                            if actual_url not in results:
                                results.append(actual_url)
                        else:
                            # 添加到待爬取页面
                            pass

        except Exception as e:
            pass

        return results[:10]
