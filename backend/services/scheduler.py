"""
定时任务调度服务
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
import os
import sys

logger = logging.getLogger(__name__)

class SchedulerService:
    """定时任务调度器服务"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.notification_callbacks = []

    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("定时任务调度器已启动")

    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("定时任务调度器已停止")

    def add_reminder_job(self, interval_minutes: int = 30, working_hours_only: bool = True,
                        start_time: str = "09:00", end_time: str = "18:00"):
        """添加提醒任务"""
        # 移除现有的提醒任务
        self.remove_reminder_job()

        if not self.is_running:
            self.start()

        if working_hours_only:
            # 只在工作时间内提醒
            # 解析时间
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))

            # 创建cron表达式，每隔指定分钟在工作时间内触发
            self.scheduler.add_job(
                func=self._send_reminder_with_time_check,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='kegel_reminder',
                name='提肛运动提醒',
                replace_existing=True,
                kwargs={
                    'start_hour': start_hour,
                    'start_minute': start_minute,
                    'end_hour': end_hour,
                    'end_minute': end_minute
                }
            )
        else:
            # 全天提醒
            self.scheduler.add_job(
                func=self._send_reminder,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='kegel_reminder',
                name='提肛运动提醒',
                replace_existing=True
            )

        logger.info(f"已设置提醒任务，间隔: {interval_minutes}分钟，工作时间限制: {working_hours_only}")

    def remove_reminder_job(self):
        """移除提醒任务"""
        try:
            self.scheduler.remove_job('kegel_reminder')
            logger.info("已移除提醒任务")
        except:
            pass  # 任务不存在时忽略错误

    def _send_reminder_with_time_check(self, start_hour: int, start_minute: int,
                                     end_hour: int, end_minute: int):
        """带时间检查的提醒发送"""
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        start_time = start_hour * 60 + start_minute
        end_time = end_hour * 60 + end_minute

        # 检查是否在工作时间内
        if start_time <= current_time <= end_time:
            self._send_reminder()
        else:
            logger.debug(f"当前时间 {now.strftime('%H:%M')} 不在工作时间内，跳过提醒")

    def _send_reminder(self):
        """发送提醒通知"""
        try:
            logger.info("发送提肛运动提醒")

            # 调用所有注册的回调函数
            for callback in self.notification_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"回调函数执行失败: {e}")

            # 显示系统通知
            self._show_system_notification()

            # 记录提醒日志
            self._log_reminder()

        except Exception as e:
            logger.error(f"发送提醒失败: {e}")

    def _show_system_notification(self):
        """显示系统通知"""
        try:
            # 尝试使用plyer显示通知
            try:
                from plyer import notification
                notification.notify(
                    title="提肛小助手",
                    message="该做提肛运动了！保持健康从现在开始 💪",
                    timeout=10,
                    app_icon=None  # 可以添加图标路径
                )
                logger.info("已显示系统通知")
                return
            except ImportError:
                logger.warning("plyer库未安装")
            except Exception as e:
                logger.warning(f"plyer通知失败: {e}")

            # Windows系统通知备选方案
            if sys.platform == "win32":
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        "提肛小助手",
                        "该做提肛运动了！保持健康从现在开始 💪",
                        duration=10
                    )
                    logger.info("已显示Windows通知")
                    return
                except ImportError:
                    logger.warning("win10toast库未安装")
                except Exception as e:
                    logger.warning(f"Windows通知失败: {e}")

            # 控制台输出备选方案
            print("\n" + "="*50)
            print("🔔 提肛小助手提醒")
            print("该做提肛运动了！保持健康从现在开始 💪")
            print("="*50 + "\n")

        except Exception as e:
            logger.error(f"显示系统通知失败: {e}")

    def _log_reminder(self):
        """记录提醒日志"""
        try:
            # TODO: 将提醒记录保存到数据库
            logger.info(f"提醒已发送 - {datetime.now().isoformat()}")
        except Exception as e:
            logger.error(f"记录提醒日志失败: {e}")

    def add_notification_callback(self, callback):
        """添加通知回调函数"""
        if callback not in self.notification_callbacks:
            self.notification_callbacks.append(callback)

    def remove_notification_callback(self, callback):
        """移除通知回调函数"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)

    def get_next_reminder_time(self) -> str:
        """获取下次提醒时间"""
        try:
            job = self.scheduler.get_job('kegel_reminder')
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except Exception as e:
            logger.error(f"获取下次提醒时间失败: {e}")
        return ""

    def is_reminder_enabled(self) -> bool:
        """检查提醒是否启用"""
        try:
            job = self.scheduler.get_job('kegel_reminder')
            return job is not None
        except Exception as e:
            logger.error(f"检查提醒状态失败: {e}")
            return False

    def get_scheduler_status(self) -> dict:
        """获取调度器状态"""
        try:
            jobs = self.scheduler.get_jobs()
            return {
                "running": self.is_running,
                "job_count": len(jobs),
                "reminder_enabled": self.is_reminder_enabled(),
                "next_reminder": self.get_next_reminder_time()
            }
        except Exception as e:
            logger.error(f"获取调度器状态失败: {e}")
            return {
                "running": False,
                "job_count": 0,
                "reminder_enabled": False,
                "next_reminder": ""
            }
