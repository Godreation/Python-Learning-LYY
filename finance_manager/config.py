"""
配置文件 - 个人财务管理系统
"""

import os
from datetime import datetime

# 数据库配置
DATABASE_CONFIG = {
    'db_path': 'finance.db',
    'backup_dir': 'backups',
    'auto_backup': True,
    'backup_interval_days': 7
}

# 应用配置
APP_CONFIG = {
    'name': '个人财务管理系统',
    'version': '1.0.0',
    'author': 'Finance Manager Team',
    'default_currency': 'CNY',
    'date_format': '%Y-%m-%d',
    'decimal_places': 2
}

# 界面配置
UI_CONFIG = {
    'theme': 'default',
    'font_family': 'Microsoft YaHei',
    'font_size': 10,
    'window_width': 1200,
    'window_height': 800
}

# 分析配置
ANALYSIS_CONFIG = {
    'default_analysis_months': 12,
    'anomaly_threshold': 2.0,  # 异常检测阈值（标准差倍数）
    'health_score_weights': {
        'savings_rate': 0.30,
        'expense_consistency': 0.25,
        'income_stability': 0.20,
        'debt_management': 0.15,
        'emergency_fund': 0.10
    }
}

# 预算配置
BUDGET_CONFIG = {
    'alert_threshold': 0.8,  # 预算使用率达到80%时提醒
    'default_period': 'monthly',
    'auto_suggest': True
}

# 导入导出配置
IMPORT_EXPORT_CONFIG = {
    'supported_formats': ['csv', 'xlsx', 'json'],
    'max_file_size_mb': 10,
    'default_export_columns': [
        'date', 'type', 'amount', 'category', 'description', 'tags'
    ]
}

# 自动分类配置
AUTO_CATEGORIZATION_CONFIG = {
    'enabled': True,
    'default_rules': {
        '工资收入': ['工资', '薪水', '薪资', '奖金', '绩效'],
        '投资收入': ['利息', '分红', '投资', '股票', '基金'],
        '食品餐饮': ['餐厅', '外卖', '超市', '买菜', '食品', '餐饮', '吃饭'],
        '交通出行': ['打车', '公交', '地铁', '火车', '机票', '汽油', '停车'],
        '住房租金': ['房租', '房贷', '水电', '物业', '维修'],
        '娱乐休闲': ['电影', '游戏', '旅游', '健身', '娱乐', '休闲'],
        '医疗健康': ['医院', '药品', '体检', '医生', '医疗'],
        '教育培训': ['学费', '书籍', '课程', '培训', '教育'],
        '购物消费': ['购物', '衣服', '电器', '网购', '消费']
    }
}

def get_backup_path():
    """生成备份文件路径"""
    backup_dir = DATABASE_CONFIG['backup_dir']
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(backup_dir, f'finance_backup_{timestamp}.db')

def should_auto_backup():
    """检查是否应该进行自动备份"""
    if not DATABASE_CONFIG['auto_backup']:
        return False
    
    backup_dir = DATABASE_CONFIG['backup_dir']
    if not os.path.exists(backup_dir):
        return True
    
    # 检查最近的备份文件
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith('finance_backup_')]
    if not backup_files:
        return True
    
    # 获取最新的备份文件
    latest_backup = max(backup_files)
    backup_path = os.path.join(backup_dir, latest_backup)
    
    # 检查备份时间
    backup_time = datetime.fromtimestamp(os.path.getctime(backup_path))
    days_since_backup = (datetime.now() - backup_time).days
    
    return days_since_backup >= DATABASE_CONFIG['backup_interval_days']