import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

print(f"Python版本: {sys.version}")
print(f"Pandas版本: {pd.__version__}")
print(f"Matplotlib版本: {plt.__version__}")
print(f"Seaborn版本: {sns.__version__}")
print(f"当前工作目录: {os.getcwd()}")

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

print(f"\n测试数据创建完成，共 {len(df)} 条记录")
print(f"价格范围: {df['price'].min():.2f} - {df['price'].max():.2f} 元")
print(f"前5条数据:")
print(df.head())

# 手动测试Matplotlib是否能正常工作
print(f"\n=== 手动测试Matplotlib ===")
try:
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建简单图表
    plt.figure(figsize=(10, 5))
    plt.plot(df['crawl_time'], df['price'], label='价格')
    plt.title('测试商品 价格趋势')
    plt.xlabel('日期')
    plt.ylabel('价格 (元)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图表
    test_chart_path = 'reports/debug_test_chart.png'
    plt.savefig(test_chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    if os.path.exists(test_chart_path):
        file_size = os.path.getsize(test_chart_path)
        print(f"✅ 手动测试图表生成成功: {test_chart_path}")
        print(f"   文件大小: {file_size / 1024:.2f} KB")
    else:
        print(f"❌ 手动测试图表生成失败")
except Exception as e:
    print(f"❌ Matplotlib测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试Seaborn是否能正常工作
print(f"\n=== 手动测试Seaborn ===")
try:
    plt.figure(figsize=(10, 5))
    sns.lineplot(x='crawl_time', y='price', data=df, label='价格', linewidth=2)
    plt.title('测试商品 价格趋势 (Seaborn)')
    plt.xlabel('日期')
    plt.ylabel('价格 (元)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图表
    seaborn_test_path = 'reports/debug_seaborn_test.png'
    plt.savefig(seaborn_test_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    if os.path.exists(seaborn_test_path):
        file_size = os.path.getsize(seaborn_test_path)
        print(f"✅ Seaborn测试图表生成成功: {seaborn_test_path}")
        print(f"   文件大小: {file_size / 1024:.2f} KB")
    else:
        print(f"❌ Seaborn测试图表生成失败")
except Exception as e:
    print(f"❌ Seaborn测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试可视化服务
print(f"\n=== 测试可视化服务 ===")
try:
    from services.visualization_service import VisualizationService
    
    viz_service = VisualizationService()
    print(f"✅ 可视化服务实例化成功")
    
    # 生成价格趋势图，不清理文件
    chart_path = viz_service.generate_price_trend_chart(df, "测试商品", days=30)
    print(f"生成的图表路径: {chart_path}")
    
    if chart_path and os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"✅ 价格趋势图生成成功: {chart_path}")
        print(f"   文件大小: {file_size / 1024:.2f} KB")
    else:
        print(f"❌ 价格趋势图生成失败")
except Exception as e:
    print(f"❌ 可视化服务测试失败: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== 测试完成，查看reports目录 ===")
# 查看reports目录内容
files = os.listdir('reports')
print(f"reports目录中的文件 ({len(files)} 个):")
for file in files:
    file_path = os.path.join('reports', file)
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        print(f"  - {file}: {file_size / 1024:.2f} KB")
    else:
        print(f"  - {file}/ (目录)")
