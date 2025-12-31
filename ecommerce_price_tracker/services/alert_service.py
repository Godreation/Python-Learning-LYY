import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv
import os
from typing import Dict, Any, List

# 加载环境变量
load_dotenv()

class AlertService:
    def __init__(self):
        # 从环境变量加载邮件配置
        self.email_host = os.getenv('EMAIL_HOST')
        self.email_port = int(os.getenv('EMAIL_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
    
    def send_email(self, subject: str, body: str, to: str = None) -> bool:
        """发送邮件"""
        if not to:
            to = self.email_to
        
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = Header(self.email_from, 'utf-8')
            msg['To'] = Header(to, 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件正文
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"邮件发送成功，收件人: {to}")
            return True
        except Exception as e:
            print(f"邮件发送失败，错误: {e}")
            return False
    
    def format_price_alert_email(self, alert_data: Dict[str, Any]) -> Dict[str, str]:
        """格式化价格告警邮件内容"""
        product = alert_data['product']
        latest_price = alert_data['latest_price']
        threshold_price = alert_data['alert'].threshold_price
        
        subject = f"【价格告警】{product.name} 价格已降至 {latest_price:.2f} 元"
        
        body = f"""<html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #ff6600;">价格告警通知</h2>
            <p>您好，</p>
            <p>您关注的商品 <strong>{product.name}</strong> 价格已降至 <strong style="color: #ff0000; font-size: 18px;">{latest_price:.2f} 元</strong>，低于您设置的阈值 <strong>{threshold_price:.2f} 元</strong>。</p>
            <p>商品详情：</p>
            <ul>
                <li>商品名称：{product.name}</li>
                <li>平台：{product.platform}</li>
                <li>当前价格：{latest_price:.2f} 元</li>
                <li>您设置的阈值：{threshold_price:.2f} 元</li>
                <li>商品链接：<a href="{product.url}">{product.url}</a></li>
            </ul>
            <p>请及时查看并做出购买决策。</p>
            <p>此致</p>
            <p>电商价格监控系统</p>
        </body>
        </html>"""
        
        return {
            'subject': subject,
            'body': body
        }
    
    def send_price_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """发送所有价格告警"""
        sent_count = 0
        
        for alert_data in alerts:
            email_content = self.format_price_alert_email(alert_data)
            if self.send_email(email_content['subject'], email_content['body']):
                sent_count += 1
        
        return sent_count
    
    def send_daily_report_email(self, report_data: Dict[str, Any], to: str = None) -> bool:
        """发送每日价格报告邮件"""
        subject = f"【每日报告】电商价格监控报告 - {report_data['date']}"
        
        body = f"""<html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #0066cc;">电商价格监控每日报告</h2>
            <p>日期：{report_data['date']}</p>
            <p>监控商品数量：{report_data['total_products']}</p>
            <p>今日更新商品数量：{report_data['updated_products']}</p>
            <p>价格下降商品数量：{report_data['price_decreased_products']}</p>
            
            {report_data.get('product_details', '')}
            
            <p>详细报告请查看附件或登录系统查看。</p>
            <p>此致</p>
            <p>电商价格监控系统</p>
        </body>
        </html>"""
        
        return self.send_email(subject, body, to)
