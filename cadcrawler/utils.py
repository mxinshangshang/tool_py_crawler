"""
通用工具函数
"""

import os
import time
import hashlib
from urllib.parse import urljoin, urlparse, unquote


def is_valid_url(url):
    """检查URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url):
    """标准化URL"""
    url = url.strip()
    if not url.startswith('http'):
        url = 'https://' + url
    return url


def get_extension_from_url(url):
    """从URL获取文件扩展名"""
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    return ext


def extract_filename(url):
    """从URL提取文件名"""
    path = unquote(urlparse(url).path)
    filename = os.path.basename(path)
    if not filename or '.' not in filename:
        return None
    return filename


def github_to_raw(url):
    """将GitHub blob URL转换为raw URL"""
    if 'github.com' in url and '/blob/' in url:
        return url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
    return url


def get_file_category(ext, target_extensions):
    """根据扩展名获取文件分类"""
    ext_lower = ext.lower()
    # 简单分类：使用扩展名去掉点
    if ext_lower.startswith('.'):
        return ext_lower[1:]
    return ext_lower


def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def get_unique_filepath(filepath):
    """获取不重复的文件路径"""
    if not os.path.exists(filepath):
        return filepath
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    return f"{base}_{counter}{ext}"


def compute_file_hash(filepath, chunk_size=65536):
    """计算文件的SHA-256哈希"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return None


class AdaptiveDelayer:
    """自适应延迟器 - 根据失败情况调整请求间隔"""

    def __init__(self, base_delay=4.0, min_delay=2.0, max_delay=30.0):
        self.base_delay = base_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.consecutive_failures = 0

    def success(self):
        """请求成功时调用"""
        self.consecutive_failures = 0
        # 逐渐恢复到基准延迟
        if self.current_delay > self.base_delay:
            self.current_delay = max(self.base_delay, self.current_delay * 0.9)

    def failure(self):
        """请求失败时调用"""
        self.consecutive_failures += 1
        # 指数退避
        multiplier = 1.5 ** self.consecutive_failures
        self.current_delay = min(self.max_delay, self.base_delay * multiplier)

    def wait(self):
        """等待适当的时间"""
        time.sleep(self.current_delay)

    def get_current_delay(self):
        """获取当前延迟"""
        return self.current_delay
