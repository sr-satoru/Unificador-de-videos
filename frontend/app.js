// Design System - Video Modifier App

// Estado da aplicação
const state = {
    files: [],
    selectedFile: null,
    activePreset: null,
    currentJobId: null,
    websocket: null,
    backendConnected: false,
    settings: {
        brightness: 0,
        contrast: 0,
        saturation: 0,
        blur: 0,
        noise: 0,
        monochrome: false,
        mirrored: false,
        speed: 100,
        quality: 'Preserve'
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    await checkBackendConnection();
    await initializePadrao1();
    initializeFileUploads();
    initializeSettings();
    initializePresets();
    updateVideoFilters();
    initializeWebSocket();
});

// Verificar conexão com backend
async function checkBackendConnection() {
    try {
        console.log('🔍 Verificando conexão com backend...');
        const response = await apiClient.healthCheck();
        console.log('✅ Backend conectado:', response);
        state.backendConnected = true;
        updateConnectionStatus(true);
    } catch (error) {
        console.error('❌ Erro ao conectar com backend:', error);
        state.backendConnected = false;
        updateConnectionStatus(false);
    }
}

// Inicializar Padrão 1
async function initializePadrao1() {
    try {
        const status = await apiClient.getPadrao1Status();
        const padrao1Checkbox = document.getElementById('padrao1');
        if (padrao1Checkbox) {
            padrao1Checkbox.checked = status.enabled;
            console.log('🎬 Padrão 1 status:', status.enabled ? 'Ativo' : 'Inativo');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar status do Padrão 1:', error);
    }
}

// Atualizar status de conexão
function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.status-indicator');
    if (statusIndicator) {
        if (connected) {
            statusIndicator.classList.remove('status-disconnected');
            statusIndicator.classList.add('status-connected');
            statusIndicator.querySelector('span').textContent = 'Backend Conectado';
        } else {
            statusIndicator.classList.remove('status-connected');
            statusIndicator.classList.add('status-disconnected');
            statusIndicator.querySelector('span').textContent = 'Backend Desconectado';
        }
    }
}

// Inicializar WebSocket
function initializeWebSocket() {
    const clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    state.websocket = apiClient.connectWebSocket(clientId, (data) => {
        handleWebSocketMessage(data);
    });
}

// Processar mensagens WebSocket
function handleWebSocketMessage(data) {
    if (data.type === 'progress_update' && data.job_id === state.currentJobId) {
        // Atualizar progresso dos arquivos
        const progress = data.progress;
        state.files.forEach(file => {
            if (file.status === 'processing') {
                file.progress = progress;
            }
        });
        updateFileList();
    } else if (data.type === 'job_completed' && data.job_id === state.currentJobId) {
        // Job concluído
        state.files.forEach(file => {
            if (file.status === 'processing') {
                file.status = 'completed';
                file.progress = 100;
            }
        });
        updateFileList();
        showDownloadButton(data.job_id);
    } else if (data.type === 'job_error') {
        alert(`Erro no processamento: ${data.error}`);
    }
}

// File Upload
function initializeFileUploads() {
    const uploadAreas = ['uploadArea1', 'uploadArea2'];
    const fileInputs = ['fileInput1', 'fileInput2'];
    
    uploadAreas.forEach((areaId, index) => {
        const area = document.getElementById(areaId);
        const input = document.getElementById(fileInputs[index]);
        
        // Drag and drop
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('drag-over');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('drag-over');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });
        
        // File input change
        input.addEventListener('change', (e) => {
            handleFiles(e.target.files);
            e.target.value = ''; // Reset para permitir selecionar o mesmo arquivo novamente
        });
    });
}

async function handleFiles(files) {
    const videoFiles = Array.from(files).filter(file => file.type.startsWith('video/'));
    
    if (videoFiles.length === 0) {
        alert('Por favor, selecione apenas arquivos de vídeo.');
        return;
    }

    try {
        // Upload para o backend
        const response = await apiClient.uploadVideos(videoFiles);
        
        // Adicionar arquivos ao estado
        response.files.forEach(uploadedFile => {
            const fileObj = {
                id: uploadedFile.id,
                file: videoFiles.find(f => f.name === uploadedFile.original_name),
                url: URL.createObjectURL(videoFiles.find(f => f.name === uploadedFile.original_name)),
                status: 'queued',
                progress: 0,
                backendId: uploadedFile.id,
                originalName: uploadedFile.original_name
            };
            
            state.files.push(fileObj);
            
            if (!state.selectedFile) {
                state.selectedFile = fileObj;
                updateVideoPreview();
            }
        });
        
        updateFileList();
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        alert(`Erro ao fazer upload: ${error.message}`);
    }
}

function updateFileList() {
    const fileListContainer = document.getElementById('fileList');
    
    if (state.files.length === 0) {
        fileListContainer.className = 'file-list-empty';
        fileListContainer.innerHTML = `
            <p class="empty-text">Sua fila está vazia.</p>
            <p class="empty-subtext">Envie um vídeo para começar.</p>
        `;
        return;
    }
    
    fileListContainer.className = 'file-list';
    fileListContainer.innerHTML = `
        <div class="file-list-header">Fila de Vídeos</div>
        <div class="file-list-items">
            ${state.files.map(file => `
                <div class="file-item ${state.selectedFile?.id === file.id ? 'selected' : ''}" 
                     onclick="selectFile('${file.id}')">
                    <div class="file-item-info">
                        <div class="file-item-name">${escapeHtml(file.file.name)}</div>
                        ${file.status === 'processing' ? `
                            <div class="file-item-progress">
                                <div class="file-item-progress-bar" style="width: ${file.progress}%"></div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="file-item-actions">
                        <button class="file-item-button" onclick="event.stopPropagation(); removeFile('${file.id}')">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.134-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.067-2.09 1.02-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                            </svg>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function selectFile(fileId) {
    state.selectedFile = state.files.find(f => f.id === fileId);
    updateFileList();
    updateVideoPreview();
}

function removeFile(fileId) {
    const file = state.files.find(f => f.id === fileId);
    if (file) {
        URL.revokeObjectURL(file.url);
    }
    
    state.files = state.files.filter(f => f.id !== fileId);
    
    if (state.selectedFile?.id === fileId) {
        state.selectedFile = state.files.length > 0 ? state.files[0] : null;
        updateVideoPreview();
    }
    
    updateFileList();
}

// Video Preview
function updateVideoPreview() {
    const videoPlayer = document.getElementById('videoPlayer');
    const videoContainer = document.getElementById('videoContainer');
    const videoWrapper = document.getElementById('videoWrapper');
    const placeholder = videoContainer.querySelector('.video-placeholder');
    
    if (state.selectedFile) {
        videoPlayer.src = state.selectedFile.url;
        if (videoWrapper) videoWrapper.style.display = 'block';
        if (placeholder) placeholder.style.display = 'none';
        
        videoPlayer.onloadedmetadata = () => {
            const aspectRatio = videoPlayer.videoWidth / videoPlayer.videoHeight;
            videoContainer.style.aspectRatio = `${videoPlayer.videoWidth} / ${videoPlayer.videoHeight}`;
        };
    } else {
        if (videoWrapper) videoWrapper.style.display = 'none';
        if (placeholder) placeholder.style.display = 'flex';
        videoContainer.style.aspectRatio = '16 / 9';
    }
    
    updateVideoFilters();
}

function updateVideoFilters() {
    const videoPlayer = document.getElementById('videoPlayer');
    if (!videoPlayer || !state.selectedFile) return;
    
    const filters = [
        `brightness(${100 + state.settings.brightness}%)`,
        `contrast(${100 + state.settings.contrast}%)`,
        `saturate(${100 + state.settings.saturation}%)`,
        `blur(${state.settings.blur / 10}px)`,
        `grayscale(${state.settings.monochrome ? 1 : 0})`
    ];
    
    videoPlayer.style.filter = filters.join(' ');
    
    // Aplicar espelhamento no vídeo e reverter nos controles
    if (state.settings.mirrored) {
        videoPlayer.classList.add('video-mirrored');
    } else {
        videoPlayer.classList.remove('video-mirrored');
    }
    
    videoPlayer.playbackRate = state.settings.speed / 100;
}

// Settings
function initializeSettings() {
    // Sliders
    const sliders = ['brightness', 'contrast', 'saturation', 'blur', 'noise', 'speed'];
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                state.settings[id] = value;
                updateSliderValue(id, value);
                updateVideoFilters();
            });
        }
    });
    
    // Checkboxes
    const checkboxes = ['monochrome', 'mirrored'];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                state.settings[id] = e.target.checked;
                updateVideoFilters();
            });
        }
    });
    
    // Padrão 1 toggle
    const padrao1Checkbox = document.getElementById('padrao1');
    if (padrao1Checkbox) {
        padrao1Checkbox.addEventListener('change', async (e) => {
            const enabled = e.target.checked;
            try {
                await apiClient.togglePadrao1(enabled);
                console.log(`🎬 Padrão 1 ${enabled ? 'ativado' : 'desativado'}`);
            } catch (error) {
                console.error('❌ Erro ao alterar Padrão 1:', error);
                // Reverter checkbox em caso de erro
                padrao1Checkbox.checked = !enabled;
                alert(`Erro ao ${enabled ? 'ativar' : 'desativar'} Padrão 1: ${error.message}`);
            }
        });
    }
    
    // Dropdown
    const quality = document.getElementById('quality');
    if (quality) {
        quality.addEventListener('change', (e) => {
            state.settings.quality = e.target.value;
        });
    }
    
    // Process button
    const processButton = document.getElementById('processButton');
    if (processButton) {
        processButton.addEventListener('click', async () => {
            await processVideos();
        });
    }
    
    // Inicializar valores
    updateSliderValue('brightness', 0);
    updateSliderValue('contrast', 0);
    updateSliderValue('saturation', 0);
    updateSliderValue('blur', 0);
    updateSliderValue('noise', 0);
    updateSliderValue('speed', 100);
}

function updateSliderValue(id, value) {
    const valueElement = document.getElementById(id + 'Value');
    if (!valueElement) return;
    
    if (id === 'speed') {
        valueElement.textContent = `${(value / 100).toFixed(2)}x`;
    } else {
        valueElement.textContent = `${value}%`;
    }
}

// Presets
async function initializePresets() {
    try {
        // Carregar presets do backend
        const presets = await apiClient.getPresets();
        
        const presetButtons = document.querySelectorAll('.preset-button');
        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const preset = button.dataset.preset;
                applyPreset(preset, presets);
            });
        });
    } catch (error) {
        console.error('Erro ao carregar presets:', error);
        // Usar presets padrão se falhar
        const presetButtons = document.querySelectorAll('.preset-button');
        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const preset = button.dataset.preset;
                applyPreset(preset);
            });
        });
    }
}

function applyPreset(presetName, backendPresets = null) {
    state.activePreset = presetName;
    
    // Atualizar botões
    document.querySelectorAll('.preset-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.preset === presetName) {
            btn.classList.add('active');
        }
    });
    
    // Usar presets do backend se disponível, senão usar padrão
    let preset;
    if (backendPresets && backendPresets[presetName]) {
        const backendPreset = backendPresets[presetName];
        preset = {
            brightness: backendPreset.color?.brightness || 0,
            contrast: backendPreset.color?.contrast || 0,
            saturation: backendPreset.color?.saturation || 0,
            blur: backendPreset.color?.blur || 0,
            noise: backendPreset.noise?.intensity || 0,
            speed: backendPreset.effects?.speed || 100,
            monochrome: backendPreset.color?.monochrome || false,
            mirrored: backendPreset.color?.mirrored || false
        };
    } else {
        // Presets padrão
        const defaultPresets = {
            YouTube: { brightness: 5, contrast: 5, saturation: 10, blur: 0, noise: 0, speed: 100, monochrome: false, mirrored: false },
            Facebook: { brightness: 0, contrast: 8, saturation: 15, blur: 1, noise: 2, speed: 100, monochrome: false, mirrored: false },
            Instagram: { brightness: 14, contrast: -9, saturation: 22, blur: 5, noise: 8, speed: 90, monochrome: false, mirrored: true },
            TikTok: { brightness: 3, contrast: 13, saturation: -17, blur: 3.2, noise: 13, speed: 120, monochrome: false, mirrored: true }
        };
        preset = defaultPresets[presetName];
    }
    
    if (preset) {
        Object.keys(preset).forEach(key => {
            state.settings[key] = preset[key];
            const slider = document.getElementById(key);
            const checkbox = document.getElementById(key);
            if (slider) {
                slider.value = preset[key];
                updateSliderValue(key, preset[key]);
            } else if (checkbox) {
                checkbox.checked = preset[key];
            }
        });
        
        updateVideoFilters();
    }
}

// Processar vídeos
async function processVideos() {
    if (state.files.length === 0) {
        alert('Por favor, faça upload de pelo menos um vídeo.');
        return;
    }

    // Preparar configurações para o backend
    const processingSettings = {
        noise: {
            type: "Perlin",
            intensity: state.settings.noise
        },
        color: {
            brightness: state.settings.brightness,
            contrast: state.settings.contrast,
            saturation: state.settings.saturation,
            blur: state.settings.blur,
            monochrome: state.settings.monochrome,
            mirrored: state.settings.mirrored
        },
        effects: {
            speed: state.settings.speed
        },
        steganography: {
            signature: "",
            method: "LSB - Least Significant Bit",
            intensity: 0
        },
        output: {
            quality: state.settings.quality === 'Preserve' ? 'Preservar Original' : 
                    state.settings.quality === 'High' ? 'HD (720p)' :
                    state.settings.quality === 'Medium' ? 'Full HD (1080p)' : 'Preservar Original'
        }
    };

    // Obter IDs dos arquivos do backend
    const fileIds = state.files
        .filter(file => file.backendId)
        .map(file => file.backendId);

    if (fileIds.length === 0) {
        alert('Nenhum arquivo válido para processar.');
        return;
    }

    try {
        const processButton = document.getElementById('processButton');
        if (processButton) {
            processButton.disabled = true;
            processButton.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Processando...
            `;
            processButton.onclick = null; // Remove previous download handler
        }

        // Atualizar status dos arquivos
        state.files.forEach(file => {
            if (file.backendId && fileIds.includes(file.backendId)) {
                file.status = 'processing';
                file.progress = 0;
            }
        });
        updateFileList();

        // Iniciar processamento
        const response = await apiClient.processVideos(fileIds, processingSettings);
        state.currentJobId = response.job_id;

        alert(`Processamento iniciado! Job ID: ${response.job_id}`);
    } catch (error) {
        console.error('Erro ao processar vídeos:', error);
        alert(`Erro ao processar vídeos: ${error.message}`);
        
        // Reverter status dos arquivos
        state.files.forEach(file => {
            if (file.status === 'processing') {
                file.status = 'queued';
            }
        });
        updateFileList();
    } finally {
        const processButton = document.getElementById('processButton');
        if (processButton) {
            processButton.disabled = false;
            processButton.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-4.5 0V6.375c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0110.5 10.5z" />
                </svg>
                Iniciar edição
            `;
        }
    }
}

// Show download button when processing is complete
function showDownloadButton(jobId) {
    const processButton = document.getElementById('processButton');
    if (processButton) {
        // Remove existing event listeners by cloning the button
        const newButton = processButton.cloneNode(true);
        processButton.parentNode.replaceChild(newButton, processButton);
        
        newButton.disabled = false;
        newButton.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Baixar vídeos processados
        `;
        newButton.addEventListener('click', () => {
            apiClient.downloadProcessedVideos(jobId);
        });
    }
}

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Expor funções globalmente para uso em onclick
window.selectFile = selectFile;
window.removeFile = removeFile;

