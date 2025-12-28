from database import DatabaseManager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class TransactionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_transaction(self, amount: float, transaction_type: str, 
                       category_id: int, description: str, date: str = None,
                       tags: List[int] = None) -> Dict:
        """Add a new transaction with validation"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate transaction type
        if transaction_type not in ['income', 'expense']:
            raise ValueError("Transaction type must be 'income' or 'expense'")
        
        # Auto-categorize if category not provided
        if not category_id:
            category_id = self.auto_categorize(description)
        
        transaction_id = self.db.add_transaction(
            amount, transaction_type, category_id, description, date, tags
        )
        
        return {
            'id': transaction_id,
            'amount': amount,
            'type': transaction_type,
            'category_id': category_id,
            'description': description,
            'date': date,
            'tags': tags or []
        }
    
    def update_transaction(self, transaction_id: int, amount: float = None,
                          category_id: int = None, description: str = None,
                          date: str = None, tags: List[int] = None) -> bool:
        """Update an existing transaction"""
        # Get current transaction
        current = self.get_transaction(transaction_id)
        if not current:
            return False
        
        # Prepare update fields
        update_fields = []
        params = []
        
        if amount is not None and amount > 0:
            update_fields.append("amount = ?")
            params.append(amount)
        
        if category_id is not None:
            update_fields.append("category_id = ?")
            params.append(category_id)
        
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
        
        if date is not None:
            update_fields.append("date = ?")
            params.append(date)
        
        if tags is not None:
            tags_json = f'[{','.join(map(str, tags))}]'
            update_fields.append("tags = ?")
            params.append(tags_json)
        
        if not update_fields:
            return False
        
        query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = ?"
        params.append(transaction_id)
        
        self.db.execute_query(query, tuple(params))
        return True
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        query = "DELETE FROM transactions WHERE id = ?"
        self.db.execute_query(query, (transaction_id,))
        return True
    
    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Get a specific transaction"""
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
        """
        
        results = self.db.execute_query(query, (transaction_id,))
        if not results:
            return None
        
        row = results[0]
        transaction = dict(zip(['id', 'amount', 'type', 'category_id', 
                              'description', 'date', 'tags', 'created_at',
                              'category_name', 'category_color'], row))
        
        # Parse tags JSON
        if transaction['tags']:
            transaction['tags'] = eval(transaction['tags'])
        else:
            transaction['tags'] = []
        
        return transaction
    
    def get_transactions(self, start_date: str = None, end_date: str = None,
                        category_id: int = None, transaction_type: str = None,
                        limit: int = 100) -> List[Dict]:
        """Get transactions with various filters"""
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
        
        if transaction_type:
            query += " AND t.type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY t.date DESC, t.created_at DESC LIMIT ?"
        params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        
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
    
    def auto_categorize(self, description: str) -> int:
        """Automatically categorize transaction based on description"""
        rules = self.db.get_categorization_rules()
        
        # Sort rules by priority (highest first)
        rules.sort(key=lambda x: x['priority'], reverse=True)
        
        for rule in rules:
            if rule['keyword'].lower() in description.lower():
                return rule['category_id']
        
        # Default category based on common patterns
        description_lower = description.lower()
        
        income_keywords = ['工资', '薪水', '奖金', '分红', '利息', '租金', '投资']
        expense_keywords = {
            '食品餐饮': ['餐厅', '外卖', '超市', '买菜', '食品', '餐饮', '吃饭'],
            '交通出行': ['打车', '公交', '地铁', '火车', '机票', '汽油', '停车'],
            '住房租金': ['房租', '房贷', '水电', '物业', '维修'],
            '娱乐休闲': ['电影', '游戏', '旅游', '健身', '娱乐', '休闲'],
            '医疗健康': ['医院', '药品', '体检', '医生', '医疗'],
            '教育培训': ['学费', '书籍', '课程', '培训', '教育'],
            '购物消费': ['购物', '衣服', '电器', '网购', '消费']
        }
        
        # Check for income keywords
        for keyword in income_keywords:
            if keyword in description_lower:
                income_categories = self.db.get_categories('income')
                return income_categories[0]['id'] if income_categories else 3  # 其他收入
        
        # Check for expense keywords
        for category_name, keywords in expense_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    expense_categories = self.db.get_categories('expense')
                    for cat in expense_categories:
                        if cat['name'] == category_name:
                            return cat['id']
        
        # Default to "其他支出"
        expense_categories = self.db.get_categories('expense')
        for cat in expense_categories:
            if cat['name'] == '其他支出':
                return cat['id']
        
        return 11  # Fallback to "其他支出" ID
    
    def get_recent_transactions(self, days: int = 30) -> List[Dict]:
        """Get recent transactions from the last N days"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        return self.get_transactions(start_date, end_date)
    
    def search_transactions(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search transactions by description"""
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.description LIKE ?
            ORDER BY t.date DESC, t.created_at DESC
            LIMIT ?
        """
        
        results = self.db.execute_query(query, (f'%{search_term}%', limit))
        
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
    
    def get_statistics(self, start_date: str, end_date: str) -> Dict:
        """Get comprehensive statistics for a date range"""
        transactions = self.get_transactions(start_date, end_date)
        
        if not transactions:
            return {
                'total_income': 0,
                'total_expense': 0,
                'balance': 0,
                'transaction_count': 0,
                'average_income': 0,
                'average_expense': 0,
                'largest_income': 0,
                'largest_expense': 0
            }
        
        income_transactions = [t for t in transactions if t['type'] == 'income']
        expense_transactions = [t for t in transactions if t['type'] == 'expense']
        
        total_income = sum(t['amount'] for t in income_transactions)
        total_expense = sum(t['amount'] for t in expense_transactions)
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'transaction_count': len(transactions),
            'income_count': len(income_transactions),
            'expense_count': len(expense_transactions),
            'average_income': total_income / len(income_transactions) if income_transactions else 0,
            'average_expense': total_expense / len(expense_transactions) if expense_transactions else 0,
            'largest_income': max((t['amount'] for t in income_transactions), default=0),
            'largest_expense': max((t['amount'] for t in expense_transactions), default=0)
        }