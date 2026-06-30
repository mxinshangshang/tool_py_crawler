from .base import BaseParser
from .github import GitHubParser
from .thingiverse import ThingiverseParser
from .printables import PrintablesParser
from .generic import GenericParser


def get_parser(name: str):
    """获取解析器"""
    parsers = {
        'github': GitHubParser,
        'thingiverse': ThingiverseParser,
        'printables': PrintablesParser,
        'generic': GenericParser,
        'google': GenericParser,
    }
    return parsers.get(name, GenericParser)


__all__ = ['BaseParser', 'get_parser', 'GitHubParser', 'ThingiverseParser', 'PrintablesParser', 'GenericParser']
