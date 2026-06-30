"""
配置管理系统
"""

import os
import yaml
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    """爬虫配置"""
    name: str = "default"

    # 关键词配置
    base_keywords: List[str] = field(default_factory=list)
    product_types: List[str] = field(default_factory=list)
    file_types: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    processes: List[str] = field(default_factory=list)

    # 目标文件扩展名
    target_extensions: List[str] = field(default_factory=lambda: [".dxf", ".stl", ".step", ".stp", ".svg", ".dwg"])

    # 数据源
    sources: List[str] = field(default_factory=lambda: ["github", "thingiverse", "printables", "google"])

    # 爬虫行为
    request_delay: float = 4.0
    min_delay: float = 2.0
    max_delay: float = 30.0
    timeout: int = 30
    max_depth: int = 2
    max_queries: int = 30
    max_pages_per_source: int = 15

    # 文件处理
    verify_files: bool = True
    deduplicate: bool = True

    # User-Agent
    user_agent: str = "CAD-Crawler/2.0 (+https://github.com/example/cad-crawler)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlerConfig':
        """从字典创建配置"""
        # 获取dataclass的所有字段名
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(cls)}
        # 只传递有效的字段
        return cls(**{k: v for k, v in data.items() if k in field_names})

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "base_keywords": self.base_keywords,
            "product_types": self.product_types,
            "file_types": self.file_types,
            "materials": self.materials,
            "processes": self.processes,
            "target_extensions": self.target_extensions,
            "sources": self.sources,
            "request_delay": self.request_delay,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
            "timeout": self.timeout,
            "max_depth": self.max_depth,
            "max_queries": self.max_queries,
            "max_pages_per_source": self.max_pages_per_source,
            "verify_files": self.verify_files,
            "deduplicate": self.deduplicate,
            "user_agent": self.user_agent,
        }

    def generate_search_queries(self) -> List[str]:
        """生成搜索关键词组合"""
        queries = []

        # 英文组合
        for base in self.base_keywords:
            # 只搜索有实际意义的组合，避免200+的组合爆炸
            if not base or not self.product_types:
                continue

            # 核心组合：基础 + 产品类型
            for product in self.product_types:
                queries.append(f"{base} {product}")

                # 基础 + 产品 + 文件类型（只选主要的几个）
                for ft in self.file_types[:3]:
                    queries.append(f"{base} {product} {ft}")

                # 基础 + 产品 + 工艺（选主要的）
                for proc in self.processes[:2]:
                    queries.append(f"{base} {product} {proc}")

                # 基础 + 产品 + 材质（选主要的）
                for mat in self.materials[:2]:
                    queries.append(f"{base} {product} {mat}")

            # 基础 + 文件类型（直接搜索）
            for ft in self.file_types[:3]:
                queries.append(f"{base} {ft}")

        # 去重并限制数量
        unique_queries = list(dict.fromkeys(queries))
        return unique_queries[:self.max_queries]


class ConfigManager:
    """配置管理器"""

    def __init__(self, configs_dir: str = None):
        if configs_dir is None:
            configs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
        self.configs_dir = configs_dir

    def list_configs(self) -> List[str]:
        """列出所有可用配置"""
        if not os.path.exists(self.configs_dir):
            return []
        configs = []
        for f in os.listdir(self.configs_dir):
            if f.endswith('.yaml') or f.endswith('.yml'):
                configs.append(os.path.splitext(f)[0])
        return sorted(configs)

    def load_config(self, name_or_path: str) -> CrawlerConfig:
        """加载配置"""
        # 如果是路径，直接加载
        if os.path.exists(name_or_path):
            filepath = name_or_path
        else:
            # 尝试在configs目录找
            for ext in ['.yaml', '.yml']:
                filepath = os.path.join(self.configs_dir, name_or_path + ext)
                if os.path.exists(filepath):
                    break
            else:
                raise ValueError(f"配置 '{name_or_path}' 不存在")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return CrawlerConfig.from_dict(data)

    def save_config(self, config: CrawlerConfig, filename: str = None):
        """保存配置"""
        if filename is None:
            filename = config.name + ".yaml"
        if not os.path.isabs(filename):
            filename = os.path.join(self.configs_dir, filename)

        ensure_dir(os.path.dirname(filename))

        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, allow_unicode=True)


from .utils import ensure_dir
