from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime
import logging

from models import ProcessingSettings, VideoFile, ProcessingStatus, NoiseType, InsertionMethod, OutputQuality
from video_processor import VideoProcessor
from websocket_manager import WebSocketManager
from database import db_manager
from cleanup_manager import cleanup_manager
from padrao1_processor import padrao1_processor

# Configure logging - apenas logs importantes
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Logger específico para padrão1 com nível INFO
padrao1_logger = logging.getLogger('padrao1')
padrao1_logger.setLevel(logging.INFO)

# Configurar handler específico para padrão1 com formato limpo
padrao1_handler = logging.StreamHandler()
padrao1_formatter = logging.Formatter('%(message)s')
padrao1_handler.setFormatter(padrao1_formatter)
padrao1_logger.addHandler(padrao1_handler)
padrao1_logger.propagate = False  # Evitar logs duplicados

app = FastAPI(title="Video Editor Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
video_processor = VideoProcessor()
websocket_manager = WebSocketManager()

# Start cleanup service
@app.on_event("startup")
async def startup_event():
    """Start background services on startup"""
    asyncio.create_task(cleanup_manager.start_cleanup_service())
    # Log removido para limpeza
    padrao1_logger.info("🎬 Sistema Padrão 1 inicializado e pronto!")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on shutdown"""
    cleanup_manager.stop_cleanup_service()
    # Log removido para limpeza

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Store for active processing jobs
active_jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    return {"message": "Video Editor Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload")
async def upload_videos(files: List[UploadFile] = File(...)):
    """Upload multiple video files"""
    try:
        uploaded_files = []
        
        for file in files:
            if not file.content_type.startswith('video/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a video")
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{file.filename}"
            file_path = os.path.join("uploads", filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Create video file object
            video_file = VideoFile(
                id=file_id,
                filename=filename,
                original_name=file.filename,
                file_path=file_path,
                status=ProcessingStatus.Queued,
                progress=0,
                size=len(content)
            )
            
            # Add to database
            db_manager.add_file(file_id, file.filename, file_path, len(content))
            
            uploaded_files.append(video_file)
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": [file.model_dump() for file in uploaded_files]
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_videos(
    file_ids: List[str],
    settings: ProcessingSettings
):
    """Start processing videos with given settings"""
    try:
        job_id = str(uuid.uuid4())
        
        # Store job information
        active_jobs[job_id] = {
            "file_ids": file_ids,
            "settings": settings.model_dump(),
            "status": "processing",
            "progress": 0,
            "started_at": datetime.now().isoformat(),
            "results": []
        }
        
        # Add job to database
        db_manager.add_job(job_id, settings.model_dump())
        
        # Update files with job_id
        for file_id in file_ids:
            db_manager.update_file_status(file_id, "processing", job_id)
        
        # Start processing in background
        asyncio.create_task(process_videos_background(job_id, file_ids, settings))
        
        return {
            "job_id": job_id,
            "message": "Processing started",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_videos_background(job_id: str, file_ids: List[str], settings: ProcessingSettings):
    """Background task for video processing"""
    try:
        total_files = len(file_ids)
        
        for i, file_id in enumerate(file_ids):
            # Find the file
            file_path = None
            for filename in os.listdir("uploads"):
                if filename.startswith(file_id):
                    file_path = os.path.join("uploads", filename)
                    break
            
            if not file_path:
                logger.error(f"File not found for ID: {file_id}")
                continue
            
            # Process the video
            output_path = await video_processor.process_video(
                file_path, 
                settings, 
                job_id, 
                file_id,
                progress_callback=lambda progress: update_job_progress(job_id, progress, i, total_files)
            )
            
            # Apply Padrão 1 if enabled
            if padrao1_processor.is_enabled:
                padrao1_logger.info(f"🎬 Aplicando Padrão 1 ao vídeo: {file_id}")
                try:
                    # Generate padrão1 output path
                    base_name = os.path.splitext(os.path.basename(output_path))[0]
                    padrao1_output_path = os.path.join("outputs", f"{base_name}_padrao1.mp4")
                    
                    # Apply padrão1 processing
                    final_output = padrao1_processor.process_video(output_path, padrao1_output_path)
                    
                    # Replace original output with padrão1 output
                    if os.path.exists(final_output):
                        os.replace(final_output, output_path)
                        padrao1_logger.info(f"✅ Padrão 1 aplicado com sucesso: {file_id}")
                    else:
                        padrao1_logger.warning(f"⚠️ Arquivo padrão1 não encontrado: {final_output}")
                        
                except Exception as e:
                    padrao1_logger.error(f"❌ Erro ao aplicar Padrão 1: {e}")
                    # Continue with original video if padrão1 fails
            
            # Store result
            active_jobs[job_id]["results"].append({
                "file_id": file_id,
                "output_path": output_path,
                "status": "completed"
            })
            
            # Update database
            db_manager.update_file_status(file_id, "completed", output_path=output_path)
        
        # Mark job as completed
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        # Update database
        db_manager.update_job_status(job_id, "completed", 100)
        
        # Notify WebSocket clients
        await websocket_manager.broadcast({
            "type": "job_completed",
            "job_id": job_id,
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"Background processing error: {str(e)}")
        active_jobs[job_id]["status"] = "error"
        active_jobs[job_id]["error"] = str(e)
        
        await websocket_manager.broadcast({
            "type": "job_error",
            "job_id": job_id,
            "error": str(e)
        })

def update_job_progress(job_id: str, file_progress: float, file_index: int, total_files: int):
    """Update job progress"""
    if job_id in active_jobs:
        # Calculate overall progress
        base_progress = (file_index / total_files) * 100
        current_file_progress = (file_progress / 100) * (100 / total_files)
        total_progress = base_progress + current_file_progress
        
        active_jobs[job_id]["progress"] = min(total_progress, 100)
        
        # Notify WebSocket clients
        asyncio.create_task(websocket_manager.broadcast({
            "type": "progress_update",
            "job_id": job_id,
            "progress": total_progress
        }))

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]

@app.get("/jobs/{job_id}/download")
async def download_processed_videos(job_id: str):
    """Download processed videos as ZIP"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Create ZIP file with processed videos
    zip_path = await video_processor.create_zip(job["results"])
    
    # Update database with zip path
    db_manager.update_job_status(job_id, "completed", zip_path=zip_path)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"processed_videos_{job_id}.zip"
    )

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

@app.get("/presets")
async def get_presets():
    """Get available presets"""
    return {
        "YouTube": {
            "noise": {"type": "Perlin", "intensity": 0},
            "color": {"brightness": 5, "contrast": 5, "saturation": 10, "blur": 0, "monochrome": False, "mirrored": False},
            "effects": {"speed": 100}
        },
        "Facebook": {
            "noise": {"type": "Perlin", "intensity": 2},
            "color": {"brightness": 0, "contrast": 8, "saturation": 15, "blur": 1, "monochrome": False, "mirrored": False},
            "effects": {"speed": 100}
        },
        "Instagram": {
            "noise": {"type": "Perlin", "intensity": 8},
            "color": {"brightness": 14, "contrast": -9, "saturation": 22, "blur": 5, "monochrome": False, "mirrored": True},
            "effects": {"speed": 90}
        },
        "TikTok": {
            "noise": {"type": "Perlin", "intensity": 13},
            "color": {"brightness": 3, "contrast": 13, "saturation": -17, "blur": 3.2, "monochrome": False, "mirrored": True},
            "effects": {"speed": 120}
        }
    }

@app.get("/cleanup/stats")
async def get_cleanup_stats():
    """Get cleanup statistics and storage usage"""
    try:
        stats = cleanup_manager.get_cleanup_stats()
        storage = cleanup_manager.get_storage_usage()
        
        return {
            "database_stats": stats,
            "storage_usage": storage,
            "cleanup_settings": {
                "upload_cleanup_delay": cleanup_manager.upload_cleanup_delay,
                "zip_cleanup_delay": cleanup_manager.zip_cleanup_delay,
                "processed_video_cleanup_delay": cleanup_manager.processed_video_cleanup_delay,
                "cleanup_interval": cleanup_manager.cleanup_interval
            }
        }
    except Exception as e:
        logger.error(f"Error getting cleanup stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup/force/{job_id}")
async def force_cleanup_job(job_id: str):
    """Force cleanup of all files related to a specific job"""
    try:
        await cleanup_manager.force_cleanup_job(job_id)
        return {"message": f"Force cleanup completed for job {job_id}"}
    except Exception as e:
        logger.error(f"Error in force cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup/manual")
async def manual_cleanup():
    """Trigger manual cleanup cycle"""
    try:
        await cleanup_manager.perform_cleanup_cycle()
        return {"message": "Manual cleanup completed"}
    except Exception as e:
        logger.error(f"Error in manual cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PADRÃO 1 ENDPOINTS =====

@app.post("/padrao1/toggle")
async def toggle_padrao1(data: dict):
    """Ativa ou desativa o Padrão 1"""
    enabled = data.get("enabled", False)
    try:
        padrao1_processor.set_enabled(enabled)
        
        # Log detalhado no terminal
        status = "✅ ATIVADO" if enabled else "❌ DESATIVADO"
        padrao1_logger.info(f"🎬 PADRÃO 1 {status}")
        padrao1_logger.info(f"🎬 Padrão 1 foi {'ativado' if enabled else 'desativado'} pelo usuário")
        padrao1_logger.info(f"📊 Status atual: {'Habilitado' if enabled else 'Desabilitado'}")
        
        return {
            "message": f"Padrão 1 {'ativado' if enabled else 'desativado'} com sucesso",
            "enabled": enabled,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao alterar status do Padrão 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/padrao1/status")
async def get_padrao1_status():
    """Obtém o status atual do Padrão 1"""
    try:
        status = padrao1_processor.is_enabled
        padrao1_logger.info(f"📊 Consulta de status do Padrão 1: {'Ativo' if status else 'Inativo'}")
        
        return {
            "enabled": status,
            "timestamp": datetime.now().isoformat(),
            "message": "Padrão 1 está ativo" if status else "Padrão 1 está inativo"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao consultar status do Padrão 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/padrao1/process")
async def process_with_padrao1(file_id: str):
    """Processa um vídeo específico com Padrão 1"""
    try:
        if not padrao1_processor.is_enabled:
            logger.warning("⚠️ Tentativa de processar com Padrão 1 desativado")
            raise HTTPException(status_code=400, detail="Padrão 1 está desativado")
        
        # Encontrar o arquivo
        file_path = None
        for filename in os.listdir("uploads"):
            if filename.startswith(file_id):
                file_path = os.path.join("uploads", filename)
                break
        
        if not file_path:
            logger.error(f"❌ Arquivo não encontrado para ID: {file_id}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        padrao1_logger.info(f"🎬 Iniciando processamento com Padrão 1 para arquivo: {file_id}")
        
        # Gerar caminho de saída
        input_path = Path(file_path)
        output_path = str(Path("outputs") / f"{file_id}_padrao1{input_path.suffix}")
        
        # Processar vídeo
        result_path = padrao1_processor.process_video(file_path, output_path)
        
        padrao1_logger.info(f"✅ Processamento com Padrão 1 concluído: {result_path}")
        
        return {
            "message": "Vídeo processado com Padrão 1 com sucesso",
            "file_id": file_id,
            "output_path": result_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento com Padrão 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

