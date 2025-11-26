#!/bin/bash

echo "🎬 Instalando Video Editor Backend..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg não encontrado. Instalando..."
    
    # Detect OS and install FFmpeg
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        else
            echo "❌ Gerenciador de pacotes não suportado. Instale FFmpeg manualmente."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew não encontrado. Instale FFmpeg manualmente."
            exit 1
        fi
    else
        echo "❌ Sistema operacional não suportado. Instale FFmpeg manualmente."
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Instalando dependências Python..."
cd backend
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências Python."
    exit 1
fi

# Create necessary directories
echo "📁 Criando diretórios necessários..."
mkdir -p uploads outputs temp

# Make run script executable
chmod +x run.py

echo "✅ Instalação concluída!"
echo ""
echo "🚀 Para executar o backend:"
echo "   cd backend"
echo "   python3 run.py"
echo ""
echo "🌐 O servidor estará disponível em:"
echo "   - API: http://localhost:8000"
echo "   - Documentação: http://localhost:8000/docs"
echo "   - WebSocket: ws://localhost:8000/ws/{client_id}"
echo ""
echo "📚 Para executar o frontend:"
echo "   npm run dev"
