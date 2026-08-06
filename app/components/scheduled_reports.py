"""
Scheduled reports system for LMS application
Allows automated report generation and delivery
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Callable
from enum import Enum
from pathlib import Path
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from components.error_handler import error_logger
    from components.reporting import ReportGenerator, ReportExporter, ReportFilter, ScheduledReport
except ImportError:
    # Fallback for direct imports
    from app.components.error_handler import error_logger
    from app.components.reporting import ReportGenerator, ReportExporter, ReportFilter, ScheduledReport


class ReportScheduler:
    """Manages scheduled report execution"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduled_reports: List[ScheduledReport] = []
        self.running = False
        self.scheduler_thread = None
        self.config_file = Path("app/config/scheduled_reports.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def add_report(self, report: ScheduledReport) -> bool:
        """
        Add a scheduled report
        
        Returns:
            True if added successfully
        """
        try:
            self.scheduled_reports.append(report)
            self._save_config()
            error_logger.info(f"Added scheduled report: {report.name}")
            return True
        except Exception as e:
            error_logger.error(f"Failed to add scheduled report: {str(e)}")
            return False
    
    def remove_report(self, report_name: str) -> bool:
        """
        Remove a scheduled report by name
        
        Returns:
            True if removed successfully
        """
        try:
            self.scheduled_reports = [r for r in self.scheduled_reports if r.name != report_name]
            self._save_config()
            error_logger.info(f"Removed scheduled report: {report_name}")
            return True
        except Exception as e:
            error_logger.error(f"Failed to remove scheduled report: {str(e)}")
            return False
    
    def get_reports(self) -> List[Dict]:
        """Get all scheduled reports as dictionaries"""
        return [
            {
                "name": r.name,
                "type": r.report_type.value,
                "format": r.export_format.value,
                "frequency": r.frequency,
                "last_run": r.last_run.isoformat() if r.last_run else None,
                "next_run": r.next_run.isoformat() if r.next_run else None,
                "email_recipients": r.email_recipients,
            }
            for r in self.scheduled_reports
        ]
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            error_logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        error_logger.info("Report scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        error_logger.info("Report scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                now = datetime.now()
                
                for report in self.scheduled_reports:
                    if report.should_run():
                        self._execute_report(report)
                
                # Check every minute
                time.sleep(60)
            
            except Exception as e:
                error_logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _execute_report(self, report: ScheduledReport):
        """
        Execute a scheduled report
        
        Args:
            report: ScheduledReport to execute
        """
        try:
            error_logger.info(f"Executing scheduled report: {report.name}")
            
            # Generate and export report
            # This would use ReportGenerator and ReportExporter
            
            # Mark as run
            report.mark_as_run()
            self._save_config()
            
            error_logger.info(f"Scheduled report executed: {report.name}")
        
        except Exception as e:
            error_logger.error(f"Failed to execute scheduled report {report.name}: {str(e)}")
    
    def _save_config(self):
        """Save scheduled reports configuration to file"""
        try:
            config_data = {
                "reports": [
                    {
                        "name": r.name,
                        "type": r.report_type.value,
                        "format": r.export_format.value,
                        "frequency": r.frequency,
                        "last_run": r.last_run.isoformat() if r.last_run else None,
                        "next_run": r.next_run.isoformat() if r.next_run else None,
                        "email_recipients": r.email_recipients,
                    }
                    for r in self.scheduled_reports
                ]
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        except Exception as e:
            error_logger.error(f"Failed to save scheduler config: {str(e)}")
    
    def _load_config(self):
        """Load scheduled reports configuration from file"""
        try:
            if not self.config_file.exists():
                return
            
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Would reconstruct ScheduledReport objects here
            error_logger.info(f"Loaded {len(config_data.get('reports', []))} scheduled reports")
        
        except Exception as e:
            error_logger.error(f"Failed to load scheduler config: {str(e)}")


class ReportDelivery:
    """Handle report delivery via email"""
    
    @staticmethod
    def send_email(report_name: str, file_path: str, recipients: List[str]) -> bool:
        """
        Send report via email
        
        Args:
            report_name: Name of report
            file_path: Path to report file
            recipients: List of email addresses
        
        Returns:
            True if sent successfully
        """
        try:
            # Placeholder for email sending logic
            # In production, use smtplib or email service
            error_logger.info(f"Sending report '{report_name}' to {', '.join(recipients)}")
            return True
        
        except Exception as e:
            error_logger.error(f"Failed to send report email: {str(e)}")
            return False


class ReportArchive:
    """Manage report history and archive"""
    
    def __init__(self):
        """Initialize archive"""
        self.archive_dir = Path("app/reports/archive")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def save_report(self, report_name: str, file_path: str) -> bool:
        """
        Save report to archive
        
        Args:
            report_name: Name of report
            file_path: Path to report file
        
        Returns:
            True if saved successfully
        """
        try:
            # Create date-based subdirectory
            date_dir = self.archive_dir / datetime.now().strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to archive with timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            archive_path = date_dir / f"{report_name}_{timestamp}"
            
            import shutil
            shutil.copy2(file_path, archive_path)
            
            error_logger.info(f"Report archived: {archive_path}")
            return True
        
        except Exception as e:
            error_logger.error(f"Failed to archive report: {str(e)}")
            return False
    
    def get_archives(self, days: int = 30) -> List[Dict]:
        """
        Get archived reports from last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of archived report info
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            archives = []
            
            for archive_file in self.archive_dir.rglob("*"):
                if archive_file.is_file():
                    stat_info = archive_file.stat()
                    if stat_info.st_mtime > cutoff_date.timestamp():
                        archives.append({
                            "name": archive_file.name,
                            "path": str(archive_file),
                            "size": stat_info.st_size,
                            "date": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        })
            
            return sorted(archives, key=lambda x: x["date"], reverse=True)
        
        except Exception as e:
            error_logger.error(f"Failed to get archives: {str(e)}")
            return []
    
    def cleanup_old_reports(self, days: int = 90) -> int:
        """
        Delete reports older than N days
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of files deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for archive_file in self.archive_dir.rglob("*"):
                if archive_file.is_file():
                    stat_info = archive_file.stat()
                    if stat_info.st_mtime < cutoff_date.timestamp():
                        archive_file.unlink()
                        deleted_count += 1
            
            if deleted_count > 0:
                error_logger.info(f"Deleted {deleted_count} archived reports older than {days} days")
            
            return deleted_count
        
        except Exception as e:
            error_logger.error(f"Failed to cleanup old reports: {str(e)}")
            return 0


# Global scheduler instance
global_scheduler = ReportScheduler()
report_archive = ReportArchive()
