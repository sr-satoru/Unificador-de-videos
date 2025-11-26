"""
Intelligent cleanup system for file management
"""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import shutil
import zipfile

from database import db_manager

logger = logging.getLogger(__name__)

class CleanupManager:
    def __init__(self):
        self.is_running = False
        self.cleanup_interval = 30  # Check every 30 seconds
        self.upload_cleanup_delay = 5  # Clean uploads after 5 seconds
        self.zip_cleanup_delay = 10  # Clean zips after 10 minutes
        self.processed_video_cleanup_delay = 1  # Clean processed videos after 1 minute
        
    async def start_cleanup_service(self):
        """Start the background cleanup service"""
        if self.is_running:
            logger.warning("Cleanup service is already running")
            return
        
        self.is_running = True
        logger.info("Starting intelligent cleanup service...")
        
        while self.is_running:
            try:
                await self.perform_cleanup_cycle()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup cycle: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    def stop_cleanup_service(self):
        """Stop the background cleanup service"""
        self.is_running = False
        logger.info("Cleanup service stopped")
    
    async def perform_cleanup_cycle(self):
        """Perform one cleanup cycle"""
        logger.debug("Performing cleanup cycle...")
        
        # 1. Clean up uploaded files (after processing is complete)
        await self.cleanup_uploaded_files()
        
        # 2. Clean up processed video files (after zip creation)
        await self.cleanup_processed_videos()
        
        # 3. Clean up zip files (after download)
        await self.cleanup_zip_files()
        
        # 4. Clean up old database entries
        await self.cleanup_old_database_entries()
    
    async def cleanup_uploaded_files(self):
        """Clean up uploaded files after processing"""
        try:
            files_to_clean = db_manager.get_files_for_cleanup(self.upload_cleanup_delay)
            
            for file_info in files_to_clean:
                file_path = file_info['file_path']
                file_id = file_info['id']
                
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        db_manager.log_cleanup_operation(
                            "upload_file_deleted", 
                            file_path, 
                            success=True
                        )
                        logger.info(f"Deleted uploaded file: {file_path}")
                    except Exception as e:
                        db_manager.log_cleanup_operation(
                            "upload_file_deleted", 
                            file_path, 
                            success=False, 
                            error_message=str(e)
                        )
                        logger.error(f"Error deleting uploaded file {file_path}: {e}")
                else:
                    logger.warning(f"Upload file not found: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error in cleanup_uploaded_files: {e}")
    
    async def cleanup_processed_videos(self):
        """Clean up processed video files after zip creation"""
        try:
            # Get completed jobs with zip files
            zip_jobs = db_manager.get_zip_files_for_cleanup(1)  # 1 minute delay
            
            for job_info in zip_jobs:
                job_id = job_info['id']
                processed_videos = db_manager.get_processed_videos_for_cleanup(job_id)
                
                for video_info in processed_videos:
                    output_path = video_info['output_path']
                    
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                            db_manager.log_cleanup_operation(
                                "processed_video_deleted", 
                                output_path, 
                                job_id, 
                                success=True
                            )
                            logger.info(f"Deleted processed video: {output_path}")
                        except Exception as e:
                            db_manager.log_cleanup_operation(
                                "processed_video_deleted", 
                                output_path, 
                                job_id, 
                                success=False, 
                                error_message=str(e)
                            )
                            logger.error(f"Error deleting processed video {output_path}: {e}")
                    else:
                        logger.warning(f"Processed video not found: {output_path}")
                        
        except Exception as e:
            logger.error(f"Error in cleanup_processed_videos: {e}")
    
    async def cleanup_zip_files(self):
        """Clean up zip files after download"""
        try:
            zip_files = db_manager.get_zip_files_for_cleanup(self.zip_cleanup_delay)
            
            for zip_info in zip_files:
                zip_path = zip_info['zip_path']
                job_id = zip_info['id']
                
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                        db_manager.log_cleanup_operation(
                            "zip_file_deleted", 
                            zip_path, 
                            job_id, 
                            success=True
                        )
                        logger.info(f"Deleted zip file: {zip_path}")
                    except Exception as e:
                        db_manager.log_cleanup_operation(
                            "zip_file_deleted", 
                            zip_path, 
                            job_id, 
                            success=False, 
                            error_message=str(e)
                        )
                        logger.error(f"Error deleting zip file {zip_path}: {e}")
                else:
                    logger.warning(f"Zip file not found: {zip_path}")
                    
        except Exception as e:
            logger.error(f"Error in cleanup_zip_files: {e}")
    
    async def cleanup_old_database_entries(self):
        """Clean up old database entries (older than 24 hours)"""
        try:
            # This would clean up old log entries and completed jobs
            # Implementation depends on your specific needs
            pass
        except Exception as e:
            logger.error(f"Error in cleanup_old_database_entries: {e}")
    
    async def force_cleanup_job(self, job_id: str):
        """Force cleanup of all files related to a specific job"""
        try:
            logger.info(f"Force cleaning job: {job_id}")
            
            # Get all files for this job
            processed_videos = db_manager.get_processed_videos_for_cleanup(job_id)
            
            # Delete processed videos
            for video_info in processed_videos:
                output_path = video_info['output_path']
                if os.path.exists(output_path):
                    os.remove(output_path)
                    db_manager.log_cleanup_operation(
                        "force_cleanup_video", 
                        output_path, 
                        job_id, 
                        success=True
                    )
                    logger.info(f"Force deleted video: {output_path}")
            
            # Delete zip file if exists
            # This would require getting zip path from job info
            
            logger.info(f"Force cleanup completed for job: {job_id}")
            
        except Exception as e:
            logger.error(f"Error in force_cleanup_job: {e}")
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics"""
        return db_manager.get_cleanup_stats()
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get current storage usage"""
        try:
            uploads_size = self._get_directory_size("uploads")
            outputs_size = self._get_directory_size("outputs")
            temp_size = self._get_directory_size("temp")
            
            return {
                "uploads_size_mb": round(uploads_size / (1024 * 1024), 2),
                "outputs_size_mb": round(outputs_size / (1024 * 1024), 2),
                "temp_size_mb": round(temp_size / (1024 * 1024), 2),
                "total_size_mb": round((uploads_size + outputs_size + temp_size) / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Error getting storage usage: {e}")
            return {}
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error calculating directory size for {directory}: {e}")
        return total_size

# Global cleanup manager instance
cleanup_manager = CleanupManager()
