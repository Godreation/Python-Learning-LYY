import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                color TEXT DEFAULT '#3498db',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category_id INTEGER,
                description TEXT,
                date DATE NOT NULL,
                tags TEXT,  -- JSON array of tag IDs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL NOT NULL,
                period TEXT NOT NULL CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly')),
                start_date DATE NOT NULL,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Auto-categorization rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorization_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Insert default categories
        default_categories = [
            ('工资收入', 'income', '#27ae60'),
            ('投资收入', 'income', '#f39c12'),
            ('其他收入', 'income', '#95a5a6'),
            ('食品餐饮', 'expense', '#e74c3c'),
            ('交通出行', 'expense', '#3498db'),
            ('住房租金', 'expense', '#9b59b6'),
            ('娱乐休闲', 'expense', '#f1c40f'),
            ('医疗健康', 'expense', '#e67e22'),
            ('教育培训', 'expense', '#1abc9c'),
            ('购物消费', 'expense', '#d35400'),
            ('其他支出', 'expense', '#7f8c8d')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO categories (name, type, color) 
            VALUES (?, ?, ?)
        """, default_categories)
        
        # Insert default tags
        default_tags = [
            ('必需品',),
            ('奢侈品',),
            ('紧急',),
            ('计划外',),
            ('定期',),
            ('一次性',)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO tags (name) 
            VALUES (?)
        """, default_tags)
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        
        conn.close()
        return result
    
    def get_categories(self, category_type: Optional[str] = None) -> List[Dict]:
        """Get all categories, optionally filtered by type"""
        if category_type:
            query = "SELECT * FROM categories WHERE type = ? ORDER BY name"
            results = self.execute_query(query, (category_type,))
        else:
            query = "SELECT * FROM categories ORDER BY type, name"
            results = self.execute_query(query)
        
        return [dict(zip(['id', 'name', 'type', 'color', 'created_at'], row)) 
                for row in results]
    
    def get_tags(self) -> List[Dict]:
        """Get all tags"""
        query = "SELECT * FROM tags ORDER BY name"
        results = self.execute_query(query)
        return [dict(zip(['id', 'name', 'created_at'], row)) for row in results]
    
    def add_transaction(self, amount: float, transaction_type: str, 
                       category_id: int, description: str, date: str, 
                       tags: List[int] = None) -> int:
        """Add a new transaction"""
        tags_json = '[]' if not tags else f'[{','.join(map(str, tags))}]'
        
        query = """
            INSERT INTO transactions (amount, type, category_id, description, date, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        return self.execute_query(query, (amount, transaction_type, category_id, 
                                         description, date, tags_json))
    
    def get_transactions(self, start_date: str = None, end_date: str = None, 
                        category_id: int = None) -> List[Dict]:
        """Get transactions with optional filters"""
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date)
        
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY t.date DESC, t.created_at DESC"
        
        results = self.execute_query(query, tuple(params))
        
        transactions = []
        for row in results:
            transaction = dict(zip(['id', 'amount', 'type', 'category_id', 
                                  'description', 'date', 'tags', 'created_at',
                                  'category_name', 'category_color'], row))
            
            # Parse tags JSON
            if transaction['tags']:
                transaction['tags'] = eval(transaction['tags'])
            else:
                transaction['tags'] = []
            
            transactions.append(transaction)
        
        return transactions
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get monthly income/expense summary"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        query = """
            SELECT 
                type,
                SUM(amount) as total,
                COUNT(*) as count
            FROM transactions 
            WHERE date >= ? AND date < ?
            GROUP BY type
        """
        
        results = self.execute_query(query, (start_date, end_date))
        
        summary = {'income': 0, 'expense': 0, 'income_count': 0, 'expense_count': 0}
        for row in results:
            transaction_type, total, count = row
            summary[transaction_type] = total
            summary[f'{transaction_type}_count'] = count
        
        summary['balance'] = summary['income'] - summary['expense']
        
        return summary
    
    def get_category_breakdown(self, year: int, month: int, transaction_type: str) -> List[Dict]:
        """Get breakdown by category for a specific month"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        query = """
            SELECT 
                c.name as category_name,
                c.color as category_color,
                SUM(t.amount) as total,
                COUNT(*) as count
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date >= ? AND t.date < ? AND t.type = ?
            GROUP BY c.id, c.name, c.color
            ORDER BY total DESC
        """
        
        results = self.execute_query(query, (start_date, end_date, transaction_type))
        
        return [dict(zip(['category_name', 'category_color', 'total', 'count'], row)) 
                for row in results]
    
    def add_budget(self, category_id: int, amount: float, period: str, 
                   start_date: str, end_date: str = None) -> int:
        """Add a new budget"""
        query = """
            INSERT INTO budgets (category_id, amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """
        
        return self.execute_query(query, (category_id, amount, period, start_date, end_date))
    
    def get_budgets(self) -> List[Dict]:
        """Get all budgets"""
        query = """
            SELECT b.*, c.name as category_name, c.type as category_type
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            ORDER BY b.start_date DESC
        """
        
        results = self.execute_query(query)
        return [dict(zip(['id', 'category_id', 'amount', 'period', 'start_date', 
                         'end_date', 'created_at', 'category_name', 'category_type'], row)) 
                for row in results]
    
    def add_categorization_rule(self, keyword: str, category_id: int, priority: int = 1) -> int:
        """Add a new categorization rule"""
        query = """
            INSERT INTO categorization_rules (keyword, category_id, priority)
            VALUES (?, ?, ?)
        """
        
        return self.execute_query(query, (keyword, category_id, priority))
    
    def get_categorization_rules(self) -> List[Dict]:
        """Get all categorization rules"""
        query = """
            SELECT cr.*, c.name as category_name
            FROM categorization_rules cr
            JOIN categories c ON cr.category_id = c.id
            ORDER BY cr.priority DESC, cr.keyword
        """
        
        results = self.execute_query(query)
        return [dict(zip(['id', 'keyword', 'category_id', 'priority', 'created_at', 
                         'category_name'], row)) for row in results]