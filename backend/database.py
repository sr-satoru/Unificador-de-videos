"""
Database models and operations for file management
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "video_editor.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Files table - tracks all uploaded files
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    original_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'uploaded',
                    job_id TEXT,
                    processed_time TIMESTAMP,
                    output_path TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            ''')
            
            # Jobs table - tracks processing jobs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'processing',
                    progress INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    zip_path TEXT,
                    zip_created_at TIMESTAMP,
                    settings TEXT,
                    error_message TEXT
                )
            ''')
            
            # Cleanup log table - tracks cleanup operations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cleanup_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    file_path TEXT,
                    job_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_file(self, file_id: str, original_name: str, file_path: str, size: int) -> bool:
        """Add a new file to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO files (id, original_name, file_path, size)
                    VALUES (?, ?, ?, ?)
                ''', (file_id, original_name, file_path, size))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding file {file_id}: {e}")
            return False
    
    def add_job(self, job_id: str, settings: Dict[str, Any]) -> bool:
        """Add a new processing job"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO jobs (id, settings)
                    VALUES (?, ?)
                ''', (job_id, str(settings)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding job {job_id}: {e}")
            return False
    
    def update_file_status(self, file_id: str, status: str, job_id: Optional[str] = None, 
                          output_path: Optional[str] = None) -> bool:
        """Update file status and processing info"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_fields = ["status = ?"]
                params = [status]
                
                if job_id:
                    update_fields.append("job_id = ?")
                    params.append(job_id)
                
                if output_path:
                    update_fields.append("output_path = ?")
                    update_fields.append("processed_time = ?")
                    params.extend([output_path, datetime.now().isoformat()])
                
                params.append(file_id)
                
                cursor.execute(f'''
                    UPDATE files 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating file {file_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: str, progress: Optional[int] = None,
                        zip_path: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        """Update job status and progress"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_fields = ["status = ?"]
                params = [status]
                
                if progress is not None:
                    update_fields.append("progress = ?")
                    params.append(progress)
                
                if zip_path:
                    update_fields.append("zip_path = ?")
                    update_fields.append("zip_created_at = ?")
                    params.extend([zip_path, datetime.now().isoformat()])
                
                if error_message:
                    update_fields.append("error_message = ?")
                    params.append(error_message)
                
                if status == 'completed':
                    update_fields.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
                
                params.append(job_id)
                
                cursor.execute(f'''
                    UPDATE jobs 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            return False
    
    def get_files_for_cleanup(self, max_age_minutes: int = 5) -> List[Dict[str, Any]]:
        """Get files that can be cleaned up from uploads folder"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
                
                cursor.execute('''
                    SELECT id, file_path, original_name, upload_time
                    FROM files 
                    WHERE status = 'completed' 
                    AND upload_time < ?
                    AND file_path LIKE 'uploads/%'
                ''', (cutoff_time.isoformat(),))
                
                return [dict(zip([col[0] for col in cursor.description], row)) 
                       for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting files for cleanup: {e}")
            return []
    
    def get_zip_files_for_cleanup(self, max_age_minutes: int = 10) -> List[Dict[str, Any]]:
        """Get zip files that can be cleaned up"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
                
                cursor.execute('''
                    SELECT id, zip_path, zip_created_at
                    FROM jobs 
                    WHERE status = 'completed' 
                    AND zip_path IS NOT NULL
                    AND zip_created_at < ?
                ''', (cutoff_time.isoformat(),))
                
                return [dict(zip([col[0] for col in cursor.description], row)) 
                       for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting zip files for cleanup: {e}")
            return []
    
    def get_processed_videos_for_cleanup(self, job_id: str) -> List[Dict[str, Any]]:
        """Get processed video files for a specific job"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, output_path, original_name
                    FROM files 
                    WHERE job_id = ? 
                    AND output_path IS NOT NULL
                    AND output_path LIKE 'outputs/%'
                ''', (job_id,))
                
                return [dict(zip([col[0] for col in cursor.description], row)) 
                       for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting processed videos for cleanup: {e}")
            return []
    
    def log_cleanup_operation(self, operation: str, file_path: str = None, 
                             job_id: str = None, success: bool = True, 
                             error_message: str = None) -> bool:
        """Log cleanup operations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO cleanup_log (operation, file_path, job_id, success, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (operation, file_path, job_id, success, error_message))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging cleanup operation: {e}")
            return False
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total files
                cursor.execute("SELECT COUNT(*) FROM files")
                total_files = cursor.fetchone()[0]
                
                # Files by status
                cursor.execute("SELECT status, COUNT(*) FROM files GROUP BY status")
                files_by_status = dict(cursor.fetchall())
                
                # Total jobs
                cursor.execute("SELECT COUNT(*) FROM jobs")
                total_jobs = cursor.fetchone()[0]
                
                # Jobs by status
                cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
                jobs_by_status = dict(cursor.fetchall())
                
                # Cleanup operations
                cursor.execute("SELECT operation, COUNT(*) FROM cleanup_log GROUP BY operation")
                cleanup_operations = dict(cursor.fetchall())
                
                return {
                    "total_files": total_files,
                    "files_by_status": files_by_status,
                    "total_jobs": total_jobs,
                    "jobs_by_status": jobs_by_status,
                    "cleanup_operations": cleanup_operations
                }
        except Exception as e:
            logger.error(f"Error getting cleanup stats: {e}")
            return {}

# Global database instance
db_manager = DatabaseManager()
