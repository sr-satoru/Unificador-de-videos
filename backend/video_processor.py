import cv2
import numpy as np
import ffmpeg
import os
import asyncio
import zipfile
import tempfile
from typing import Callable, Optional
import logging
from models import ProcessingSettings

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def process_video(
        self, 
        input_path: str, 
        settings: ProcessingSettings, 
        job_id: str, 
        file_id: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> str:
        """Process a single video with the given settings"""
        try:
            # Create output filename
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{job_id}_{file_id}_{base_name}_processed.mp4"
            output_path = os.path.join("outputs", output_filename)
            
            # Ensure output directory exists
            os.makedirs("outputs", exist_ok=True)
            
            # Get video properties
            probe = ffmpeg.probe(input_path)
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            duration = float(probe['format']['duration'])
            fps = eval(video_stream['r_frame_rate'])
            
            # Check if audio stream exists
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            has_audio = len(audio_streams) > 0
            
            # Determine output resolution based on quality setting
            width, height = self._get_output_resolution(video_stream, settings.output.quality)
            
            # Create processing pipeline
            input_stream = ffmpeg.input(input_path)
            
            # Build output stream with basic scaling
            output_stream = input_stream.video.filter('scale', width, height)
            
            # Apply mirror effect FIRST (before other filters)
            if settings.color.mirrored:
                output_stream = output_stream.filter('hflip')
            
            # Apply speed change if needed
            if settings.effects.speed != 100:
                speed_factor = settings.effects.speed / 100
                output_stream = output_stream.filter('setpts', f'{1/speed_factor}*PTS')
            
            # Apply basic color adjustments
            if settings.color.brightness != 0 or settings.color.contrast != 0:
                brightness = settings.color.brightness / 100.0
                contrast = 1 + (settings.color.contrast / 100.0)
                output_stream = output_stream.filter('eq', brightness=brightness, contrast=contrast)
            
            if settings.color.saturation != 0:
                saturation = 1 + (settings.color.saturation / 100.0)
                output_stream = output_stream.filter('eq', saturation=saturation)
            
            if settings.color.blur > 0:
                blur_amount = settings.color.blur / 10.0
                output_stream = output_stream.filter('gblur', sigma=blur_amount)
            
            if settings.color.monochrome:
                output_stream = output_stream.filter('hue', s=0)
            
            # Create output - only include audio if it exists
            if has_audio:
                output = ffmpeg.output(
                    output_stream,
                    input_stream.audio,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    preset='medium',
                    crf=23
                )
            else:
                # Video only, no audio - não incluir stream de áudio
                output = ffmpeg.output(
                    output_stream,
                    output_path,
                    vcodec='libx264',
                    preset='medium',
                    crf=23
                )
            
            # Run FFmpeg with progress tracking
            await self._run_ffmpeg_with_progress(output, duration, progress_callback)
            
            logger.info(f"Successfully processed video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing video {input_path}: {str(e)}")
            raise
    
    def _get_output_resolution(self, video_stream, quality):
        """Determine output resolution based on quality setting"""
        original_width = int(video_stream['width'])
        original_height = int(video_stream['height'])
        
        def ensure_even_dimensions(width, height):
            """Ensure width and height are even numbers for video encoding"""
            if width % 2 != 0:
                width += 1
            if height % 2 != 0:
                height += 1
            return width, height
        
        if quality == "Preservar Original":
            return ensure_even_dimensions(original_width, original_height)
        elif quality == "HD (720p)":
            # Scale to 720p while maintaining aspect ratio
            if original_height > 720:
                scale_factor = 720 / original_height
                new_width = int(original_width * scale_factor)
                return ensure_even_dimensions(new_width, 720)
            return ensure_even_dimensions(original_width, original_height)
        elif quality == "Full HD (1080p)":
            # Scale to 1080p while maintaining aspect ratio
            if original_height > 1080:
                scale_factor = 1080 / original_height
                new_width = int(original_width * scale_factor)
                return ensure_even_dimensions(new_width, 1080)
            return ensure_even_dimensions(original_width, original_height)
        
        return ensure_even_dimensions(original_width, original_height)
    
    
    async def _run_ffmpeg_with_progress(
        self, 
        output, 
        duration: float, 
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """Run FFmpeg with progress tracking"""
        try:
            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *output.compile(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress
            if progress_callback:
                start_time = asyncio.get_event_loop().time()
                
                while process.returncode is None:
                    await asyncio.sleep(0.5)  # Check every 500ms
                    
                    # Estimate progress based on time elapsed
                    elapsed = asyncio.get_event_loop().time() - start_time
                    estimated_progress = min((elapsed / duration) * 100, 95)  # Cap at 95% until completion
                    
                    progress_callback(estimated_progress)
            
            # Wait for completion
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {stderr.decode()}")
            
            # Final progress update
            if progress_callback:
                progress_callback(100.0)
                
        except Exception as e:
            logger.error(f"FFmpeg execution error: {str(e)}")
            raise
    
    async def create_zip(self, results: list) -> str:
        """Create ZIP file with processed videos"""
        zip_filename = f"processed_videos_{int(asyncio.get_event_loop().time())}.zip"
        zip_path = os.path.join("outputs", zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for result in results:
                if os.path.exists(result['output_path']):
                    # Add file to ZIP with original name
                    arcname = os.path.basename(result['output_path'])
                    zipf.write(result['output_path'], arcname)
        
        return zip_path
    
    def apply_opencv_filters(self, frame: np.ndarray, settings: ProcessingSettings) -> np.ndarray:
        """Apply OpenCV filters to a frame (alternative method)"""
        processed_frame = frame.copy()
        
        # Brightness and contrast
        if settings.color.brightness != 0 or settings.color.contrast != 0:
            alpha = 1 + (settings.color.contrast / 100.0)  # Contrast
            beta = settings.color.brightness  # Brightness
            processed_frame = cv2.convertScaleAbs(processed_frame, alpha=alpha, beta=beta)
        
        # Saturation
        if settings.color.saturation != 0:
            hsv = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = hsv[:, :, 1] * (1 + settings.color.saturation / 100.0)
            processed_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Blur
        if settings.color.blur > 0:
            kernel_size = int(settings.color.blur / 10) * 2 + 1  # Ensure odd number
            processed_frame = cv2.GaussianBlur(processed_frame, (kernel_size, kernel_size), 0)
        
        # Monochrome
        if settings.color.monochrome:
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        
        # Mirror
        if settings.color.mirrored:
            processed_frame = cv2.flip(processed_frame, 1)
        
        # Noise
        if settings.noise.intensity > 0:
            noise_intensity = settings.noise.intensity / 100.0
            if settings.noise.type == "Gaussian":
                noise = np.random.normal(0, noise_intensity * 25, processed_frame.shape).astype(np.uint8)
                processed_frame = cv2.add(processed_frame, noise)
            elif settings.noise.type == "Salt & Pepper":
                salt_pepper = np.random.random(processed_frame.shape[:2])
                processed_frame[salt_pepper < noise_intensity/2] = 0  # Pepper
                processed_frame[salt_pepper > 1 - noise_intensity/2] = 255  # Salt
        
        return processed_frame
