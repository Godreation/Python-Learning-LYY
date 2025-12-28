import os
from datetime import datetime
from typing import Dict, List, Any
from database import DatabaseManager
from analysis import FinancialAnalysis
from transaction_manager import TransactionManager
import json

class ReportGenerator:
    def __init__(self, db_manager: DatabaseManager, transaction_manager: TransactionManager):
        self.db = db_manager
        self.transaction_manager = transaction_manager
        self.analysis = FinancialAnalysis(db_manager, transaction_manager)
    
    def generate_monthly_report(self, year: int, month: int, output_format: str = 'json') -> str:
        """生成月度财务报告"""
        # 获取月度数据
        monthly_summary = self.analysis.get_monthly_summary(year, month)
        category_analysis = self.analysis.get_category_analysis(
            f"{year}-{month:02d}-01",
            f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"
        )
        
        # 获取交易详情
        transactions = self.transaction_manager.get_transactions(
            f"{year}-{month:02d}-01",
            f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"
        )
        
        # 构建报告数据
        report_data = {
            'report_type': 'monthly',
            'period': f"{year}年{month}月",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_income': monthly_summary['income'],
                'total_expense': monthly_summary['expense'],
                'balance': monthly_summary['balance'],
                'savings_rate': monthly_summary['savings_rate'],
                'income_count': monthly_summary['income_count'],
                'expense_count': monthly_summary['expense_count']
            },
            'category_breakdown': {
                'income': monthly_summary['income_breakdown'],
                'expense': monthly_summary['expense_breakdown']
            },
            'top_transactions': {
                'largest_income': max([t for t in transactions if t['type'] == 'income'], 
                                    key=lambda x: x['amount'], default=None),
                'largest_expense': max([t for t in transactions if t['type'] == 'expense'], 
                                     key=lambda x: x['amount'], default=None)
            },
            'insights': self._generate_insights(monthly_summary, category_analysis)
        }
        
        # 根据格式生成输出
        if output_format.lower() == 'json':
            return self._generate_json_report(report_data)
        elif output_format.lower() == 'text':
            return self._generate_text_report(report_data)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def generate_annual_report(self, year: int, output_format: str = 'json') -> str:
        """生成年度财务报告"""
        # 获取年度数据
        monthly_data = []
        for month in range(1, 13):
            try:
                monthly_summary = self.analysis.get_monthly_summary(year, month)
                monthly_data.append({
                    'month': month,
                    'summary': monthly_summary
                })
            except:
                continue
        
        # 计算年度汇总
        total_income = sum(data['summary']['income'] for data in monthly_data)
        total_expense = sum(data['summary']['expense'] for data in monthly_data)
        
        # 构建报告数据
        report_data = {
            'report_type': 'annual',
            'period': f"{year}年",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': total_income - total_expense,
                'average_monthly_income': total_income / len(monthly_data) if monthly_data else 0,
                'average_monthly_expense': total_expense / len(monthly_data) if monthly_data else 0,
                'months_with_data': len(monthly_data)
            },
            'monthly_breakdown': monthly_data,
            'trend_analysis': self.analysis.get_trend_analysis(12),
            'financial_health': self.analysis.get_financial_health_score()
        }
        
        # 根据格式生成输出
        if output_format.lower() == 'json':
            return self._generate_json_report(report_data)
        elif output_format.lower() == 'text':
            return self._generate_text_report(report_data)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def _generate_json_report(self, report_data: Dict) -> str:
        """生成JSON格式报告"""
        # 创建报告目录
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_type = report_data['report_type']
        period = report_data['period'].replace('年', '').replace('月', '')
        
        filename = f"{report_type}_report_{period}_{timestamp}.json"
        filepath = os.path.join(reports_dir, filename)
        
        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _generate_text_report(self, report_data: Dict) -> str:
        """生成文本格式报告"""
        # 创建报告目录
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_type = report_data['report_type']
        period = report_data['period'].replace('年', '').replace('月', '')
        
        filename = f"{report_type}_report_{period}_{timestamp}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        # 生成文本内容
        text_content = self._format_text_report(report_data)
        
        # 保存文本文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return filepath
    
    def _format_text_report(self, report_data: Dict) -> str:
        """格式化文本报告"""
        lines = []
        
        # 报告标题
        lines.append("=" * 50)
        lines.append(f"财务报告 - {report_data['period']}")
        lines.append("=" * 50)
        lines.append(f"生成时间: {report_data['generated_at']}")
        lines.append("")
        
        # 汇总信息
        summary = report_data['summary']
        lines.append("【财务汇总】")
        lines.append(f"总收入: ¥{summary['total_income']:,.2f}")
        lines.append(f"总支出: ¥{summary['total_expense']:,.2f}")
        lines.append(f"结余: ¥{summary['balance']:,.2f}")
        
        if 'savings_rate' in summary:
            lines.append(f"储蓄率: {summary['savings_rate']:.1f}%")
        
        lines.append("")
        
        # 分类明细
        if 'category_breakdown' in report_data:
            lines.append("【分类明细】")
            
            # 收入分类
            lines.append("收入分类:")
            for category in report_data['category_breakdown']['income']:
                lines.append(f"  {category['category_name']}: ¥{category['total']:,.2f} ({category['count']}笔)")
            
            lines.append("")
            
            # 支出分类
            lines.append("支出分类:")
            for category in report_data['category_breakdown']['expense']:
                percentage = (category['total'] / summary['total_expense'] * 100) if summary['total_expense'] > 0 else 0
                lines.append(f"  {category['category_name']}: ¥{category['total']:,.2f} ({percentage:.1f}%)")
            
            lines.append("")
        
        # 趋势分析（年度报告）
        if 'trend_analysis' in report_data:
            lines.append("【趋势分析】")
            trend = report_data['trend_analysis']
            lines.append(f"收入趋势: {trend['income_trend']}")
            lines.append(f"支出趋势: {trend['expense_trend']}")
            lines.append(f"结余趋势: {trend['balance_trend']}")
            lines.append("")
        
        # 财务健康度（年度报告）
        if 'financial_health' in report_data:
            health = report_data['financial_health']
            lines.append("【财务健康度】")
            lines.append(f"综合评分: {health['score']}/100")
            lines.append(f"健康等级: {health['health_level']}")
            lines.append("")
            
            if health['recommendations']:
                lines.append("改进建议:")
                for rec in health['recommendations']:
                    lines.append(f"• {rec}")
                lines.append("")
        
        # 洞察分析
        if 'insights' in report_data:
            lines.append("【财务洞察】")
            for insight in report_data['insights']:
                lines.append(f"• {insight}")
            lines.append("")
        
        lines.append("=" * 50)
        lines.append("报告结束")
        lines.append("=" * 50)
        
        return '\n'.join(lines)
    
    def _generate_insights(self, monthly_summary: Dict, category_analysis: Dict) -> List[str]:
        """生成财务洞察"""
        insights = []
        
        # 储蓄率分析
        savings_rate = monthly_summary['savings_rate']
        if savings_rate > 30:
            insights.append("储蓄率优秀！继续保持良好的储蓄习惯")
        elif savings_rate > 20:
            insights.append("储蓄率良好，有进一步提升空间")
        elif savings_rate > 0:
            insights.append("储蓄率为正，但建议提高储蓄比例")
        else:
            insights.append("储蓄率为负，需要控制支出或增加收入")
        
        # 支出结构分析
        if category_analysis['categories']:
            top_category = category_analysis['categories'][0]
            if top_category['percentage'] > 40:
                insights.append(f"{top_category['category']}支出占比过高，建议优化支出结构")
        
        # 交易频率分析
        total_transactions = monthly_summary['income_count'] + monthly_summary['expense_count']
        if total_transactions > 100:
            insights.append("交易频率较高，建议合并小额交易")
        elif total_transactions < 10:
            insights.append("交易记录较少，建议更详细地记录收支")
        
        # 收入支出比
        if monthly_summary['income'] > 0:
            expense_ratio = (monthly_summary['expense'] / monthly_summary['income']) * 100
            if expense_ratio > 90:
                insights.append("支出收入比过高，财务压力较大")
            elif expense_ratio < 50:
                insights.append("支出控制良好，财务状况健康")
        
        return insights
    
    def export_report(self, report_type: str, period: str, output_format: str = 'json') -> str:
        """导出指定类型的报告"""
        if report_type == 'monthly':
            # 解析日期
            if '年' in period and '月' in period:
                year = int(period.split('年')[0])
                month = int(period.split('年')[1].replace('月', ''))
                return self.generate_monthly_report(year, month, output_format)
            else:
                raise ValueError("月度报告格式应为'2024年1月'")
        
        elif report_type == 'annual':
            # 解析年份
            if '年' in period:
                year = int(period.replace('年', ''))
                return self.generate_annual_report(year, output_format)
            else:
                raise ValueError("年度报告格式应为'2024年'")
        
        else:
            raise ValueError(f"不支持的报告类型: {report_type}")
    
    def get_available_reports(self) -> List[Dict]:
        """获取可用的报告列表"""
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return []
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith(('.json', '.txt')):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                
                reports.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created_time': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按创建时间排序
        reports.sort(key=lambda x: x['created_time'], reverse=True)
        return reports