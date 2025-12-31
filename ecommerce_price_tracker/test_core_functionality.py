import asyncio
from spiders import JDSpider, TaobaoSpider
from services.visualization_service import VisualizationService
import pandas as pd
from datetime import datetime, timedelta
import os

async def test_spiders():
    """测试爬虫功能"""
    print("=== 测试爬虫功能 ===")
    
    # 京东爬虫测试
    print("\n1. 测试京东爬虫")
    jd_spider = JDSpider()
    try:
        # 使用京东测试URL
        jd_url = "https://item.jd.com/100012345678.html"
        product_data = await jd_spider.crawl(jd_url)
        print(f"京东爬虫返回数据类型: {type(product_data)}")
        if product_data:
            print(f"京东爬虫返回数据: {product_data.keys()}")
            if "name" in product_data and product_data["name"]:
                print(f"商品名称: {product_data['name']}")
            if "price" in product_data:
                print(f"商品价格: {product_data['price']} 元")
        print("京东爬虫测试完成")
    except Exception as e:
        print(f"京东爬虫测试失败: {e}")
    
    # 淘宝爬虫测试
    print("\n2. 测试淘宝爬虫")
    taobao_spider = TaobaoSpider()
    try:
        # 使用淘宝测试URL
        taobao_url = "https://item.taobao.com/item.htm?id=1234567890"
        product_data = await taobao_spider.crawl(taobao_url)
        print(f"淘宝爬虫返回数据类型: {type(product_data)}")
        if product_data:
            print(f"淘宝爬虫返回数据: {product_data.keys()}")
            if "name" in product_data and product_data["name"]:
                print(f"商品名称: {product_data['name']}")
            if "price" in product_data:
                print(f"商品价格: {product_data['price']} 元")
        print("淘宝爬虫测试完成")
    except Exception as e:
        print(f"淘宝爬虫测试失败: {e}")
    
    print("\n=== 爬虫功能测试完成 ===")

def test_visualization():
    """测试可视化功能"""
    print("\n=== 测试可视化功能 ===")
    
    # 创建可视化服务实例
    viz_service = VisualizationService()
    
    # 创建测试数据
    dates = [datetime.now() - timedelta(days=i) for i in range(30)][::-1]
    prices = [100 - i*0.5 + (i%5)*2 for i in range(30)]
    
    # 创建DataFrame
    df = pd.DataFrame({
        'crawl_time': dates,
        'price': prices,
        'original_price': [p + 20 for p in prices],
        'stock_status': ['in_stock'] * 30,
        'discount': [p/(p+20) for p in prices]
    })
    
    print(f"测试数据创建完成，共 {len(df)} 条记录")
    print(f"价格范围: {df['price'].min():.2f} - {df['price'].max():.2f} 元")
    
    # 测试生成价格趋势图
    print("\n1. 测试生成价格趋势图")
    try:
        chart_path = viz_service.generate_price_trend_chart(df, "测试商品", days=30)
        if chart_path and os.path.exists(chart_path):
            print(f"价格趋势图生成成功: {chart_path}")
            # 清理生成的文件
            os.remove(chart_path)
        else:
            print("价格趋势图生成失败")
    except Exception as e:
        print(f"生成价格趋势图失败: {e}")
    
    # 测试生成价格分布直方图
    print("\n2. 测试生成价格分布直方图")
    try:
        chart_path = viz_service.generate_price_distribution_chart(df, "测试商品")
        if chart_path and os.path.exists(chart_path):
            print(f"价格分布直方图生成成功: {chart_path}")
            # 清理生成的文件
            os.remove(chart_path)
        else:
            print("价格分布直方图生成失败")
    except Exception as e:
        print(f"生成价格分布直方图失败: {e}")
    
    # 测试生成价格统计摘要
    print("\n3. 测试生成价格统计摘要")
    try:
        summary_path = viz_service.generate_summary_statistics(df, "测试商品")
        if summary_path and os.path.exists(summary_path):
            print(f"价格统计摘要生成成功: {summary_path}")
            # 显示摘要内容
            with open(summary_path, 'r', encoding='utf-8') as f:
                print("\n摘要内容:")
                print(f.read())
            # 清理生成的文件
            os.remove(summary_path)
        else:
            print("价格统计摘要生成失败")
    except Exception as e:
        print(f"生成价格统计摘要失败: {e}")
    
    print("\n=== 可视化功能测试完成 ===")

def test_utils():
    """测试工具类"""
    print("\n=== 测试工具类 ===")
    
    # 测试CrawlerUtils
    from utils.crawler_utils import CrawlerUtils
    
    print("\n1. 测试CrawlerUtils")
    try:
        crawler_utils = CrawlerUtils()
        
        # 测试获取随机User-Agent
        user_agent = crawler_utils.get_random_user_agent()
        print(f"随机User-Agent: {user_agent[:100]}...")
        
        # 测试获取请求头
        headers = crawler_utils.get_headers()
        print(f"请求头包含的键: {list(headers.keys())}")
        
        # 测试获取随机代理（如果配置了）
        proxy = crawler_utils.get_random_proxy()
        print(f"随机代理: {proxy if proxy else '未配置代理'}")
        
        print("CrawlerUtils测试完成")
    except Exception as e:
        print(f"CrawlerUtils测试失败: {e}")
    
    print("\n=== 工具类测试完成 ===")

def test_scheduler():
    """测试调度器功能"""
    print("\n=== 测试调度器功能 ===")
    
    from services.scheduler_service import SchedulerService
    
    try:
        scheduler = SchedulerService()
        
        # 测试启动调度器
        scheduler.start()
        print("调度器启动成功")
        
        # 测试添加简单任务
        def test_job():
            print("测试任务执行")
        
        # 添加间隔任务（1秒后执行，只执行一次）
        job_id = scheduler.add_interval_job(test_job, seconds=1, max_instances=1)
        print(f"添加测试任务，job_id: {job_id}")
        
        # 等待任务执行
        import time
        time.sleep(2)
        
        # 测试移除任务
        scheduler.remove_job(job_id)
        print("移除测试任务成功")
        
        # 测试关闭调度器
        scheduler.shutdown()
        print("调度器关闭成功")
        
        print("调度器测试完成")
    except Exception as e:
        print(f"调度器测试失败: {e}")
    
    print("\n=== 调度器功能测试完成 ===")

async def main():
    """测试主函数"""
    print("=== 电商价格监控系统核心功能测试 ===")
    
    # 测试爬虫功能
    await test_spiders()
    
    # 测试可视化功能
    test_visualization()
    
    # 测试工具类
    test_utils()
    
    # 测试调度器功能
    test_scheduler()
    
    print("\n=== 所有核心功能测试完成 ===")

if __name__ == "__main__":
    asyncio.run(main())
