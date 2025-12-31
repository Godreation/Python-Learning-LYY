import random
import aiohttp
from dotenv import load_dotenv
import os
from typing import List, Optional

# 加载环境变量
load_dotenv()

class CrawlerUtils:
    def __init__(self):
        # 从环境变量加载配置
        self.user_agents = os.getenv('USER_AGENT_LIST', '').split(',')
        self.use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        self.proxies = os.getenv('PROXY_LIST', '').split(',') if self.use_proxy else []
        self.request_delay = float(os.getenv('REQUEST_DELAY', '1.0'))
    
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        if not self.user_agents:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        return random.choice(self.user_agents)
    
    def get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_headers(self) -> dict:
        """构建请求头"""
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def fetch(self, url: str, proxy: Optional[str] = None) -> str:
        """异步获取网页内容"""
        headers = self.get_headers()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, proxy=proxy, timeout=30) as response:
                    response.raise_for_status()
                    return await response.text()
            except aiohttp.ClientError as e:
                print(f"请求失败: {url}, 错误: {e}")
                return ""
    
    async def fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
        """带重试机制的异步请求"""
        for retry in range(max_retries):
            proxy = self.get_random_proxy() if self.use_proxy else None
            result = await self.fetch(url, proxy)
            if result:
                return result
            print(f"重试中... ({retry + 1}/{max_retries})")
        return ""
