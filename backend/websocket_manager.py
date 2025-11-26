from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client {client_id} disconnected")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                # Remove the connection if it's broken
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
        
        # Create a list of clients to remove (broken connections)
        clients_to_remove = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                clients_to_remove.append(client_id)
        
        # Remove broken connections
        for client_id in clients_to_remove:
            self.disconnect(client_id)
    
    async def send_progress_update(self, job_id: str, progress: float):
        """Send progress update for a specific job"""
        message = {
            "type": "progress_update",
            "job_id": job_id,
            "progress": progress
        }
        await self.broadcast(message)
    
    async def send_job_completed(self, job_id: str, results: list):
        """Send job completion notification"""
        message = {
            "type": "job_completed",
            "job_id": job_id,
            "status": "completed",
            "results": results
        }
        await self.broadcast(message)
    
    async def send_job_error(self, job_id: str, error: str):
        """Send job error notification"""
        message = {
            "type": "job_error",
            "job_id": job_id,
            "status": "error",
            "error": error
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())
