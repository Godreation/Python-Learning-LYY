from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.crawler_utils import CrawlerUtils

class BaseSpider(ABC):
    def __init__(self):
        self.utils = CrawlerUtils()
    
    @abstractmethod
    async def crawl(self, url: str) -> Dict[str, Any]:
        """爬取商品信息"""
        pass
    
    @abstractmethod
    def parse(self, html: str) -> Dict[str, Any]:
        """解析HTML获取商品信息"""
        pass
    
    def get_platform(self) -> str:
        """获取平台名称"""
        return self.__class__.__name__.replace('Spider', '').lower()
