// Design System - Video Modifier App

// Estado da aplicação
const state = {
    files: [],
    selectedFile: null,
    activePreset: null,
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
document.addEventListener('DOMContentLoaded', () => {
    initializeFileUploads();
    initializeSettings();
    initializePresets();
    updateVideoFilters();
});

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

function handleFiles(files) {
    Array.from(files).forEach(file => {
        if (file.type.startsWith('video/')) {
            const fileObj = {
                id: Date.now() + Math.random(),
                file: file,
                url: URL.createObjectURL(file),
                status: 'queued',
                progress: 0
            };
            
            state.files.push(fileObj);
            
            if (!state.selectedFile) {
                state.selectedFile = fileObj;
                updateVideoPreview();
            }
        }
    });
    
    updateFileList();
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
    const placeholder = videoContainer.querySelector('.video-placeholder');
    
    if (state.selectedFile) {
        videoPlayer.src = state.selectedFile.url;
        videoPlayer.style.display = 'block';
        if (placeholder) placeholder.style.display = 'none';
        
        videoPlayer.onloadedmetadata = () => {
            const aspectRatio = videoPlayer.videoWidth / videoPlayer.videoHeight;
            videoContainer.style.aspectRatio = `${videoPlayer.videoWidth} / ${videoPlayer.videoHeight}`;
        };
    } else {
        videoPlayer.style.display = 'none';
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
    videoPlayer.style.transform = `scaleX(${state.settings.mirrored ? -1 : 1})`;
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
        processButton.addEventListener('click', () => {
            alert('Funcionalidade de processamento não implementada nesta versão do design system.');
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
function initializePresets() {
    const presetButtons = document.querySelectorAll('.preset-button');
    presetButtons.forEach(button => {
        button.addEventListener('click', () => {
            const preset = button.dataset.preset;
            applyPreset(preset);
        });
    });
}

function applyPreset(presetName) {
    state.activePreset = presetName;
    
    // Atualizar botões
    document.querySelectorAll('.preset-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.preset === presetName) {
            btn.classList.add('active');
        }
    });
    
    // Aplicar configurações do preset
    const presets = {
        YouTube: { brightness: 5, contrast: 5, saturation: 10, blur: 0, noise: 0, speed: 100 },
        Facebook: { brightness: 0, contrast: 8, saturation: 15, blur: 1, noise: 2, speed: 100 },
        Instagram: { brightness: 14, contrast: -9, saturation: 22, blur: 5, noise: 8, speed: 90 },
        TikTok: { brightness: 3, contrast: 13, saturation: -17, blur: 3.2, noise: 13, speed: 120 }
    };
    
    const preset = presets[presetName];
    if (preset) {
        Object.keys(preset).forEach(key => {
            state.settings[key] = preset[key];
            const slider = document.getElementById(key);
            if (slider) {
                slider.value = preset[key];
                updateSliderValue(key, preset[key]);
            }
        });
        
        updateVideoFilters();
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

