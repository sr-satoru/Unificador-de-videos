#!/bin/bash

echo "🎬 Iniciando Video Editor System..."
echo "================================="

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "🐍 Iniciando backend Python..."
cd backend
python3 run.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Iniciando frontend React..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Serviços iniciados!"
echo ""
echo "🌐 URLs disponíveis:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📱 WebSocket: ws://localhost:8000/ws/{client_id}"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços..."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
