#!/usr/bin/env python3
"""
系统功能测试脚本
"""

import sys
import os
from datetime import datetime, timedelta

def test_database():
    """测试数据库功能"""
    print("=== 测试数据库功能 ===")
    
    try:
        from database import DatabaseManager
        
        # 创建数据库管理器
        db = DatabaseManager("test_finance.db")
        
        # 测试获取分类
        categories = db.get_categories()
        print(f"✓ 成功加载 {len(categories)} 个分类")
        
        # 测试获取标签
        tags = db.get_tags()
        print(f"✓ 成功加载 {len(tags)} 个标签")
        
        # 测试添加交易
        transaction_id = db.add_transaction(
            amount=100.50,
            transaction_type="expense",
            category_id=4,  # 食品餐饮
            description="测试午餐",
            date="2024-01-15"
        )
        print(f"✓ 成功添加交易，ID: {transaction_id}")
        
        # 测试查询交易
        transactions = db.get_transactions()
        print(f"✓ 成功查询到 {len(transactions)} 笔交易")
        
        # 测试月度汇总
        summary = db.get_monthly_summary(2024, 1)
        print(f"✓ 月度汇总测试完成")
        
        # 清理测试数据库
        if os.path.exists("test_finance.db"):
            os.remove("test_finance.db")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False

def test_transaction_manager():
    """测试交易管理功能"""
    print("\n=== 测试交易管理功能 ===")
    
    try:
        from database import DatabaseManager
        from transaction_manager import TransactionManager
        
        db = DatabaseManager("test_finance.db")
        tm = TransactionManager(db)
        
        # 测试添加交易
        transaction = tm.add_transaction(
            amount=200.00,
            transaction_type="income",
            category_id=1,  # 工资收入
            description="测试工资"
        )
        print(f"✓ 成功添加交易: {transaction}")
        
        # 测试自动分类
        auto_category_id = tm.auto_categorize("公司发放工资")
        print(f"✓ 自动分类测试: '公司发放工资' -> 分类ID {auto_category_id}")
        
        # 测试查询交易
        transactions = tm.get_transactions(limit=5)
        print(f"✓ 成功查询到 {len(transactions)} 笔交易")
        
        # 测试搜索功能
        search_results = tm.search_transactions("测试")
        print(f"✓ 搜索功能测试: 找到 {len(search_results)} 条结果")
        
        # 测试统计功能
        stats = tm.get_statistics("2024-01-01", "2024-01-31")
        print(f"✓ 统计功能测试完成")
        
        # 清理测试数据库
        if os.path.exists("test_finance.db"):
            os.remove("test_finance.db")
        
        return True
        
    except Exception as e:
        print(f"✗ 交易管理测试失败: {e}")
        return False

def test_budget_manager():
    """测试预算管理功能"""
    print("\n=== 测试预算管理功能 ===")
    
    try:
        from database import DatabaseManager
        from transaction_manager import TransactionManager
        from budget_manager import BudgetManager
        
        db = DatabaseManager("test_finance.db")
        tm = TransactionManager(db)
        bm = BudgetManager(db, tm)
        
        # 测试创建预算
        budget = bm.create_budget(
            category_id=4,  # 食品餐饮
            amount=1000.00,
            period="monthly",
            start_date="2024-01-01"
        )
        print(f"✓ 成功创建预算: {budget}")
        
        # 测试获取预算
        budgets = bm.get_all_budgets()
        print(f"✓ 成功获取 {len(budgets)} 个预算")
        
        # 测试预算进度计算
        if budgets:
            progress = bm.calculate_budget_progress(budgets[0])
            print(f"✓ 预算进度计算测试完成")
        
        # 测试预算建议
        suggestion = bm.suggest_budget(4)  # 食品餐饮
        print(f"✓ 预算建议功能测试完成")
        
        # 清理测试数据库
        if os.path.exists("test_finance.db"):
            os.remove("test_finance.db")
        
        return True
        
    except Exception as e:
        print(f"✗ 预算管理测试失败: {e}")
        return False

def test_analysis():
    """测试数据分析功能"""
    print("\n=== 测试数据分析功能 ===")
    
    try:
        from database import DatabaseManager
        from transaction_manager import TransactionManager
        from analysis import FinancialAnalysis
        
        db = DatabaseManager("test_finance.db")
        tm = TransactionManager(db)
        analysis = FinancialAnalysis(db, tm)
        
        # 添加测试数据
        test_transactions = [
            (5000.00, "income", 1, "工资", "2024-01-05"),
            (300.00, "expense", 4, "午餐", "2024-01-10"),
            (200.00, "expense", 5, "交通", "2024-01-15"),
            (1000.00, "expense", 6, "房租", "2024-01-20")
        ]
        
        for amount, t_type, cat_id, desc, date in test_transactions:
            tm.add_transaction(amount, t_type, cat_id, desc, date)
        
        # 测试月度汇总
        monthly_summary = analysis.get_monthly_summary(2024, 1)
        print(f"✓ 月度汇总测试: 收入{monthly_summary['income']}, 支出{monthly_summary['expense']}")
        
        # 测试趋势分析
        trends = analysis.get_trend_analysis(3)
        print(f"✓ 趋势分析测试完成")
        
        # 测试分类分析
        category_analysis = analysis.get_category_analysis("2024-01-01", "2024-01-31")
        print(f"✓ 分类分析测试: {len(category_analysis['categories'])} 个分类")
        
        # 测试财务健康评分
        health_score = analysis.get_financial_health_score()
        print(f"✓ 财务健康评分: {health_score['score']}")
        
        # 清理测试数据库
        if os.path.exists("test_finance.db"):
            os.remove("test_finance.db")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据分析测试失败: {e}")
        return False

def test_import_export():
    """测试导入导出功能"""
    print("\n=== 测试导入导出功能 ===")
    
    try:
        from database import DatabaseManager
        from import_export import ImportExportManager
        
        db = DatabaseManager("test_finance.db")
        ie = ImportExportManager(db)
        
        # 测试导出格式
        formats = ie.get_export_formats()
        print(f"✓ 支持 {len(formats)} 种导出格式")
        
        # 测试导入格式
        import_formats = ie.get_import_formats()
        print(f"✓ 支持 {len(import_formats)} 种导入格式")
        
        # 测试备份功能
        backup_success = ie.backup_database("test_backup.db")
        print(f"✓ 数据库备份测试: {'成功' if backup_success else '失败'}")
        
        # 清理测试文件
        for file in ["test_finance.db", "test_backup.db"]:
            if os.path.exists(file):
                os.remove(file)
        
        return True
        
    except Exception as e:
        print(f"✗ 导入导出测试失败: {e}")
        return False

def test_report_generator():
    """测试报表生成功能"""
    print("\n=== 测试报表生成功能 ===")
    
    try:
        from database import DatabaseManager
        from transaction_manager import TransactionManager
        from report_generator import ReportGenerator
        
        db = DatabaseManager("test_finance.db")
        tm = TransactionManager(db)
        rg = ReportGenerator(db, tm)
        
        # 添加测试数据
        test_transactions = [
            (8000.00, "income", 1, "十二月工资", "2024-12-05"),
            (500.00, "expense", 4, "圣诞大餐", "2024-12-24"),
            (300.00, "expense", 9, "新年礼物", "2024-12-28")
        ]
        
        for amount, t_type, cat_id, desc, date in test_transactions:
            tm.add_transaction(amount, t_type, cat_id, desc, date)
        
        # 测试月度报告
        monthly_report = rg.generate_monthly_report(2024, 12, "text")
        print(f"✓ 月度报告生成: {monthly_report}")
        
        # 测试报告列表
        reports = rg.get_available_reports()
        print(f"✓ 可用报告数量: {len(reports)}")
        
        # 清理测试文件
        if os.path.exists("test_finance.db"):
            os.remove("test_finance.db")
        
        # 清理报告目录
        import shutil
        if os.path.exists("reports"):
            shutil.rmtree("reports")
        
        return True
        
    except Exception as e:
        print(f"✗ 报表生成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试个人财务管理系统...")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_database,
        test_transaction_manager,
        test_budget_manager,
        test_analysis,
        test_import_export,
        test_report_generator
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"测试函数 {test_func.__name__} 执行异常: {e}")
            results.append(False)
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)