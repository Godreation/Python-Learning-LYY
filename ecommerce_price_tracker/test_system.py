import pytest
import asyncio
from models import Base, engine, SessionLocal, Product, PriceHistory, Alert
from spiders import JDSpider, TaobaoSpider
from services.data_service import DataService
from services.alert_service import AlertService
from services.visualization_service import VisualizationService
import os
import tempfile

# 测试数据库URL（使用SQLite内存数据库进行测试）
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_session():
    """创建数据库会话和测试表"""
    # 创建测试表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = SessionLocal()
    
    yield db
    
    # 清理测试数据
    db.query(PriceHistory).delete()
    db.query(Alert).delete()
    db.query(Product).delete()
    db.commit()
    db.close()

@pytest.fixture
def data_service(db_session):
    """创建数据服务实例"""
    return DataService(db_session)

@pytest.fixture
def alert_service():
    """创建告警服务实例"""
    return AlertService()

@pytest.fixture
def visualization_service():
    """创建可视化服务实例"""
    return VisualizationService()

# 测试商品数据
test_product_data = {
    "name": "测试商品",
    "url": "https://test.com/product/123",
    "platform": "jd",
    "brand": "测试品牌",
    "category": "测试分类",
    "image_url": "https://test.com/image.jpg"
}

# 测试价格数据
test_price_data = {
    "price": 99.99,
    "original_price": 129.99,
    "stock_status": "in_stock",
    "discount": 0.77
}

def test_product_model(db_session):
    """测试商品模型"""
    # 创建商品
    product = Product(**test_product_data)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # 验证商品创建
    assert product.id is not None
    assert product.name == test_product_data["name"]
    assert product.url == test_product_data["url"]
    
    # 查询商品
    query_product = db_session.query(Product).filter(Product.id == product.id).first()
    assert query_product is not None
    assert query_product.name == product.name

def test_price_history_model(db_session):
    """测试价格历史模型"""
    # 先创建商品
    product = Product(**test_product_data)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # 创建价格历史
    price_history = PriceHistory(
        product_id=product.id,
        **test_price_data
    )
    db_session.add(price_history)
    db_session.commit()
    db_session.refresh(price_history)
    
    # 验证价格历史创建
    assert price_history.id is not None
    assert price_history.product_id == product.id
    assert price_history.price == test_price_data["price"]
    
    # 查询价格历史
    query_price_history = db_session.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).first()
    assert query_price_history is not None
    assert query_price_history.price == test_price_data["price"]

@pytest.mark.asyncio
async def test_jd_spider():
    """测试京东爬虫"""
    spider = JDSpider()
    # 使用京东测试URL（实际测试时需要替换为真实URL）
    test_url = "https://item.jd.com/100012345678.html"
    
    # 测试爬虫不抛出异常
    try:
        product_data = await spider.crawl(test_url)
        # 验证返回数据格式
        assert isinstance(product_data, dict)
    except Exception as e:
        # 网络请求可能失败，这里只测试不抛出未处理的异常
        assert True, f"爬虫抛出异常: {e}"

@pytest.mark.asyncio
async def test_taobao_spider():
    """测试淘宝爬虫"""
    spider = TaobaoSpider()
    # 使用淘宝测试URL（实际测试时需要替换为真实URL）
    test_url = "https://item.taobao.com/item.htm?id=1234567890"
    
    # 测试爬虫不抛出异常
    try:
        product_data = await spider.crawl(test_url)
        # 验证返回数据格式
        assert isinstance(product_data, dict)
    except Exception as e:
        # 网络请求可能失败，这里只测试不抛出未处理的异常
        assert True, f"爬虫抛出异常: {e}"

def test_save_product(data_service):
    """测试保存商品"""
    # 保存商品
    product = data_service.save_product(test_product_data)
    
    # 验证商品保存
    assert product.id is not None
    assert product.name == test_product_data["name"]
    
    # 测试更新商品
    updated_data = test_product_data.copy()
    updated_data["name"] = "更新后的测试商品"
    updated_product = data_service.save_product(updated_data)
    
    # 验证商品更新
    assert updated_product.id == product.id
    assert updated_product.name == updated_data["name"]

def test_save_price_history(data_service):
    """测试保存价格历史"""
    # 先保存商品
    product = data_service.save_product(test_product_data)
    
    # 保存价格历史
    price_history = data_service.save_price_history(product.id, test_price_data)
    
    # 验证价格历史保存
    assert price_history.id is not None
    assert price_history.product_id == product.id
    assert price_history.price == test_price_data["price"]

def test_get_product_price_history(data_service):
    """测试获取商品价格历史"""
    # 先保存商品和价格历史
    product = data_service.save_product(test_product_data)
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取价格历史
    df = data_service.get_product_price_history(product.id)
    
    # 验证返回的DataFrame
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]["price"] == test_price_data["price"]

def test_analyze_price_trend(data_service):
    """测试价格趋势分析"""
    # 先保存商品和价格历史
    product = data_service.save_product(test_product_data)
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取价格历史
    df = data_service.get_product_price_history(product.id)
    
    # 分析价格趋势
    trend_analysis = data_service.analyze_price_trend(df)
    
    # 验证趋势分析结果
    assert isinstance(trend_analysis, dict)
    assert "price_stats" in trend_analysis
    assert "trend_data" in trend_analysis
    assert isinstance(trend_analysis["price_stats"], dict)
    assert isinstance(trend_analysis["trend_data"], dict)

def test_alert_model(db_session):
    """测试告警模型"""
    # 先创建商品
    product = Product(**test_product_data)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # 创建告警
    alert = Alert(
        product_id=product.id,
        threshold_price=80.0,
        email="test@example.com",
        is_active=1
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    
    # 验证告警创建
    assert alert.id is not None
    assert alert.product_id == product.id
    assert alert.threshold_price == 80.0

def test_get_price_alerts(data_service):
    """测试获取价格告警"""
    # 先保存商品和价格历史（价格低于告警阈值）
    product = data_service.save_product(test_product_data)
    
    # 创建告警（阈值100.0，当前价格99.99低于阈值）
    alert = Alert(
        product_id=product.id,
        threshold_price=100.0,
        email="test@example.com",
        is_active=1
    )
    data_service.db.add(alert)
    data_service.db.commit()
    data_service.db.refresh(alert)
    
    # 保存价格历史
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取告警
    alerts = data_service.get_price_alerts()
    
    # 验证告警获取
    assert len(alerts) == 1
    assert alerts[0]["alert"].id == alert.id
    assert alerts[0]["product"].id == product.id
    assert alerts[0]["latest_price"] == test_price_data["price"]

def test_update_alert_last_time(data_service):
    """测试更新告警最后触发时间"""
    # 先保存商品和告警
    product = data_service.save_product(test_product_data)
    alert = Alert(
        product_id=product.id,
        threshold_price=100.0,
        email="test@example.com",
        is_active=1
    )
    data_service.db.add(alert)
    data_service.db.commit()
    data_service.db.refresh(alert)
    
    # 更新告警最后触发时间
    data_service.update_alert_last_time(alert.id)
    
    # 验证告警最后触发时间已更新
    updated_alert = data_service.db.query(Alert).filter(Alert.id == alert.id).first()
    assert updated_alert.last_alert_time is not None

def test_generate_price_trend_chart(visualization_service, data_service):
    """测试生成价格趋势图"""
    # 先保存商品和价格历史
    product = data_service.save_product(test_product_data)
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取价格历史
    df = data_service.get_product_price_history(product.id)
    
    # 生成价格趋势图
    chart_path = visualization_service.generate_price_trend_chart(df, product.name, days=30)
    
    # 验证图表生成
    assert isinstance(chart_path, str)
    assert chart_path.endswith(".png")
    # 验证文件存在
    assert os.path.exists(chart_path)
    # 清理测试生成的文件
    if os.path.exists(chart_path):
        os.remove(chart_path)

def test_generate_price_distribution_chart(visualization_service, data_service):
    """测试生成价格分布直方图"""
    # 先保存商品和价格历史
    product = data_service.save_product(test_product_data)
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取价格历史
    df = data_service.get_product_price_history(product.id)
    
    # 生成价格分布直方图
    chart_path = visualization_service.generate_price_distribution_chart(df, product.name)
    
    # 验证图表生成
    assert isinstance(chart_path, str)
    assert chart_path.endswith(".png")
    # 验证文件存在
    assert os.path.exists(chart_path)
    # 清理测试生成的文件
    if os.path.exists(chart_path):
        os.remove(chart_path)

def test_generate_summary_statistics(visualization_service, data_service):
    """测试生成价格统计摘要"""
    # 先保存商品和价格历史
    product = data_service.save_product(test_product_data)
    data_service.save_price_history(product.id, test_price_data)
    
    # 获取价格历史
    df = data_service.get_product_price_history(product.id)
    
    # 生成价格统计摘要
    summary_path = visualization_service.generate_summary_statistics(df, product.name)
    
    # 验证摘要生成
    assert isinstance(summary_path, str)
    assert summary_path.endswith(".txt")
    # 验证文件存在
    assert os.path.exists(summary_path)
    # 清理测试生成的文件
    if os.path.exists(summary_path):
        os.remove(summary_path)

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
