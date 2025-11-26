from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import asyncio
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from models import ProcessingSettings, VideoFile, ProcessingStatus
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
video_processor = VideoProcessor()
websocket_manager = WebSocketManager()

@app.on_event("startup")
async def startup_event():
    """Start background services on startup"""
    asyncio.create_task(cleanup_manager.start_cleanup_service())
    padrao1_logger.info("🎬 Sistema Padrão 1 inicializado e pronto!")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background services on shutdown"""
    cleanup_manager.stop_cleanup_service()

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Configurar caminho do frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Store for active processing jobs
active_jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload")
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

@app.post("/api/process")
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
                padrao1_logger.info(f"🎬 Aplicando Padrão 1 ao vídeo processado: {file_id}")
                try:
                    # Criar caminho temporário para o vídeo com Padrão 1
                    base_name = os.path.splitext(os.path.basename(output_path))[0]
                    padrao1_output_path = os.path.join("outputs", f"{base_name}_padrao1.mp4")
                    
                    # Processar vídeo com Padrão 1
                    final_output = padrao1_processor.process_video(output_path, padrao1_output_path)
                    
                    # Verificar se o arquivo foi criado corretamente
                    if os.path.exists(final_output) and os.path.getsize(final_output) > 0:
                        # Remover o arquivo original processado
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        
                        # Renomear o arquivo com Padrão 1 para o nome original
                        os.rename(final_output, output_path)
                        padrao1_logger.info(f"✅ Padrão 1 aplicado com sucesso: {file_id}")
                        padrao1_logger.info(f"📁 Arquivo final: {output_path}")
                    else:
                        padrao1_logger.warning(f"⚠️ Arquivo Padrão 1 não foi criado corretamente, mantendo vídeo original")
                except Exception as e:
                    padrao1_logger.error(f"❌ Erro ao aplicar Padrão 1: {e}")
                    padrao1_logger.error(f"📁 Mantendo vídeo processado original: {output_path}")
                    # Continuar com o vídeo original se o Padrão 1 falhar
            
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
        
        # Create ZIP file automatically with processed videos
        logger.info(f"📦 Criando arquivo ZIP para job {job_id}...")
        try:
            zip_path = await video_processor.create_zip(active_jobs[job_id]["results"])
            active_jobs[job_id]["zip_path"] = zip_path
            logger.info(f"✅ ZIP criado com sucesso: {zip_path}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar ZIP: {e}")
            zip_path = None
        
        # Update database
        db_manager.update_job_status(job_id, "completed", 100, zip_path=zip_path)
        
        # Notify WebSocket clients
        await websocket_manager.broadcast({
            "type": "job_completed",
            "job_id": job_id,
            "status": "completed",
            "zip_ready": zip_path is not None
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

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]

@app.get("/api/jobs/{job_id}/download")
async def download_processed_videos(job_id: str):
    """Download processed videos as ZIP"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Use existing ZIP file if available
    zip_path = job.get("zip_path")
    
    # If ZIP doesn't exist, create it
    if not zip_path or not os.path.exists(zip_path):
        logger.info(f"📦 Criando ZIP para download do job {job_id}...")
        zip_path = await video_processor.create_zip(job["results"])
        active_jobs[job_id]["zip_path"] = zip_path
        db_manager.update_job_status(job_id, "completed", zip_path=zip_path)
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=500, detail="ZIP file not found")
    
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

@app.get("/api/presets")
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

# ===== PADRÃO 1 ENDPOINTS =====

@app.post("/api/padrao1/toggle")
async def toggle_padrao1(data: dict):
    """Ativa ou desativa o Padrão 1"""
    enabled = data.get("enabled", False)
    try:
        padrao1_processor.set_enabled(enabled)
        status = "✅ ATIVADO" if enabled else "❌ DESATIVADO"
        padrao1_logger.info(f"🎬 PADRÃO 1 {status}")
        
        return {
            "message": f"Padrão 1 {'ativado' if enabled else 'desativado'} com sucesso",
            "enabled": enabled,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erro ao alterar status do Padrão 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/padrao1/status")
async def get_padrao1_status():
    """Obtém o status atual do Padrão 1"""
    try:
        status = padrao1_processor.is_enabled
        return {
            "enabled": status,
            "timestamp": datetime.now().isoformat(),
            "message": "Padrão 1 está ativo" if status else "Padrão 1 está inativo"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao consultar status do Padrão 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Servir frontend estático - deve ser a última rota
if FRONTEND_DIR.exists():
    # Rota raiz - servir index.html
    @app.get("/")
    async def serve_index():
        """Serve index.html"""
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    # Servir arquivos estáticos (CSS, JS, imagens, etc.)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files"""
        # Primeiro, verificar se é um arquivo estático do frontend
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Se não for arquivo estático, verificar se é rota da API do backend
        if full_path.startswith("api/") and not (FRONTEND_DIR / full_path).exists():
            # É uma rota da API do backend, não servir frontend
            raise HTTPException(status_code=404, detail="Not found")
        
        # Ignorar outras rotas do FastAPI
        if full_path.startswith("docs") or full_path.startswith("openapi.json") or \
           full_path.startswith("redoc") or full_path.startswith("ws/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Se não encontrar, servir index.html (para SPA routing)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Carregar variáveis de ambiente
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Obter porta e host das variáveis de ambiente (sem fallback)
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    uvicorn.run(app, host=host, port=port)

