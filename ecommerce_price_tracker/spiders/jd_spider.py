from .base_spider import BaseSpider
from typing import Dict, Any
from bs4 import BeautifulSoup
import re

class JDSpider(BaseSpider):
    async def crawl(self, url: str) -> Dict[str, Any]:
        """爬取京东商品信息"""
        html = await self.utils.fetch_with_retry(url)
        if not html:
            return {}
        return self.parse(html)
    
    def parse(self, html: str) -> Dict[str, Any]:
        """解析京东商品页面"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # 商品名称
            name = soup.find('div', class_='sku-name').get_text().strip() if soup.find('div', class_='sku-name') else ''
            
            # 商品价格
            price = 0.0
            price_elem = soup.find('span', class_='price J-p-')
            if price_elem:
                price_text = price_elem.get_text().strip()
                if price_text:
                    price = float(price_text)
            
            # 原价
            original_price = 0.0
            original_price_elem = soup.find('span', class_='p-price-old')
            if original_price_elem:
                original_price_text = original_price_elem.get_text().strip()
                if original_price_text:
                    original_price = float(original_price_text)
            
            # 品牌
            brand = ''
            brand_elem = soup.find('ul', class_='parameter2 p-parameter-list')
            if brand_elem:
                brand_match = re.search(r'品牌：([^<]+)', str(brand_elem))
                if brand_match:
                    brand = brand_match.group(1)
            
            # 商品图片
            image_url = ''
            image_elem = soup.find('img', id='spec-img')
            if image_elem and 'data-origin' in image_elem.attrs:
                image_url = image_elem['data-origin']
            elif image_elem and 'src' in image_elem.attrs:
                image_url = image_elem['src']
            
            # 库存状态
            stock_status = 'in_stock'
            stock_elem = soup.find('div', class_='btn-area')
            if stock_elem:
                if '无货' in str(stock_elem):
                    stock_status = 'out_of_stock'
            
            # 折扣计算
            discount = 0.0
            if original_price > 0 and price > 0:
                discount = price / original_price
            
            return {
                'name': name,
                'price': price,
                'original_price': original_price,
                'brand': brand,
                'image_url': image_url,
                'stock_status': stock_status,
                'discount': discount
            }
        except Exception as e:
            print(f"解析京东页面失败: {e}")
            return {}
