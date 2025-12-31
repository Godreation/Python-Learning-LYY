import asyncio
from models import Base, engine, SessionLocal
from spiders import JDSpider, TaobaoSpider
from services.data_service import DataService
from services.alert_service import AlertService
from services.visualization_service import VisualizationService
from services.scheduler_service import SchedulerService
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import time

# 加载环境变量
load_dotenv()

# 初始化数据库
def init_db():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功")

# 商品URL列表（示例）
PRODUCT_URLS = [
    # 京东商品示例
    {
        "url": "https://item.jd.com/100012345678.html",
        "platform": "jd"
    },
    # 淘宝商品示例
    {
        "url": "https://item.taobao.com/item.htm?id=1234567890",
        "platform": "taobao"
    }
]

async def crawl_product_price(url: str, platform: str) -> Dict[str, Any]:
    """爬取单个商品价格"""
    print(f"开始爬取 {platform} 商品: {url}")
    
    # 根据平台选择对应的爬虫
    if platform == "jd":
        spider = JDSpider()
    elif platform == "taobao":
        spider = TaobaoSpider()
    else:
        print(f"不支持的平台: {platform}")
        return {}
    
    # 执行爬取
    product_data = await spider.crawl(url)
    
    if product_data:
        product_data['url'] = url
        product_data['platform'] = platform
        print(f"爬取成功: {product_data.get('name')}, 价格: {product_data.get('price')} 元")
    
    return product_data

async def crawl_all_products() -> None:
    """爬取所有商品价格"""
    print(f"\n=== 开始爬取所有商品价格 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        data_service = DataService(db)
        
        for product_info in PRODUCT_URLS:
            url = product_info['url']
            platform = product_info['platform']
            
            # 爬取商品数据
            product_data = await crawl_product_price(url, platform)
            
            if product_data:
                # 保存商品信息
                product = data_service.save_product(product_data)
                
                # 保存价格历史
                data_service.save_price_history(product.id, product_data)
                
                # 等待一段时间，避免请求过于频繁
                await asyncio.sleep(float(os.getenv('REQUEST_DELAY', '1.0')))
    finally:
        db.close()
    
    print(f"=== 所有商品价格爬取完成 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

def check_price_alerts():
    """检查价格告警"""
    print(f"\n=== 开始检查价格告警 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        data_service = DataService(db)
        alert_service = AlertService()
        
        # 获取需要告警的商品
        alerts = data_service.get_price_alerts()
        
        if alerts:
            print(f"发现 {len(alerts)} 个商品需要告警")
            
            # 发送告警邮件
            sent_count = alert_service.send_price_alerts(alerts)
            
            # 更新告警最后触发时间
            for alert_data in alerts:
                data_service.update_alert_last_time(alert_data['alert'].id)
            
            print(f"成功发送 {sent_count} 封告警邮件")
        else:
            print("没有商品需要告警")
    finally:
        db.close()
    
    print(f"=== 价格告警检查完成 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

def generate_visualization_reports():
    """生成可视化报告"""
    print(f"\n=== 开始生成可视化报告 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        data_service = DataService(db)
        viz_service = VisualizationService()
        
        # 获取所有商品数据
        products_df = data_service.get_products_dataframe()
        
        if not products_df.empty:
            # 生成平台价格对比图
            viz_service.generate_platform_comparison_chart(products_df)
            
            # 为每个商品生成详细报告
            products_history = {}
            for _, product in products_df.iterrows():
                # 获取商品价格历史
                df = data_service.get_product_price_history(product['id'], days=30)
                if not df.empty:
                    products_history[product['id']] = df
                    
                    # 生成价格趋势图
                    viz_service.generate_price_trend_chart(df, product['name'], days=30)
                    
                    # 生成价格分布直方图
                    viz_service.generate_price_distribution_chart(df, product['name'])
                    
                    # 生成价格统计摘要
                    viz_service.generate_summary_statistics(df, product['name'])
            
            print(f"成功生成 {len(products_history)} 个商品的可视化报告")
        else:
            print("没有商品数据可用于生成报告")
    finally:
        db.close()
    
    print(f"=== 可视化报告生成完成 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

def send_daily_report():
    """发送每日报告"""
    print(f"\n=== 开始发送每日报告 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        data_service = DataService(db)
        alert_service = AlertService()
        
        # 获取所有商品数据
        products_df = data_service.get_products_dataframe()
        
        # 生成报告数据
        report_data = {
            'date': time.strftime('%Y-%m-%d'),
            'total_products': len(products_df),
            'updated_products': len(products_df),  # 简化处理，实际应统计今日更新的商品
            'price_decreased_products': 0  # 简化处理，实际应统计价格下降的商品
        }
        
        # 发送每日报告邮件
        alert_service.send_daily_report_email(report_data)
        
        print("每日报告邮件发送成功")
    finally:
        db.close()
    
    print(f"=== 每日报告发送完成 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

def main():
    """主程序入口"""
    print("=== 电商价格监控系统启动 ===")
    
    # 初始化数据库
    init_db()
    
    # 创建调度器
    scheduler = SchedulerService()
    
    try:
        # 立即执行一次商品爬取
        asyncio.run(crawl_all_products())
        
        # 立即生成一次可视化报告
        generate_visualization_reports()
        
        # 立即检查一次价格告警
        check_price_alerts()
        
        # 设置定时任务
        scheduler.schedule_price_crawling(
            lambda: asyncio.run(crawl_all_products()),
            hours=1  # 每小时爬取一次
        )
        
        scheduler.schedule_price_alerts(
            check_price_alerts,
            minutes=30  # 每30分钟检查一次告警
        )
        
        scheduler.schedule_visualization_generation(
            generate_visualization_reports,
            hours=24  # 每天生成一次可视化报告
        )
        
        scheduler.schedule_daily_report(
            send_daily_report,
            hour=9, minute=0  # 每天上午9点发送报告
        )
        
        # 启动调度器
        scheduler.start()
        
        # 保持主程序运行
        print("\n系统已启动，按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭系统...")
        
        # 关闭调度器
        scheduler.shutdown()
        
    print("\n=== 电商价格监控系统已停止 ===")

if __name__ == "__main__":
    main()
