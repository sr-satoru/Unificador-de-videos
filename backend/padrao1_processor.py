import os
from pathlib import Path
from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video import fx as vfx
import numpy as np
import cv2
import logging

# Logger específico para padrão1
logger = logging.getLogger('padrao1')

def aplicar_blur_customizado(get_frame, t, blur_intensity=10):
    """Aplica blur customizado usando OpenCV"""
    frame = get_frame(t)
    
    # Converter para o formato que o OpenCV espera (BGR)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Aplicar blur gaussiano
    blurred = cv2.GaussianBlur(frame_bgr, (blur_intensity*2+1, blur_intensity*2+1), 0)
    
    # Converter de volta para RGB
    frame_rgb = cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)
    
    return frame_rgb

def criar_efeito_blur_inicial(video, duracao_blur=2.0, intensidade_blur=30):
    """Aplica efeito de blur apenas nos primeiros X segundos"""
    logger.info(f"🌫️ Aplicando blur nos primeiros {duracao_blur}s...")
    
    def aplicar_blur_inicial(get_frame, t):
        frame = get_frame(t)
        
        # Aplicar blur apenas nos primeiros segundos
        if t < duracao_blur:
            # Aplicar blur
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            blurred = cv2.GaussianBlur(frame_bgr, (intensidade_blur*2+1, intensidade_blur*2+1), 0)
            frame_rgb = cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)
            return frame_rgb
        else:
            # Sem blur
            return frame
    
    return video.fl(aplicar_blur_inicial)

def criar_efeito_padrao_complexo(video):
    """Aplica padrão complexo com diferentes velocidades e efeitos"""
    logger.info("🎬 Aplicando padrão complexo...")
    logger.info("📋 Sequência: Blur(2s) → Pausa(2s) → Velocidade 0.9x(1s) → Piscada+Zoom(2s) → Normal(3s) → Piscada sem zoom → Velocidade 0.8x → Normal(2.5s) → Piscada+Zoom(2s)")
    
    def aplicar_padrao_complexo(get_frame, t):
        frame = get_frame(t)
        
        # Sequência de efeitos baseada no tempo
        if t < 2.0:
            # 0-2s: Blur (já aplicado anteriormente)
            return frame
        elif t < 4.0:
            # 2-4s: Vídeo normal (pausa)
            return frame
        elif t < 5.0:
            # 4-5s: Velocidade 0.9x (1 segundo)
            # Nota: A velocidade será aplicada no processamento do vídeo
            return frame
        elif t < 5.1:
            # 5.0-5.1s: Piscada (0.1s)
            h, w = frame.shape[:2]
            black_frame = np.zeros((h, w, 3), dtype=np.uint8)
            return black_frame
        elif t < 7.1:
            # 5.1-7.1s: Zoom instantâneo (2s)
            h, w = frame.shape[:2]
            zoom_factor = 1.4
            new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
            
            # Centralizar
            start_h = (h - new_h) // 2
            start_w = (w - new_w) // 2
            
            # Redimensionar e centralizar
            zoomed = frame[start_h:start_h+new_h, start_w:start_w+new_w]
            zoomed_resized = np.array(zoomed)
            
            # Redimensionar de volta para o tamanho original
            from PIL import Image
            img = Image.fromarray(zoomed_resized)
            img_resized = img.resize((w, h), Image.LANCZOS)
            
            return np.array(img_resized)
        elif t < 10.1:
            # 7.1-10.1s: Vídeo normal (3s)
            return frame
        elif t < 10.2:
            # 10.1-10.2s: Piscada sem zoom (0.1s)
            h, w = frame.shape[:2]
            black_frame = np.zeros((h, w, 3), dtype=np.uint8)
            return black_frame
        elif t < 12.2:
            # 10.2-12.2s: Velocidade 0.8x (2s)
            # Nota: A velocidade será aplicada no processamento do vídeo
            return frame
        elif t < 14.7:
            # 12.2-14.7s: Vídeo normal (2.5s)
            return frame
        elif t < 14.8:
            # 14.7-14.8s: Piscada (0.1s)
            h, w = frame.shape[:2]
            black_frame = np.zeros((h, w, 3), dtype=np.uint8)
            return black_frame
        elif t < 16.8:
            # 14.8-16.8s: Zoom instantâneo (2s)
            h, w = frame.shape[:2]
            zoom_factor = 1.4
            new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
            
            # Centralizar
            start_h = (h - new_h) // 2
            start_w = (w - new_w) // 2
            
            # Redimensionar e centralizar
            zoomed = frame[start_h:start_h+new_h, start_w:start_w+new_w]
            zoomed_resized = np.array(zoomed)
            
            # Redimensionar de volta para o tamanho original
            from PIL import Image
            img = Image.fromarray(zoomed_resized)
            img_resized = img.resize((w, h), Image.LANCZOS)
            
            return np.array(img_resized)
        else:
            # Após 16.8s: Repetir padrão a cada 6 segundos
            tempo_no_ciclo = (t - 16.8) % 6.0
            
            if tempo_no_ciclo < 0.1:
                # Piscada
                h, w = frame.shape[:2]
                black_frame = np.zeros((h, w, 3), dtype=np.uint8)
                return black_frame
            elif tempo_no_ciclo < 2.1:
                # Zoom (2s)
                h, w = frame.shape[:2]
                zoom_factor = 1.4
                new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
                
                # Centralizar
                start_h = (h - new_h) // 2
                start_w = (w - new_w) // 2
                
                # Redimensionar e centralizar
                zoomed = frame[start_h:start_h+new_h, start_w:start_w+new_w]
                zoomed_resized = np.array(zoomed)
                
                # Redimensionar de volta para o tamanho original
                from PIL import Image
                img = Image.fromarray(zoomed_resized)
                img_resized = img.resize((w, h), Image.LANCZOS)
                
                return np.array(img_resized)
            else:
                # Vídeo normal
                return frame
    
    return video.fl(aplicar_padrao_complexo)

class Padrao1Processor:
    """Processador para aplicar o Padrão 1 nos vídeos"""
    
    def __init__(self):
        self.is_enabled = False
        logger.info("🎬 Padrao1Processor inicializado")
    
    def set_enabled(self, enabled: bool):
        """Ativa ou desativa o processamento do Padrão 1"""
        self.is_enabled = enabled
        logger.info(f"🎬 Padrão 1 {'ativado' if enabled else 'desativado'}")
    
    def process_video(self, video_path: str, output_path: str = None, progress_callback=None):
        """Processa vídeo com Padrão 1: Sequência complexa com blur, velocidades e efeitos"""
        if not self.is_enabled:
            logger.info("🎬 Padrão 1 desativado, retornando vídeo original")
            return video_path
        
        logger.info("🎬 Iniciando processamento com Padrão 1...")
        logger.info("📋 Efeitos: Sequência complexa com blur, velocidades e efeitos variados")
        
        # Verificar se arquivo existe
        if not Path(video_path).exists():
            logger.error(f"❌ Arquivo '{video_path}' não encontrado!")
            raise FileNotFoundError(f"Arquivo não encontrado: {video_path}")
        
        # Definir caminho de saída
        if output_path is None:
            input_path = Path(video_path)
            output_path = str(input_path.parent / f"{input_path.stem}_padrao1{input_path.suffix}")
        
        try:
            # Carregar vídeo
            logger.info("📁 Carregando vídeo...")
            video = VideoFileClip(str(video_path))
            
            logger.info(f"📊 Duração do vídeo: {video.duration:.2f} segundos")
            
            # Aplicar efeito de blur apenas nos primeiros 2 segundos
            video_com_blur = criar_efeito_blur_inicial(
                video, 
                duracao_blur=2.0, 
                intensidade_blur=25
            )
            
            # Aplicar padrão complexo
            video_final = criar_efeito_padrao_complexo(video_com_blur)
            
            # Salvar vídeo editado
            logger.info("💾 Salvando vídeo editado...")
            video_final.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Fechar clips
            video.close()
            video_com_blur.close()
            video_final.close()
            
            logger.info(f"✅ Vídeo editado salvo em: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar vídeo: {e}")
            raise e

# Instância global do processador
padrao1_processor = Padrao1Processor()
