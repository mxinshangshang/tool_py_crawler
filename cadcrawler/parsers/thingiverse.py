"""
Thingiverse解析器
"""

from .base import BaseParser
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup


class ThingiverseParser(BaseParser):
    """Thingiverse解析器"""

    def search(self, query: str) -> list:
        """在Thingiverse搜索"""
        results = []
        url = f"https://www.thingiverse.com/search?q={quote(query)}&type=things&sort=relevant"

        try:
            response = self._get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取项目链接
            project_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/thing:' in href:
                    full_url = urljoin("https://www.thingiverse.com", href)
                    if full_url not in project_links:
                        project_links.append(full_url)

            # 访问每个项目页面提取文件
            for link in project_links[:5]:
                files, _ = self.extract_files_from_page(link, depth=1)
                results.extend(files)

        except Exception as e:
            pass

        return results
