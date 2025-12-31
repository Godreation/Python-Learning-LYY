from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True)
    platform = Column(String(50), nullable=False, index=True)  # 京东、淘宝等
    brand = Column(String(100))
    category = Column(String(100))
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    stock_status = Column(String(20))  # in_stock, out_of_stock, pre_order
    discount = Column(Float)  # 折扣率，如0.8表示8折
    crawl_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    product = relationship("Product", back_populates="price_history")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    threshold_price = Column(Float, nullable=False)
    email = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)  # 1: 激活, 0: 停用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_alert_time = Column(DateTime(timezone=True))
    
    # 关系
    product = relationship("Product", back_populates="alerts")
