from database import DatabaseManager
from transaction_manager import TransactionManager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import calendar
import statistics

class FinancialAnalysis:
    def __init__(self, db_manager: DatabaseManager, transaction_manager: TransactionManager):
        self.db = db_manager
        self.transaction_manager = transaction_manager
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get comprehensive monthly summary"""
        summary = self.db.get_monthly_summary(year, month)
        
        # Add additional calculations
        if summary['income_count'] > 0:
            summary['average_income'] = summary['income'] / summary['income_count']
        else:
            summary['average_income'] = 0
        
        if summary['expense_count'] > 0:
            summary['average_expense'] = summary['expense'] / summary['expense_count']
        else:
            summary['average_expense'] = 0
        
        # Get category breakdown
        summary['income_breakdown'] = self.db.get_category_breakdown(year, month, 'income')
        summary['expense_breakdown'] = self.db.get_category_breakdown(year, month, 'expense')
        
        # Calculate savings rate
        if summary['income'] > 0:
            summary['savings_rate'] = (summary['balance'] / summary['income']) * 100
        else:
            summary['savings_rate'] = 0
        
        return summary
    
    def get_trend_analysis(self, months: int = 12) -> Dict:
        """Analyze trends over the last N months"""
        today = datetime.now()
        trends = {
            'months': [],
            'income': [],
            'expense': [],
            'balance': [],
            'savings_rate': []
        }
        
        for i in range(months - 1, -1, -1):
            target_date = today - timedelta(days=30 * i)
            year = target_date.year
            month = target_date.month
            
            summary = self.get_monthly_summary(year, month)
            
            trends['months'].append(f"{year}-{month:02d}")
            trends['income'].append(summary['income'])
            trends['expense'].append(summary['expense'])
            trends['balance'].append(summary['balance'])
            trends['savings_rate'].append(summary['savings_rate'])
        
        # Calculate trends
        if len(trends['income']) >= 2:
            trends['income_trend'] = self._calculate_trend(trends['income'])
            trends['expense_trend'] = self._calculate_trend(trends['expense'])
            trends['balance_trend'] = self._calculate_trend(trends['balance'])
        else:
            trends['income_trend'] = 'insufficient_data'
            trends['expense_trend'] = 'insufficient_data'
            trends['balance_trend'] = 'insufficient_data'
        
        return trends
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction based on data"""
        if len(data) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation: compare first and last values
        first_half_avg = statistics.mean(data[:len(data)//2])
        second_half_avg = statistics.mean(data[len(data)//2:])
        
        if second_half_avg > first_half_avg * 1.1:
            return 'increasing'
        elif second_half_avg < first_half_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_category_analysis(self, start_date: str, end_date: str) -> Dict:
        """Analyze spending by category"""
        transactions = self.transaction_manager.get_transactions(start_date, end_date, transaction_type='expense')
        
        category_totals = {}
        category_counts = {}
        
        for transaction in transactions:
            category_name = transaction['category_name']
            amount = transaction['amount']
            
            if category_name not in category_totals:
                category_totals[category_name] = 0
                category_counts[category_name] = 0
            
            category_totals[category_name] += amount
            category_counts[category_name] += 1
        
        # Calculate percentages
        total_expenses = sum(category_totals.values())
        
        category_analysis = []
        for category_name, total in category_totals.items():
            percentage = (total / total_expenses * 100) if total_expenses > 0 else 0
            
            category_analysis.append({
                'category': category_name,
                'total': total,
                'percentage': percentage,
                'count': category_counts[category_name],
                'average': total / category_counts[category_name]
            })
        
        # Sort by total (descending)
        category_analysis.sort(key=lambda x: x['total'], reverse=True)
        
        return {
            'total_expenses': total_expenses,
            'categories': category_analysis,
            'period': f"{start_date} to {end_date}"
        }
    
    def detect_anomalies(self, months: int = 6) -> List[Dict]:
        """Detect unusual spending patterns"""
        today = datetime.now()
        start_date = (today - timedelta(days=30 * months)).strftime('%Y-%m-%d')
        
        transactions = self.transaction_manager.get_transactions(start_date)
        expense_transactions = [t for t in transactions if t['type'] == 'expense']
        
        if len(expense_transactions) < 10:
            return []
        
        # Calculate average and standard deviation
        amounts = [t['amount'] for t in expense_transactions]
        avg_amount = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        anomalies = []
        
        for transaction in expense_transactions:
            # Detect large transactions (more than 2 standard deviations from mean)
            if std_dev > 0 and transaction['amount'] > avg_amount + (2 * std_dev):
                anomalies.append({
                    'type': 'large_transaction',
                    'transaction': transaction,
                    'reason': f"Transaction amount ({transaction['amount']}) is significantly higher than average ({avg_amount:.2f})",
                    'severity': 'high'
                })
            
            # Detect unusual categories (spending in categories that are rarely used)
            # This would require more sophisticated analysis
        
        return anomalies
    
    def get_spending_habits(self, months: int = 6) -> Dict:
        """Analyze spending habits and patterns"""
        today = datetime.now()
        start_date = (today - timedelta(days=30 * months)).strftime('%Y-%m-%d')
        
        transactions = self.transaction_manager.get_transactions(start_date, transaction_type='expense')
        
        if not transactions:
            return {'message': 'Insufficient data for analysis'}
        
        # Analyze by day of week
        day_of_week_totals = {}
        day_of_week_counts = {}
        
        # Analyze by time of month
        day_of_month_totals = {}
        day_of_month_counts = {}
        
        for transaction in transactions:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            
            # Day of week analysis
            day_name = date.strftime('%A')
            if day_name not in day_of_week_totals:
                day_of_week_totals[day_name] = 0
                day_of_week_counts[day_name] = 0
            day_of_week_totals[day_name] += transaction['amount']
            day_of_week_counts[day_name] += 1
            
            # Day of month analysis
            day_num = date.day
            if day_num not in day_of_month_totals:
                day_of_month_totals[day_num] = 0
                day_of_month_counts[day_num] = 0
            day_of_month_totals[day_num] += transaction['amount']
            day_of_month_counts[day_num] += 1
        
        # Calculate averages
        day_of_week_analysis = []
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            total = day_of_week_totals.get(day_name, 0)
            count = day_of_week_counts.get(day_name, 0)
            average = total / count if count > 0 else 0
            
            day_of_week_analysis.append({
                'day': day_name,
                'total': total,
                'count': count,
                'average': average
            })
        
        day_of_month_analysis = []
        for day_num in range(1, 32):
            total = day_of_month_totals.get(day_num, 0)
            count = day_of_month_counts.get(day_num, 0)
            average = total / count if count > 0 else 0
            
            if count > 0:  # Only include days with data
                day_of_month_analysis.append({
                    'day': day_num,
                    'total': total,
                    'count': count,
                    'average': average
                })
        
        return {
            'day_of_week': day_of_week_analysis,
            'day_of_month': day_of_month_analysis,
            'total_transactions': len(transactions),
            'total_spent': sum(t['amount'] for t in transactions),
            'analysis_period': f"Last {months} months"
        }
    
    def get_financial_health_score(self) -> Dict:
        """Calculate overall financial health score"""
        today = datetime.now()
        
        # Get data for the last 6 months
        start_date = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        
        transactions = self.transaction_manager.get_transactions(start_date)
        income_transactions = [t for t in transactions if t['type'] == 'income']
        expense_transactions = [t for t in transactions if t['type'] == 'expense']
        
        if not income_transactions or not expense_transactions:
            return {'score': 0, 'message': 'Insufficient data for scoring'}
        
        total_income = sum(t['amount'] for t in income_transactions)
        total_expenses = sum(t['amount'] for t in expense_transactions)
        
        # Calculate scores for different factors (0-100 each)
        
        # 1. Savings rate (weight: 30%)
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            savings_score = min(max(savings_rate * 2, 0), 100)  # 50% savings rate = 100 points
        else:
            savings_score = 0
        
        # 2. Expense consistency (weight: 25%)
        monthly_expenses = {}
        for transaction in expense_transactions:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_expenses:
                monthly_expenses[month_key] = 0
            monthly_expenses[month_key] += transaction['amount']
        
        if len(monthly_expenses) >= 3:
            expense_values = list(monthly_expenses.values())
            cv = statistics.stdev(expense_values) / statistics.mean(expense_values)
            consistency_score = max(0, 100 - (cv * 100))  # Lower CV = higher score
        else:
            consistency_score = 50  # Neutral score for insufficient data
        
        # 3. Income stability (weight: 20%)
        monthly_income = {}
        for transaction in income_transactions:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_income:
                monthly_income[month_key] = 0
            monthly_income[month_key] += transaction['amount']
        
        if len(monthly_income) >= 3:
            income_values = list(monthly_income.values())
            cv = statistics.stdev(income_values) / statistics.mean(income_values)
            income_stability_score = max(0, 100 - (cv * 100))
        else:
            income_stability_score = 50
        
        # 4. Debt-to-income ratio (simplified) (weight: 15%)
        # For simplicity, we'll use expense-to-income ratio
        if total_income > 0:
            expense_ratio = (total_expenses / total_income) * 100
            debt_score = max(0, 100 - (expense_ratio - 50))  # 50% ratio = 100 points
        else:
            debt_score = 0
        
        # 5. Emergency fund (simplified) (weight: 10%)
        # Check if there's consistent savings
        monthly_balances = {}
        for transaction in transactions:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_balances:
                monthly_balances[month_key] = 0
            
            if transaction['type'] == 'income':
                monthly_balances[month_key] += transaction['amount']
            else:
                monthly_balances[month_key] -= transaction['amount']
        
        positive_months = sum(1 for balance in monthly_balances.values() if balance > 0)
        total_months = len(monthly_balances)
        
        if total_months > 0:
            emergency_score = (positive_months / total_months) * 100
        else:
            emergency_score = 0
        
        # Calculate weighted total score
        weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        scores = [savings_score, consistency_score, income_stability_score, debt_score, emergency_score]
        
        total_score = sum(score * weight for score, weight in zip(scores, weights))
        
        # Determine health level
        if total_score >= 80:
            health_level = 'Excellent'
        elif total_score >= 60:
            health_level = 'Good'
        elif total_score >= 40:
            health_level = 'Fair'
        else:
            health_level = 'Needs Improvement'
        
        return {
            'score': round(total_score, 1),
            'health_level': health_level,
            'breakdown': {
                'savings_rate': round(savings_score, 1),
                'expense_consistency': round(consistency_score, 1),
                'income_stability': round(income_stability_score, 1),
                'debt_management': round(debt_score, 1),
                'emergency_fund': round(emergency_score, 1)
            },
            'recommendations': self._generate_recommendations(scores, weights)
        }
    
    def _generate_recommendations(self, scores: List[float], weights: List[float]) -> List[str]:
        """Generate personalized financial recommendations"""
        recommendations = []
        
        factor_names = ['储蓄率', '支出稳定性', '收入稳定性', '债务管理', '应急储备']
        
        for i, (score, weight, name) in enumerate(zip(scores, weights, factor_names)):
            if score < 60:
                if i == 0:  # Savings rate
                    recommendations.append(f"提高{name}：尝试每月节省更多收入")
                elif i == 1:  # Expense consistency
                    recommendations.append(f"改善{name}：减少不必要支出，建立预算")
                elif i == 2:  # Income stability
                    recommendations.append(f"增强{name}：考虑多元化收入来源")
                elif i == 3:  # Debt management
                    recommendations.append(f"优化{name}：控制支出，避免过度消费")
                elif i == 4:  # Emergency fund
                    recommendations.append(f"建立{name}：确保有足够的应急资金")
        
        if not recommendations:
            recommendations.append("财务状况良好！继续保持当前的理财习惯")
        
        return recommendations