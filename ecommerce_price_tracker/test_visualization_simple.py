import pandas as pd
from datetime import datetime, timedelta
from services.visualization_service import VisualizationService
import os

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
        print(f"✅ 价格趋势图生成成功: {chart_path}")
        # 显示文件大小
        file_size = os.path.getsize(chart_path)
        print(f"   文件大小: {file_size / 1024:.2f} KB")
        # 清理生成的文件
        os.remove(chart_path)
        print(f"   文件已清理")
    else:
        print("❌ 价格趋势图生成失败")
except Exception as e:
    print(f"❌ 生成价格趋势图失败: {e}")

# 测试生成价格分布直方图
print("\n2. 测试生成价格分布直方图")
try:
    chart_path = viz_service.generate_price_distribution_chart(df, "测试商品")
    if chart_path and os.path.exists(chart_path):
        print(f"✅ 价格分布直方图生成成功: {chart_path}")
        # 显示文件大小
        file_size = os.path.getsize(chart_path)
        print(f"   文件大小: {file_size / 1024:.2f} KB")
        # 清理生成的文件
        os.remove(chart_path)
        print(f"   文件已清理")
    else:
        print("❌ 价格分布直方图生成失败")
except Exception as e:
    print(f"❌ 生成价格分布直方图失败: {e}")

# 测试生成价格统计摘要
print("\n3. 测试生成价格统计摘要")
try:
    summary_path = viz_service.generate_summary_statistics(df, "测试商品")
    if summary_path and os.path.exists(summary_path):
        print(f"✅ 价格统计摘要生成成功: {summary_path}")
        # 显示摘要内容
        print("   摘要内容:")
        with open(summary_path, 'r', encoding='utf-8') as f:
            print(f.read())
        # 清理生成的文件
        os.remove(summary_path)
        print(f"   文件已清理")
    else:
        print("❌ 价格统计摘要生成失败")
except Exception as e:
    print(f"❌ 生成价格统计摘要失败: {e}")

print("\n🎉 所有测试完成!")
