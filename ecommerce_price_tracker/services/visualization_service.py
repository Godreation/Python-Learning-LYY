import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List

class VisualizationService:
    def __init__(self):
        # 设置中文字体，避免中文显示问题
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建reports目录（如果不存在）
        self.reports_dir = 'reports'
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_price_trend_chart(self, df: pd.DataFrame, product_name: str, days: int = 30) -> str:
        """生成单个商品价格趋势图"""
        if df.empty:
            return ""
        
        # 确保crawl_time是datetime类型
        df['crawl_time'] = pd.to_datetime(df['crawl_time'])
        
        # 设置图表大小
        plt.figure(figsize=(12, 6))
        
        # 绘制价格趋势
        sns.lineplot(x='crawl_time', y='price', data=df, label='价格', linewidth=2)
        
        # 绘制7天移动平均线
        if len(df) >= 7:
            df['price_ma7'] = df['price'].rolling(window=7).mean()
            sns.lineplot(x='crawl_time', y='price_ma7', data=df, label='7天均线', linestyle='--', linewidth=1.5)
        
        # 设置图表标题和标签
        plt.title(f'{product_name} 价格趋势 ({days}天)', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格 (元)', fontsize=12)
        
        # 添加网格线
        plt.grid(True, alpha=0.3)
        
        # 添加图例
        plt.legend(fontsize=10)
        
        # 自动旋转x轴标签
        plt.xticks(rotation=45)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        filename = f'{product_name.replace(" ", "_")}_price_trend_{days}d_{datetime.now().strftime("%Y%m%d")}.png'
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_price_comparison_chart(self, products_data: Dict[str, pd.DataFrame], days: int = 30) -> str:
        """生成多个商品价格对比图"""
        if not products_data:
            return ""
        
        # 设置图表大小
        plt.figure(figsize=(14, 7))
        
        # 绘制每个商品的价格趋势
        for product_name, df in products_data.items():
            if not df.empty:
                df['crawl_time'] = pd.to_datetime(df['crawl_time'])
                sns.lineplot(x='crawl_time', y='price', data=df, label=product_name, linewidth=2)
        
        # 设置图表标题和标签
        plt.title(f'商品价格对比 ({days}天)', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格 (元)', fontsize=12)
        
        # 添加网格线
        plt.grid(True, alpha=0.3)
        
        # 添加图例
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 自动旋转x轴标签
        plt.xticks(rotation=45)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        filename = f'price_comparison_{days}d_{datetime.now().strftime("%Y%m%d")}.png'
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_price_distribution_chart(self, df: pd.DataFrame, product_name: str) -> str:
        """生成价格分布直方图"""
        if df.empty:
            return ""
        
        # 设置图表大小
        plt.figure(figsize=(10, 6))
        
        # 绘制价格分布直方图
        sns.histplot(df['price'], kde=True, bins=20, color='skyblue')
        
        # 设置图表标题和标签
        plt.title(f'{product_name} 价格分布', fontsize=16)
        plt.xlabel('价格 (元)', fontsize=12)
        plt.ylabel('频率', fontsize=12)
        
        # 添加网格线
        plt.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        filename = f'{product_name.replace(" ", "_")}_price_distribution_{datetime.now().strftime("%Y%m%d")}.png'
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_platform_comparison_chart(self, df: pd.DataFrame) -> str:
        """生成不同平台价格对比图"""
        if df.empty:
            return ""
        
        # 设置图表大小
        plt.figure(figsize=(12, 6))
        
        # 绘制平台价格对比箱线图
        sns.boxplot(x='platform', y='latest_price', data=df)
        
        # 添加散点图显示实际数据点
        sns.swarmplot(x='platform', y='latest_price', data=df, color='black', alpha=0.5)
        
        # 设置图表标题和标签
        plt.title('不同平台商品价格对比', fontsize=16)
        plt.xlabel('平台', fontsize=12)
        plt.ylabel('价格 (元)', fontsize=12)
        
        # 添加网格线
        plt.grid(True, alpha=0.3, axis='y')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        filename = f'platform_price_comparison_{datetime.now().strftime("%Y%m%d")}.png'
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_daily_price_change_chart(self, df: pd.DataFrame, product_name: str) -> str:
        """生成每日价格变化率图表"""
        if df.empty or len(df) < 2:
            return ""
        
        # 确保crawl_time是datetime类型并排序
        df['crawl_time'] = pd.to_datetime(df['crawl_time'])
        df = df.sort_values('crawl_time')
        
        # 计算每日价格变化率
        df['price_change'] = df['price'].pct_change() * 100
        
        # 设置图表大小
        plt.figure(figsize=(12, 6))
        
        # 绘制价格变化率柱状图
        sns.barplot(x='crawl_time', y='price_change', data=df, color='skyblue')
        
        # 添加水平线表示0变化
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # 设置图表标题和标签
        plt.title(f'{product_name} 每日价格变化率', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格变化率 (%)', fontsize=12)
        
        # 添加网格线
        plt.grid(True, alpha=0.3, axis='y')
        
        # 自动旋转x轴标签
        plt.xticks(rotation=45)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        filename = f'{product_name.replace(" ", "_")}_daily_price_change_{datetime.now().strftime("%Y%m%d")}.png'
        filepath = os.path.join(self.reports_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_all_products_report(self, products_df: pd.DataFrame, products_history: Dict[int, pd.DataFrame]) -> None:
        """生成所有商品的综合报告"""
        # 1. 平台价格对比图
        self.generate_platform_comparison_chart(products_df)
        
        # 2. 为每个商品生成价格趋势图和分布直方图
        for _, product in products_df.iterrows():
            product_id = product['id']
            product_name = product['name']
            
            if product_id in products_history and not products_history[product_id].empty:
                # 生成30天价格趋势图
                self.generate_price_trend_chart(products_history[product_id], product_name, days=30)
                
                # 生成价格分布直方图
                self.generate_price_distribution_chart(products_history[product_id], product_name)
                
                # 生成每日价格变化率图表
                self.generate_daily_price_change_chart(products_history[product_id], product_name)
    
    def generate_summary_statistics(self, df: pd.DataFrame, product_name: str) -> str:
        """生成价格统计摘要"""
        if df.empty:
            return ""
        
        # 计算统计信息
        stats = df['price'].describe()
        
        # 创建摘要文本
        summary = f"商品: {product_name}\n"
        summary += f"\n价格统计摘要:\n"
        summary += f"样本数量: {int(stats['count'])}\n"
        summary += f"平均价格: {stats['mean']:.2f} 元\n"
        summary += f"最低价格: {stats['min']:.2f} 元\n"
        summary += f"最高价格: {stats['max']:.2f} 元\n"
        summary += f"价格中位数: {df['price'].median():.2f} 元\n"
        summary += f"价格标准差: {stats['std']:.2f} 元\n"
        
        # 保存摘要到文件
        filename = f'{product_name.replace(" ", "_")}_price_summary_{datetime.now().strftime("%Y%m%d")}.txt'
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return filepath
