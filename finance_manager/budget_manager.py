from database import DatabaseManager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import calendar

class BudgetManager:
    def __init__(self, db_manager: DatabaseManager, transaction_manager):
        self.db = db_manager
        self.transaction_manager = transaction_manager
    
    def create_budget(self, category_id: int, amount: float, period: str,
                     start_date: str, end_date: str = None) -> Dict:
        """Create a new budget"""
        # Validate period
        if period not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise ValueError("Period must be one of: daily, weekly, monthly, yearly")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Budget amount must be positive")
        
        # Validate category exists
        categories = self.db.get_categories()
        category_exists = any(cat['id'] == category_id for cat in categories)
        if not category_exists:
            raise ValueError("Category does not exist")
        
        budget_id = self.db.add_budget(category_id, amount, period, start_date, end_date)
        
        return {
            'id': budget_id,
            'category_id': category_id,
            'amount': amount,
            'period': period,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def update_budget(self, budget_id: int, amount: float = None,
                     period: str = None, end_date: str = None) -> bool:
        """Update an existing budget"""
        # Get current budget
        current = self.get_budget(budget_id)
        if not current:
            return False
        
        # Prepare update fields
        update_fields = []
        params = []
        
        if amount is not None and amount > 0:
            update_fields.append("amount = ?")
            params.append(amount)
        
        if period is not None and period in ['daily', 'weekly', 'monthly', 'yearly']:
            update_fields.append("period = ?")
            params.append(period)
        
        if end_date is not None:
            update_fields.append("end_date = ?")
            params.append(end_date)
        
        if not update_fields:
            return False
        
        query = f"UPDATE budgets SET {', '.join(update_fields)} WHERE id = ?"
        params.append(budget_id)
        
        self.db.execute_query(query, tuple(params))
        return True
    
    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget"""
        query = "DELETE FROM budgets WHERE id = ?"
        self.db.execute_query(query, (budget_id,))
        return True
    
    def get_budget(self, budget_id: int) -> Optional[Dict]:
        """Get a specific budget with progress information"""
        query = """
            SELECT b.*, c.name as category_name, c.type as category_type
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.id = ?
        """
        
        results = self.db.execute_query(query, (budget_id,))
        if not results:
            return None
        
        row = results[0]
        budget = dict(zip(['id', 'category_id', 'amount', 'period', 'start_date', 
                          'end_date', 'created_at', 'category_name', 'category_type'], row))
        
        # Calculate budget progress
        budget['progress'] = self.calculate_budget_progress(budget)
        
        return budget
    
    def get_all_budgets(self) -> List[Dict]:
        """Get all budgets with progress information"""
        budgets = self.db.get_budgets()
        
        for budget in budgets:
            budget['progress'] = self.calculate_budget_progress(budget)
        
        return budgets
    
    def get_active_budgets(self) -> List[Dict]:
        """Get currently active budgets"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT b.*, c.name as category_name, c.type as category_type
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.start_date <= ? AND (b.end_date IS NULL OR b.end_date >= ?)
            ORDER BY b.period, c.name
        """
        
        results = self.db.execute_query(query, (today, today))
        budgets = [dict(zip(['id', 'category_id', 'amount', 'period', 'start_date', 
                           'end_date', 'created_at', 'category_name', 'category_type'], row)) 
                  for row in results]
        
        for budget in budgets:
            budget['progress'] = self.calculate_budget_progress(budget)
        
        return budgets
    
    def calculate_budget_progress(self, budget: Dict) -> Dict:
        """Calculate budget progress and spending information"""
        today = datetime.now()
        start_date = datetime.strptime(budget['start_date'], '%Y-%m-%d')
        
        # Determine date range for this period
        if budget['end_date']:
            end_date = datetime.strptime(budget['end_date'], '%Y-%m-%d')
        else:
            if budget['period'] == 'daily':
                end_date = start_date + timedelta(days=1)
            elif budget['period'] == 'weekly':
                end_date = start_date + timedelta(weeks=1)
            elif budget['period'] == 'monthly':
                # Calculate end of month
                if start_date.month == 12:
                    end_date = datetime(start_date.year + 1, 1, 1)
                else:
                    end_date = datetime(start_date.year, start_date.month + 1, 1)
            else:  # yearly
                end_date = datetime(start_date.year + 1, start_date.month, start_date.day)
        
        # Get transactions for this budget period
        transactions = self.transaction_manager.get_transactions(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            budget['category_id'],
            'expense'
        )
        
        total_spent = sum(t['amount'] for t in transactions)
        budget_amount = budget['amount']
        
        # Calculate progress percentage
        if budget_amount > 0:
            progress_percent = min((total_spent / budget_amount) * 100, 100)
        else:
            progress_percent = 0
        
        # Determine status
        if total_spent > budget_amount:
            status = 'exceeded'
        elif progress_percent >= 80:
            status = 'warning'
        else:
            status = 'normal'
        
        # Calculate days remaining
        days_remaining = max(0, (end_date - today).days)
        
        return {
            'total_spent': total_spent,
            'remaining': max(0, budget_amount - total_spent),
            'progress_percent': progress_percent,
            'status': status,
            'days_remaining': days_remaining,
            'transaction_count': len(transactions),
            'period_start': budget['start_date'],
            'period_end': end_date.strftime('%Y-%m-%d')
        }
    
    def get_budget_alerts(self) -> List[Dict]:
        """Get budget alerts for exceeded or nearly exceeded budgets"""
        active_budgets = self.get_active_budgets()
        alerts = []
        
        for budget in active_budgets:
            progress = budget['progress']
            
            if progress['status'] == 'exceeded':
                alerts.append({
                    'type': 'exceeded',
                    'budget': budget,
                    'message': f"预算已超出！{budget['category_name']} 预算为 {budget['amount']}，实际支出 {progress['total_spent']}",
                    'severity': 'high'
                })
            elif progress['status'] == 'warning':
                alerts.append({
                    'type': 'warning',
                    'budget': budget,
                    'message': f"预算即将用完！{budget['category_name']} 已使用 {progress['progress_percent']:.1f}%",
                    'severity': 'medium'
                })
        
        return alerts
    
    def get_budget_summary(self, year: int, month: int) -> Dict:
        """Get budget summary for a specific month"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        # Get monthly budgets
        monthly_budgets = []
        all_budgets = self.get_all_budgets()
        
        for budget in all_budgets:
            budget_start = datetime.strptime(budget['start_date'], '%Y-%m-%d')
            
            # Check if budget applies to this month
            if (budget_start.year == year and budget_start.month == month) or \
               (budget['period'] == 'monthly' and budget_start <= datetime(year, month, 1)):
                monthly_budgets.append(budget)
        
        # Calculate summary
        total_budget = sum(b['amount'] for b in monthly_budgets)
        
        # Get actual expenses for the month
        expenses = self.transaction_manager.get_transactions(start_date, end_date, transaction_type='expense')
        total_expenses = sum(t['amount'] for t in expenses)
        
        # Calculate by category
        category_expenses = {}
        for expense in expenses:
            cat_name = expense['category_name']
            if cat_name not in category_expenses:
                category_expenses[cat_name] = 0
            category_expenses[cat_name] += expense['amount']
        
        # Compare with budgets
        budget_comparison = []
        for budget in monthly_budgets:
            cat_name = budget['category_name']
            actual = category_expenses.get(cat_name, 0)
            planned = budget['amount']
            
            budget_comparison.append({
                'category': cat_name,
                'planned': planned,
                'actual': actual,
                'difference': actual - planned,
                'variance_percent': ((actual - planned) / planned * 100) if planned > 0 else 0
            })
        
        return {
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'budget_variance': total_expenses - total_budget,
            'variance_percent': ((total_expenses - total_budget) / total_budget * 100) if total_budget > 0 else 0,
            'budget_comparison': budget_comparison,
            'month': f"{year}-{month:02d}"
        }
    
    def suggest_budget(self, category_id: int, period: str = 'monthly') -> Dict:
        """Suggest a budget based on historical spending"""
        # Get historical data for the last 6 months
        today = datetime.now()
        six_months_ago = today - timedelta(days=180)
        
        transactions = self.transaction_manager.get_transactions(
            six_months_ago.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d'),
            category_id,
            'expense'
        )
        
        if not transactions:
            return {
                'suggested_amount': 0,
                'confidence': 'low',
                'reason': 'No historical data available',
                'data_points': 0
            }
        
        # Calculate average monthly spending
        monthly_totals = {}
        for transaction in transactions:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += transaction['amount']
        
        monthly_amounts = list(monthly_totals.values())
        
        if not monthly_amounts:
            return {
                'suggested_amount': 0,
                'confidence': 'low',
                'reason': 'No monthly data available',
                'data_points': 0
            }
        
        # Calculate suggested amount (average + 10% buffer)
        average_amount = sum(monthly_amounts) / len(monthly_amounts)
        suggested_amount = average_amount * 1.1
        
        # Determine confidence level
        if len(monthly_amounts) >= 3:
            # Calculate standard deviation for confidence
            variance = sum((x - average_amount) ** 2 for x in monthly_amounts) / len(monthly_amounts)
            std_dev = variance ** 0.5
            
            if std_dev / average_amount < 0.2:  # Low variance
                confidence = 'high'
            elif std_dev / average_amount < 0.5:  # Medium variance
                confidence = 'medium'
            else:  # High variance
                confidence = 'low'
        else:
            confidence = 'low'
        
        return {
            'suggested_amount': round(suggested_amount, 2),
            'confidence': confidence,
            'reason': f'Based on {len(monthly_amounts)} months of data',
            'data_points': len(monthly_amounts),
            'average_monthly': round(average_amount, 2),
            'min_monthly': round(min(monthly_amounts), 2),
            'max_monthly': round(max(monthly_amounts), 2)
        }