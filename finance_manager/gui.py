import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from database import DatabaseManager
from transaction_manager import TransactionManager
from budget_manager import BudgetManager
from analysis import FinancialAnalysis
from import_export import ImportExportManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import calendar

class FinanceManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("个人财务管理系统")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.db = DatabaseManager()
        self.transaction_manager = TransactionManager(self.db)
        self.budget_manager = BudgetManager(self.db, self.transaction_manager)
        self.analysis = FinancialAnalysis(self.db, self.transaction_manager)
        self.import_export = ImportExportManager(self.db)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create navigation
        self.create_navigation()
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        self.content_frame.columnconfigure(0, weight=1)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_navigation(self):
        """Create navigation sidebar"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))
        
        # Navigation buttons
        buttons = [
            ("仪表盘", self.show_dashboard),
            ("交易记录", self.show_transactions),
            ("添加交易", self.show_add_transaction),
            ("预算管理", self.show_budgets),
            ("数据分析", self.show_analysis),
            ("导入导出", self.show_import_export),
            ("设置", self.show_settings)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, command=command, width=15)
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        nav_frame.columnconfigure(0, weight=1)
    
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard with overview"""
        self.clear_content()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Overview tab
        overview_frame = ttk.Frame(notebook, padding="10")
        notebook.add(overview_frame, text="概览")
        
        # Current month summary
        today = datetime.now()
        monthly_summary = self.analysis.get_monthly_summary(today.year, today.month)
        
        # Create summary cards
        summary_frame = ttk.Frame(overview_frame)
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        cards = [
            ("本月收入", f"¥{monthly_summary['income']:,.2f}", "green"),
            ("本月支出", f"¥{monthly_summary['expense']:,.2f}", "red"),
            ("本月结余", f"¥{monthly_summary['balance']:,.2f}", "blue"),
            ("储蓄率", f"{monthly_summary['savings_rate']:.1f}%", "orange")
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card = ttk.Frame(summary_frame, relief="solid", borderwidth=1)
            card.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E))
            card.columnconfigure(0, weight=1)
            
            ttk.Label(card, text=title, font=("Arial", 10, "bold")).grid(row=0, column=0, pady=5)
            ttk.Label(card, text=value, font=("Arial", 12, "bold"), foreground=color).grid(row=1, column=0, pady=5)
        
        summary_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Recent transactions
        recent_frame = ttk.LabelFrame(overview_frame, text="最近交易", padding="10")
        recent_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        recent_frame.columnconfigure(0, weight=1)
        
        transactions = self.transaction_manager.get_recent_transactions(7)
        
        # Create treeview for transactions
        columns = ("日期", "类型", "金额", "分类", "描述")
        tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("描述", width=200)
        
        for transaction in transactions:
            type_display = "收入" if transaction['type'] == 'income' else "支出"
            amount_color = "green" if transaction['type'] == 'income' else "red"
            amount_display = f"¥{transaction['amount']:,.2f}"
            
            tree.insert("", "end", values=(
                transaction['date'],
                type_display,
                amount_display,
                transaction['category_name'],
                transaction['description'][:50]  # Limit description length
            ))
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Budget alerts
        alerts_frame = ttk.LabelFrame(overview_frame, text="预算提醒", padding="10")
        alerts_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        alerts = self.budget_manager.get_budget_alerts()
        
        if alerts:
            for i, alert in enumerate(alerts):
                color = "red" if alert['severity'] == 'high' else "orange"
                ttk.Label(alerts_frame, text=alert['message'], foreground=color).grid(
                    row=i, column=0, sticky=tk.W, pady=2)
        else:
            ttk.Label(alerts_frame, text="暂无预算提醒", foreground="gray").grid(row=0, column=0)
        
        # Financial health score
        health_frame = ttk.LabelFrame(overview_frame, text="财务健康度", padding="10")
        health_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        health_score = self.analysis.get_financial_health_score()
        
        # Create health score display
        score_color = self.get_health_score_color(health_score['score'])
        
        ttk.Label(health_frame, text=f"综合评分: {health_score['score']}/100", 
                 font=("Arial", 14, "bold"), foreground=score_color).grid(row=0, column=0)
        ttk.Label(health_frame, text=f"健康等级: {health_score['health_level']}").grid(row=1, column=0)
        
        # Recommendations
        if health_score['recommendations']:
            ttk.Label(health_frame, text="改进建议:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
            for i, rec in enumerate(health_score['recommendations']):
                ttk.Label(health_frame, text=f"• {rec}").grid(row=3+i, column=0, sticky=tk.W)
    
    def get_health_score_color(self, score):
        """Get color based on health score"""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "orange"
        else:
            return "red"
    
    def show_transactions(self):
        """Show transactions management interface"""
        self.clear_content()
        
        # Create filter frame
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Date filter
        ttk.Label(filter_frame, text="开始日期:").grid(row=0, column=0, padx=5)
        start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        start_entry = ttk.Entry(filter_frame, textvariable=start_date_var, width=12)
        start_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="结束日期:").grid(row=0, column=2, padx=5)
        end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        end_entry = ttk.Entry(filter_frame, textvariable=end_date_var, width=12)
        end_entry.grid(row=0, column=3, padx=5)
        
        # Type filter
        ttk.Label(filter_frame, text="类型:").grid(row=0, column=4, padx=5)
        type_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(filter_frame, textvariable=type_var, values=["全部", "收入", "支出"], width=8)
        type_combo.grid(row=0, column=5, padx=5)
        
        # Search
        ttk.Label(filter_frame, text="搜索:").grid(row=0, column=6, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=15)
        search_entry.grid(row=0, column=7, padx=5)
        
        # Filter button
        filter_btn = ttk.Button(filter_frame, text="筛选", command=lambda: self.filter_transactions(
            start_date_var.get(), end_date_var.get(), type_var.get(), search_var.get()))
        filter_btn.grid(row=0, column=8, padx=5)
        
        # Transactions table
        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        columns = ("ID", "日期", "类型", "金额", "分类", "描述", "操作")
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=80)
        
        self.transactions_tree.column("描述", width=150)
        self.transactions_tree.column("操作", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transactions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load initial transactions
        self.load_transactions()
    
    def load_transactions(self, start_date=None, end_date=None, transaction_type=None, search_term=None):
        """Load transactions into the treeview"""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get transactions
        if search_term:
            transactions = self.transaction_manager.search_transactions(search_term)
        else:
            transactions = self.transaction_manager.get_transactions(start_date, end_date)
        
        # Filter by type if specified
        if transaction_type and transaction_type != "全部":
            type_filter = 'income' if transaction_type == "收入" else 'expense'
            transactions = [t for t in transactions if t['type'] == type_filter]
        
        # Add to treeview
        for transaction in transactions:
            type_display = "收入" if transaction['type'] == 'income' else "支出"
            amount_color = "green" if transaction['type'] == 'income' else "red"
            amount_display = f"¥{transaction['amount']:,.2f}"
            
            self.transactions_tree.insert("", "end", values=(
                transaction['id'],
                transaction['date'],
                type_display,
                amount_display,
                transaction['category_name'],
                transaction['description'],
                "编辑 | 删除"
            ))
    
    def filter_transactions(self, start_date, end_date, transaction_type, search_term):
        """Apply filters to transactions"""
        self.load_transactions(start_date, end_date, transaction_type, search_term)
    
    def show_add_transaction(self):
        """Show add transaction form"""
        self.clear_content()
        
        form_frame = ttk.LabelFrame(self.content_frame, text="添加交易", padding="20")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=100, pady=50)
        form_frame.columnconfigure(1, weight=1)
        
        # Form fields
        fields = [
            ("金额*", "amount_entry"),
            ("类型*", "type_combo"),
            ("分类", "category_combo"),
            ("描述*", "desc_entry"),
            ("日期", "date_entry")
        ]
        
        self.form_vars = {}
        
        for i, (label, field_name) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if field_name == "type_combo":
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, values=["收入", "支出"], state="readonly")
                combo.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.form_vars[field_name] = var
            elif field_name == "category_combo":
                var = tk.StringVar()
                categories = self.db.get_categories()
                category_names = [cat['name'] for cat in categories]
                combo = ttk.Combobox(form_frame, textvariable=var, values=category_names)
                combo.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.form_vars[field_name] = var
            else:
                var = tk.StringVar()
                if field_name == "date_entry":
                    var.set(datetime.now().strftime('%Y-%m-%d'))
                entry = ttk.Entry(form_frame, textvariable=var)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.form_vars[field_name] = var
        
        # Submit button
        submit_btn = ttk.Button(form_frame, text="添加交易", command=self.submit_transaction)
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def submit_transaction(self):
        """Submit new transaction"""
        try:
            # Validate required fields
            amount = float(self.form_vars["amount_entry"].get())
            transaction_type = "income" if self.form_vars["type_combo"].get() == "收入" else "expense"
            description = self.form_vars["desc_entry"].get()
            
            if not amount or not transaction_type or not description:
                messagebox.showerror("错误", "请填写所有必填字段（标记*）")
                return
            
            # Get category ID
            category_name = self.form_vars["category_combo"].get()
            category_id = None
            if category_name:
                categories = self.db.get_categories()
                for cat in categories:
                    if cat['name'] == category_name:
                        category_id = cat['id']
                        break
            
            # Get date
            date_str = self.form_vars["date_entry"].get() or datetime.now().strftime('%Y-%m-%d')
            
            # Add transaction
            self.transaction_manager.add_transaction(amount, transaction_type, category_id, description, date_str)
            
            messagebox.showinfo("成功", "交易添加成功！")
            
            # Clear form
            for var in self.form_vars.values():
                if hasattr(var, 'set'):
                    var.set("")
            self.form_vars["date_entry"].set(datetime.now().strftime('%Y-%m-%d'))
            
        except ValueError as e:
            messagebox.showerror("错误", f"数据格式错误: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"添加交易失败: {e}")
    
    def show_budgets(self):
        """Show budget management interface"""
        self.clear_content()
        
        # This would implement the budget management interface
        ttk.Label(self.content_frame, text="预算管理功能开发中...").grid(row=0, column=0, pady=50)
    
    def show_analysis(self):
        """Show financial analysis interface"""
        self.clear_content()
        
        # This would implement the analysis interface
        ttk.Label(self.content_frame, text="数据分析功能开发中...").grid(row=0, column=0, pady=50)
    
    def show_import_export(self):
        """Show import/export interface"""
        self.clear_content()
        
        # This would implement the import/export interface
        ttk.Label(self.content_frame, text="导入导出功能开发中...").grid(row=0, column=0, pady=50)
    
    def show_settings(self):
        """Show settings interface"""
        self.clear_content()
        
        # This would implement the settings interface
        ttk.Label(self.content_frame, text="系统设置功能开发中...").grid(row=0, column=0, pady=50)

def main():
    root = tk.Tk()
    app = FinanceManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()