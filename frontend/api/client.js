// API Client para comunicação com o backend
const API_BASE_URL = window.location.origin;

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        console.log('🌐 API Client inicializado com baseURL:', this.baseURL);
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...options.headers,
            },
        };
        
        // Só adicionar Content-Type se não for FormData
        if (!(options.body instanceof FormData) && !config.headers['Content-Type']) {
            config.headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP error! status: ${response.status}`);
            }

            // Se a resposta não tiver conteúdo, retornar null
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return null;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        return this.request('/api/health');
    }

    // Upload de vídeos
    async uploadVideos(files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${this.baseURL}/api/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    // Processar vídeos
    async processVideos(fileIds, settings) {
        return this.request('/api/process', {
            method: 'POST',
            body: JSON.stringify({
                file_ids: fileIds,
                settings: settings
            }),
        });
    }

    // Obter status do job
    async getJobStatus(jobId) {
        return this.request(`/api/jobs/${jobId}`);
    }

    // Download de vídeos processados
    async downloadProcessedVideos(jobId) {
        const url = `${this.baseURL}/api/jobs/${jobId}/download`;
        window.location.href = url;
    }

    // Obter presets
    async getPresets() {
        return this.request('/api/presets');
    }

    // Padrão 1 - Toggle
    async togglePadrao1(enabled) {
        return this.request('/api/padrao1/toggle', {
            method: 'POST',
            body: JSON.stringify({ enabled }),
        });
    }

    // Padrão 1 - Status
    async getPadrao1Status() {
        return this.request('/api/padrao1/status');
    }

    // WebSocket connection
    connectWebSocket(clientId, onMessage) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket conectado');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (onMessage) {
                    onMessage(data);
                }
            } catch (error) {
                console.error('Erro ao processar mensagem WebSocket:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('Erro WebSocket:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket desconectado');
        };

        return ws;
    }
}

// Instância global do cliente API
const apiClient = new APIClient();

