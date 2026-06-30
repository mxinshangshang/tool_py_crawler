"""
Printables解析器
"""

from .base import BaseParser
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup


class PrintablesParser(BaseParser):
    """Printables解析器"""

    def search(self, query: str) -> list:
        """在Printables搜索"""
        results = []
        url = f"https://www.printables.com/search?q={quote(query)}"

        try:
            response = self._get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            project_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/model/' in href:
                    full_url = urljoin("https://www.printables.com", href)
                    if full_url not in project_links:
                        project_links.append(full_url)

            for link in project_links[:5]:
                files, _ = self.extract_files_from_page(link, depth=1)
                results.extend(files)

        except Exception as e:
            pass

        return results
