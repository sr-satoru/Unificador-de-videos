# Video Editor Backend

Backend em Python para processamento de vídeos em tempo real com FastAPI, OpenCV e FFmpeg.

## 🚀 Funcionalidades

- **Upload de múltiplos vídeos** - Suporte a vários formatos de vídeo
- **Processamento em tempo real** - Aplicação de filtros e efeitos
- **WebSocket** - Atualizações de progresso em tempo real
- **Filtros avançados** - Brilho, contraste, saturação, blur, ruído
- **Efeitos especiais** - Velocidade, espelhamento, monocromático
- **Presets** - YouTube, Facebook, Instagram, TikTok
- **Qualidade configurável** - HD, Full HD, preservar original
- **Download em ZIP** - Resultados processados

## 📋 Pré-requisitos

- Python 3.8+
- FFmpeg instalado no sistema
- OpenCV
- FastAPI

## 🛠️ Instalação

1. **Instalar FFmpeg** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

2. **Instalar dependências Python**:
```bash
cd backend
pip install -r requirements.txt
```

## 🏃‍♂️ Execução

```bash
# Executar o servidor
python run.py

# Ou diretamente com uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

O servidor estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/{client_id}

## 📡 Endpoints da API

### Upload de Vídeos
```http
POST /upload
Content-Type: multipart/form-data

files: [arquivos de vídeo]
```

### Processamento
```http
POST /process
Content-Type: application/json

{
  "file_ids": ["id1", "id2"],
  "settings": {
    "noise": {"type": "Perlin", "intensity": 10},
    "color": {"brightness": 5, "contrast": 5, "saturation": 10, "blur": 0, "monochrome": false, "mirrored": false},
    "effects": {"speed": 100},
    "steganography": {"signature": "", "method": "LSB", "intensity": 50},
    "output": {"quality": "Preservar Original"}
  }
}
```

### Status do Job
```http
GET /jobs/{job_id}
```

### Download
```http
GET /jobs/{job_id}/download
```

### Presets
```http
GET /presets
```

## 🔌 WebSocket

Conecte-se ao WebSocket para receber atualizações em tempo real:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'progress_update':
      console.log(`Progresso: ${data.progress}%`);
      break;
    case 'job_completed':
      console.log('Processamento concluído!');
      break;
    case 'job_error':
      console.error('Erro:', data.error);
      break;
  }
};
```

## 🎨 Filtros Disponíveis

### Ajustes de Cor
- **Brilho**: -100% a +100%
- **Contraste**: -100% a +100%
- **Saturação**: -100% a +100%
- **Blur**: 0% a 100%

### Efeitos
- **Velocidade**: 0.5x a 2.0x
- **Monocromático**: P/B
- **Espelhado**: Horizontal flip

### Ruído
- **Perlin**: Ruído orgânico
- **Gaussian**: Ruído suave
- **Salt & Pepper**: Ruído pontual

### Qualidade de Saída
- **Preservar Original**: Mantém resolução original
- **HD (720p)**: Reduz para 720p
- **Full HD (1080p)**: Reduz para 1080p

## 📁 Estrutura de Arquivos

```
backend/
├── main.py              # Aplicação principal FastAPI
├── models.py            # Modelos Pydantic
├── video_processor.py   # Processamento de vídeo
├── websocket_manager.py # Gerenciamento WebSocket
├── run.py              # Script de execução
├── requirements.txt    # Dependências Python
└── README.md           # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na pasta backend:

```env
# Configurações do servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Configurações de processamento
MAX_FILE_SIZE=500MB
TEMP_DIR=temp
OUTPUT_DIR=outputs
UPLOAD_DIR=uploads

# Configurações FFmpeg
FFMPEG_PRESET=medium
FFMPEG_CRF=23
```

## 🐛 Troubleshooting

### Erro: FFmpeg não encontrado
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Baixe de https://ffmpeg.org/download.html
```

### Erro: OpenCV não instalado
```bash
pip install opencv-python
```

### Erro: Porta em uso
```bash
# Encontrar processo usando a porta
lsof -i :8000

# Matar processo
kill -9 <PID>
```

## 📊 Monitoramento

O backend inclui logs detalhados para monitoramento:

- **Upload**: Log de arquivos recebidos
- **Processamento**: Progresso em tempo real
- **WebSocket**: Conexões e mensagens
- **Erros**: Detalhes de falhas

## 🚀 Deploy

### Docker (Recomendado)
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

### Produção
```bash
# Usar Gunicorn para produção
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.
