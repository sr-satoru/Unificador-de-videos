import os
from pathlib import Path
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import resize
from moviepy.video.fx.all import crop
import numpy as np
import cv2

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

def criar_efeito_desfoque(video, duracao=2):
    """Aplica efeito de desfoque por 2 segundos"""
    print("🌫️ Aplicando efeito de desfoque...")
    
    # Pegar os primeiros 2 segundos
    inicio = video.subclip(0, min(duracao, video.duration))
    
    # Aplicar desfoque usando nossa função customizada (50% mais forte)
    inicio_desfocado = inicio.fl(lambda get_frame, t: aplicar_blur_customizado(get_frame, t, blur_intensity=37))
    
    # Resto do vídeo sem efeito
    resto = video.subclip(duracao) if video.duration > duracao else None
    
    # Combinar
    if resto:
        return CompositeVideoClip([inicio_desfocado, resto.set_start(duracao)])
    else:
        return inicio_desfocado

def criar_efeito_zoom(video, inicio_zoom=4.0, duracao_zoom=1.0):
    """Aplica efeito de zoom com piscar de olhos (blackout transition)"""
    print("🔍 Aplicando efeito de zoom com piscar de olhos (início aos 4s)...")
    
    # Timing do efeito
    blackout_entrada = 0.05   # 50ms de blackout na entrada
    duracao_hold = duracao_zoom  # 1 segundo mantendo zoom
    blackout_saida = 0.05    # 50ms de blackout na saída
    
    inicio_blackout_entrada = inicio_zoom
    fim_blackout_entrada = inicio_zoom + blackout_entrada
    inicio_hold = fim_blackout_entrada
    fim_hold = inicio_hold + duracao_hold
    inicio_blackout_saida = fim_hold
    fim_blackout_saida = inicio_blackout_saida + blackout_saida
    
    # Criar zoom com efeito de piscar de olhos
    def fazer_zoom(get_frame, t):
        frame = get_frame(t)
        
        # Calcular fator de zoom e efeito de blackout
        if t < inicio_zoom:
            # Antes do zoom, sem efeito
            zoom_factor = 1.0
            blackout = False
        elif t < fim_blackout_entrada:
            # Blackout de entrada (50ms) - tela escura
            zoom_factor = 1.4
            blackout = True
        elif t < fim_hold:
            # Mantém zoom por 1 segundo (sem blackout)
            zoom_factor = 1.4
            blackout = False
        elif t < fim_blackout_saida:
            # Blackout de saída (50ms) - tela escura
            zoom_factor = 1.0
            blackout = True
        else:
            # Depois do zoom, volta ao normal
            zoom_factor = 1.0
            blackout = False
        
        # Aplicar blackout (tela escura)
        if blackout:
            # Criar frame preto
            h, w = frame.shape[:2]
            black_frame = np.zeros((h, w, 3), dtype=np.uint8)
            return black_frame
        
        # Aplicar zoom
        h, w = frame.shape[:2]
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
    
    return video.fl(fazer_zoom)

def processar_video():
    """Processa o arquivo midia.mp4 com os efeitos"""
    print("🎬 Iniciando processamento do vídeo...")
    
    # Verificar se midia.mp4 existe
    video_path = Path("midia.mp4")
    if not video_path.exists():
        print("❌ Arquivo 'midia.mp4' não encontrado!")
        return False
    
    # Criar pasta output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Carregar vídeo
        print("📁 Carregando vídeo...")
        video = VideoFileClip(str(video_path))
        
        print(f"📊 Duração do vídeo: {video.duration:.2f} segundos")
        
        # Aplicar efeito de desfoque (2 segundos)
        video_com_desfoque = criar_efeito_desfoque(video, duracao=2)
        
        # Aplicar efeito de zoom
        video_final = criar_efeito_zoom(video_com_desfoque)
        
        # Salvar vídeo editado
        output_path = output_dir / "midia_editado.mp4"
        print("💾 Salvando vídeo editado...")
        
        video_final.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Fechar clips
        video.close()
        video_com_desfoque.close()
        video_final.close()
        
        print(f"✅ Vídeo editado salvo em: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar vídeo: {e}")
        return False

def main():
    """Função principal"""
    print("🎬 Automação de Edição de Vídeo")
    print("=" * 40)
    print("📁 Procurando arquivo: midia.mp4")
    print("🎯 Efeitos: Desfoque forte (2s) + Zoom com piscar de olhos (4s-5s)")
    print("📂 Saída: pasta 'output'")
    print("=" * 40)
    
    sucesso = processar_video()
    
    if sucesso:
        print("\n🎉 Processamento concluído com sucesso!")
        print("📁 Verifique a pasta 'output' para o vídeo editado")
    else:
        print("\n❌ Erro no processamento")

if __name__ == "__main__":
    main()