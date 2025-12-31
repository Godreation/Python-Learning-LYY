from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Dict, Any
import asyncio

class SchedulerService:
    def __init__(self):
        # 配置任务存储和执行器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        # 创建调度器
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
    
    def start(self) -> None:
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("调度器已启动")
    
    def shutdown(self) -> None:
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("调度器已关闭")
    
    def add_interval_job(self, func: Callable, seconds: int = 60, minutes: int = 0, hours: int = 0, **kwargs) -> str:
        """添加间隔执行的任务"""
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        job = self.scheduler.add_job(func, trigger, **kwargs)
        return job.id
    
    def add_cron_job(self, func: Callable, **cron_kwargs) -> str:
        """添加Cron表达式执行的任务"""
        trigger = CronTrigger(**cron_kwargs)
        job = self.scheduler.add_job(func, trigger)
        return job.id
    
    def remove_job(self, job_id: str) -> None:
        """移除任务"""
        self.scheduler.remove_job(job_id)
    
    def pause_job(self, job_id: str) -> None:
        """暂停任务"""
        self.scheduler.pause_job(job_id)
    
    def resume_job(self, job_id: str) -> None:
        """恢复任务"""
        self.scheduler.resume_job(job_id)
    
    def list_jobs(self) -> list:
        """列出所有任务"""
        return self.scheduler.get_jobs()
    
    def schedule_price_crawling(self, func: Callable, hours: int = 1) -> str:
        """调度价格爬取任务，默认每小时执行一次"""
        return self.add_interval_job(func, hours=hours, id='price_crawling')
    
    def schedule_daily_report(self, func: Callable, hour: int = 9, minute: int = 0) -> str:
        """调度每日报告生成任务，默认每天上午9点执行"""
        return self.add_cron_job(func, hour=hour, minute=minute, id='daily_report')
    
    def schedule_price_alerts(self, func: Callable, minutes: int = 30) -> str:
        """调度价格告警检查任务，默认每30分钟执行一次"""
        return self.add_interval_job(func, minutes=minutes, id='price_alerts')
    
    def schedule_visualization_generation(self, func: Callable, hours: int = 24) -> str:
        """调度可视化图表生成任务，默认每天执行一次"""
        return self.add_interval_job(func, hours=hours, id='visualization_generation')
    
    def run_async_job(self, coro_func: Callable, **kwargs) -> str:
        """运行异步任务"""
        def wrapper():
            asyncio.run(coro_func(**kwargs))
        
        return self.scheduler.add_job(wrapper, 'date')
    
    def get_job(self, job_id: str) -> Any:
        """获取任务信息"""
        return self.scheduler.get_job(job_id)
    
    def modify_job(self, job_id: str, **kwargs) -> None:
        """修改任务配置"""
        self.scheduler.modify_job(job_id, **kwargs)
