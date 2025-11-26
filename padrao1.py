import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import resize
from moviepy.video.fx.all import crop
import numpy as np
import cv2
import threading

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
    print(f"🌫️ Aplicando blur nos primeiros {duracao_blur}s...")
    
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
    print("🎬 Aplicando padrão complexo...")
    print("📋 Sequência: Blur(2s) → Pausa(2s) → Velocidade 0.9x(1s) → Piscada+Zoom(2s) → Normal(3s) → Piscada sem zoom → Velocidade 0.8x → Normal(2.5s) → Piscada+Zoom(2s)")
    
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

def processar_video_padrao1(video_path, output_path=None):
    """Processa vídeo com Padrão 1: Sequência complexa com blur, velocidades e efeitos"""
    print("🎬 Iniciando processamento com Padrão 1...")
    print("📋 Efeitos: Sequência complexa com blur, velocidades e efeitos variados")
    
    # Verificar se arquivo existe
    if not Path(video_path).exists():
        print(f"❌ Arquivo '{video_path}' não encontrado!")
        return False
    
    # Definir caminho de saída
    if output_path is None:
        input_path = Path(video_path)
        output_path = input_path.parent / f"{input_path.stem}_padrao1{input_path.suffix}"
    
    try:
        # Carregar vídeo
        print("📁 Carregando vídeo...")
        video = VideoFileClip(str(video_path))
        
        print(f"📊 Duração do vídeo: {video.duration:.2f} segundos")
        
        # Aplicar efeito de blur apenas nos primeiros 2 segundos
        video_com_blur = criar_efeito_blur_inicial(
            video, 
            duracao_blur=2.0, 
            intensidade_blur=25
        )
        
        # Aplicar padrão complexo
        video_final = criar_efeito_padrao_complexo(video_com_blur)
        
        # Salvar vídeo editado
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
        video_com_blur.close()
        video_final.close()
        
        print(f"✅ Vídeo editado salvo em: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar vídeo: {e}")
        return False

class Padrao1GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Padrão 1 - Editor de Vídeo")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.minsize(500, 400)  # Tamanho mínimo
        
        # Variáveis
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.is_processing = False
        self.effects_label = None  # Referência para o label de efeitos
        
        self.setup_ui()
        
        # Bind para redimensionamento
        self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_ui(self):
        # Configurar grid principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid do frame principal
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🎬 Padrão 1 - Editor de Vídeo", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Descrição dos efeitos
        effects_frame = ttk.LabelFrame(main_frame, text="Efeitos Aplicados", padding="10")
        effects_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        effects_frame.columnconfigure(0, weight=1)
        
        effects_text = """🌫️ Blur Inicial: Primeiros 2 segundos
⏸️ Pausa: 2 segundos (2-4s)
🐌 Velocidade 0.9x: 1 segundo (4-5s)
👁️ Piscada + Zoom: 2 segundos (5-7s)
▶️ Normal: 3 segundos (7-10s)
👁️ Piscada sem zoom: 0.1s (10s)
🐌 Velocidade 0.8x: 2 segundos (10-12s)
▶️ Normal: 2.5 segundos (12-14.5s)
👁️ Piscada + Zoom: 2 segundos (14.5-16.5s)
🔄 Repetir: A cada 6 segundos"""
        
        self.effects_label = ttk.Label(effects_frame, text=effects_text, justify=tk.LEFT, wraplength=500)
        self.effects_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Seleção de vídeo
        video_frame = ttk.LabelFrame(main_frame, text="Vídeo de Entrada", padding="10")
        video_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        
        ttk.Label(video_frame, text="Arquivo de vídeo:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        video_entry = ttk.Entry(video_frame, textvariable=self.video_path)
        video_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(video_frame, text="📁 Selecionar", 
                  command=self.select_video).grid(row=1, column=1)
        
        # Seleção de saída
        output_frame = ttk.LabelFrame(main_frame, text="Local de Saída", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Label(output_frame, text="Arquivo de saída:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        output_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="📁 Selecionar", 
                  command=self.select_output).grid(row=1, column=1)
        
        # Botão de processamento
        self.process_button = ttk.Button(main_frame, text="🚀 Processar Vídeo", 
                                        command=self.start_processing, style="Accent.TButton")
        self.process_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Pronto para processar", 
                                     foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=3)
    
    def on_window_resize(self, event):
        """Ajusta o wraplength do label de efeitos quando a janela é redimensionada"""
        if event.widget == self.root and self.effects_label:
            # Calcular novo wraplength baseado na largura da janela
            new_width = event.width - 100  # Margem para padding
            if new_width > 200:  # Evitar wraplength muito pequeno
                self.effects_label.config(wraplength=new_width)
    
    def select_video(self):
        """Seleciona arquivo de vídeo"""
        filetypes = [
            ("Arquivos de vídeo", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("MP4", "*.mp4"),
            ("AVI", "*.avi"),
            ("MOV", "*.mov"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecionar vídeo",
            filetypes=filetypes
        )
        
        if filename:
            self.video_path.set(filename)
            # Sugerir nome de saída
            input_path = Path(filename)
            suggested_output = input_path.parent / f"{input_path.stem}_padrao1{input_path.suffix}"
            self.output_path.set(str(suggested_output))
            self.update_status("Vídeo selecionado", "green")
    
    def select_output(self):
        """Seleciona local de saída"""
        filetypes = [
            ("MP4", "*.mp4"),
            ("AVI", "*.avi"),
            ("MOV", "*.mov"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Salvar vídeo processado",
            defaultextension=".mp4",
            filetypes=filetypes
        )
        
        if filename:
            self.output_path.set(filename)
            self.update_status("Local de saída selecionado", "green")
    
    def update_status(self, message, color="black"):
        """Atualiza mensagem de status"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_processing(self):
        """Inicia processamento em thread separada"""
        if not self.video_path.get():
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo!")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Erro", "Selecione um local de saída!")
            return
        
        if self.is_processing:
            return
        
        # Iniciar processamento em thread separada
        self.is_processing = True
        self.process_button.config(state="disabled")
        self.progress.start()
        self.update_status("Processando vídeo...", "blue")
        
        thread = threading.Thread(target=self.process_video_thread)
        thread.daemon = True
        thread.start()
    
    def process_video_thread(self):
        """Thread para processamento do vídeo"""
        try:
            sucesso = processar_video_padrao1(
                self.video_path.get(), 
                self.output_path.get()
            )
            
            # Atualizar UI na thread principal
            self.root.after(0, self.processing_complete, sucesso)
            
        except Exception as e:
            self.root.after(0, self.processing_error, str(e))
    
    def processing_complete(self, sucesso):
        """Chamado quando processamento termina"""
        self.is_processing = False
        self.process_button.config(state="normal")
        self.progress.stop()
        
        if sucesso:
            self.update_status("✅ Processamento concluído com sucesso!", "green")
            messagebox.showinfo("Sucesso", 
                              f"Vídeo processado com sucesso!\n\nSalvo em:\n{self.output_path.get()}")
        else:
            self.update_status("❌ Erro no processamento", "red")
            messagebox.showerror("Erro", "Erro durante o processamento do vídeo!")
    
    def processing_error(self, error_message):
        """Chamado quando há erro no processamento"""
        self.is_processing = False
        self.process_button.config(state="normal")
        self.progress.stop()
        self.update_status("❌ Erro no processamento", "red")
        messagebox.showerror("Erro", f"Erro durante o processamento:\n\n{error_message}")

def main():
    """Função principal - inicia a interface gráfica"""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Criar e executar aplicação
    app = Padrao1GUI(root)
    
    # Deixar o sistema operacional gerenciar a posição da janela
    # Isso evita problemas de posicionamento em diferentes monitores
    
    root.mainloop()

if __name__ == "__main__":
    main()
