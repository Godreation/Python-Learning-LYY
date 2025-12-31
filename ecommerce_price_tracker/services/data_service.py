from sqlalchemy.orm import Session
from models import Product, PriceHistory, Alert
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class DataService:
    def __init__(self, db: Session):
        self.db = db
    
    def save_product(self, product_data: Dict[str, Any]) -> Product:
        """保存商品信息"""
        # 检查商品是否已存在
        existing_product = self.db.query(Product).filter(Product.url == product_data['url']).first()
        
        if existing_product:
            # 更新商品信息
            for key, value in product_data.items():
                if hasattr(existing_product, key) and value:
                    setattr(existing_product, key, value)
            product = existing_product
        else:
            # 创建新商品
            product = Product(**product_data)
            self.db.add(product)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def save_price_history(self, product_id: int, price_data: Dict[str, Any]) -> PriceHistory:
        """保存价格历史记录"""
        price_history = PriceHistory(
            product_id=product_id,
            price=price_data['price'],
            original_price=price_data['original_price'],
            stock_status=price_data['stock_status'],
            discount=price_data['discount']
        )
        
        self.db.add(price_history)
        self.db.commit()
        self.db.refresh(price_history)
        return price_history
    
    def get_product_price_history(self, product_id: int, days: Optional[int] = None) -> pd.DataFrame:
        """获取商品价格历史数据"""
        query = self.db.query(PriceHistory).filter(PriceHistory.product_id == product_id)
        
        if days:
            # 只获取指定天数内的数据
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(PriceHistory.crawl_time >= start_date)
        
        # 按时间排序
        price_history = query.order_by(PriceHistory.crawl_time).all()
        
        # 转换为DataFrame
        data = [{
            'crawl_time': ph.crawl_time,
            'price': ph.price,
            'original_price': ph.original_price,
            'stock_status': ph.stock_status,
            'discount': ph.discount
        } for ph in price_history]
        
        return pd.DataFrame(data)
    
    def get_all_products(self) -> List[Product]:
        """获取所有商品"""
        return self.db.query(Product).all()
    
    def analyze_price_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析价格趋势"""
        if df.empty:
            return {}
        
        # 确保crawl_time是datetime类型
        df['crawl_time'] = pd.to_datetime(df['crawl_time'])
        
        # 设置crawl_time为索引
        df = df.set_index('crawl_time')
        
        # 价格统计信息
        price_stats = {
            'current_price': float(df['price'].iloc[-1]) if not df.empty else 0.0,
            'avg_price': float(df['price'].mean()) if not df.empty else 0.0,
            'min_price': float(df['price'].min()) if not df.empty else 0.0,
            'max_price': float(df['price'].max()) if not df.empty else 0.0,
            'price_change': float(df['price'].iloc[-1] - df['price'].iloc[0]) if len(df) > 1 else 0.0,
            'price_change_percent': float(((df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0] * 100)) if len(df) > 1 and df['price'].iloc[0] != 0 else 0.0
        }
        
        # 价格趋势（使用滚动平均）
        df['price_ma7'] = df['price'].rolling(window=7).mean()
        df['price_ma30'] = df['price'].rolling(window=30).mean()
        
        # 转换为JSON格式
        trend_data = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'prices': df['price'].tolist(),
            'price_ma7': df['price_ma7'].tolist(),
            'price_ma30': df['price_ma30'].tolist()
        }
        
        return {
            'price_stats': price_stats,
            'trend_data': trend_data
        }
    
    def get_price_alerts(self) -> List[Dict[str, Any]]:
        """获取需要触发告警的商品"""
        alerts = []
        
        # 获取所有激活的告警
        active_alerts = self.db.query(Alert).filter(Alert.is_active == 1).all()
        
        for alert in active_alerts:
            # 获取最新价格
            latest_price = self.db.query(PriceHistory).filter(
                PriceHistory.product_id == alert.product_id
            ).order_by(PriceHistory.crawl_time.desc()).first()
            
            if latest_price and latest_price.price < alert.threshold_price:
                # 获取商品信息
                product = self.db.query(Product).filter(Product.id == alert.product_id).first()
                if product:
                    alerts.append({
                        'alert': alert,
                        'product': product,
                        'latest_price': latest_price.price
                    })
        
        return alerts
    
    def update_alert_last_time(self, alert_id: int) -> None:
        """更新告警最后触发时间"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.last_alert_time = datetime.now()
            self.db.commit()
    
    def get_products_dataframe(self) -> pd.DataFrame:
        """获取所有商品数据的DataFrame"""
        products = self.get_all_products()
        
        data = []
        for product in products:
            # 获取最新价格
            latest_price = self.db.query(PriceHistory).filter(
                PriceHistory.product_id == product.id
            ).order_by(PriceHistory.crawl_time.desc()).first()
            
            product_data = {
                'id': product.id,
                'name': product.name,
                'url': product.url,
                'platform': product.platform,
                'brand': product.brand,
                'category': product.category,
                'created_at': product.created_at,
                'updated_at': product.updated_at,
                'latest_price': latest_price.price if latest_price else 0.0,
                'latest_stock': latest_price.stock_status if latest_price else 'unknown'
            }
            data.append(product_data)
        
        return pd.DataFrame(data)
