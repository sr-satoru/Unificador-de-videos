import React, { useState, useCallback, useEffect } from 'react';
import {
  ProcessingSettings,
  VideoFile,
  ProcessingStatus,
  NoiseType,
  InsertionMethod,
  Profile,
  PresetName,
  OutputQuality,
} from './types';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import SettingsPanel from './components/SettingsPanel';
import VideoPreview from './components/VideoPreview';
import Presets from './components/Presets';
import { useLocalStorage } from './hooks/useLocalStorage';
import ApiService from './services/api';
import { websocketService, WebSocketMessage } from './services/websocket';

const defaultSettings: ProcessingSettings = {
  noise: {
    type: NoiseType.Perlin,
    intensity: 0,
  },
  color: {
    brightness: 0,
    contrast: 0,
    saturation: 0,
    blur: 0,
    monochrome: false,
    mirrored: false,
  },
  effects: {
    speed: 100, // Represents 1.00x
  },
  steganography: {
    signature: '',
    method: InsertionMethod.LSB,
    intensity: 50,
  },
  output: {
    quality: OutputQuality.Preserve,
  }
};

const PRESET_SETTINGS: Record<PresetName, Partial<ProcessingSettings>> = {
  YouTube: {
    noise: { type: NoiseType.Perlin, intensity: 0 },
    color: { brightness: 5, contrast: 5, saturation: 10, blur: 0, monochrome: false, mirrored: false },
    effects: { speed: 100 },
  },
  Facebook: {
    noise: { type: NoiseType.Perlin, intensity: 2 },
    color: { brightness: 0, contrast: 8, saturation: 15, blur: 1, monochrome: false, mirrored: false },
    effects: { speed: 100 },
  },
  Instagram: {
    noise: { type: NoiseType.Perlin, intensity: 8 },
    color: {
      brightness: 14,
      contrast: -9,
      saturation: 22,
      blur: 5,
      monochrome: false,
      mirrored: true,
    },
    effects: { speed: 90 },
  },
  TikTok: {
    noise: { type: NoiseType.Perlin, intensity: 13 },
    color: {
      brightness: 3,
      contrast: 13,
      saturation: -17,
      blur: 3.2,
      monochrome: false,
      mirrored: true,
    },
    effects: { speed: 120 },
  },
};

const App: React.FC = () => {
  const [videoFiles, setVideoFiles] = useState<VideoFile[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoFile | null>(null);
  const [settings, setSettings] = useState<ProcessingSettings>(defaultSettings);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [profiles, setProfiles] = useLocalStorage<Profile[]>('video-modifier-profiles', []);
  const [activePreset, setActivePreset] = useState<PresetName | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [applyPadrao1, setApplyPadrao1] = useState<boolean>(false);

  // WebSocket connection and message handling
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        await websocketService.connect();
        setBackendConnected(true);
        console.log('WebSocket connected');
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setBackendConnected(false);
      }
    };

    connectWebSocket();

    // Handle WebSocket messages
    const handleWebSocketMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'progress_update':
          if (message.job_id === currentJobId && message.progress !== undefined) {
            setVideoFiles(prevFiles =>
              prevFiles.map(f => ({
                ...f,
                progress: message.progress!,
                status: ProcessingStatus.Processing
              }))
            );
          }
          break;
        case 'job_completed':
          if (message.job_id === currentJobId) {
            setVideoFiles(prevFiles =>
              prevFiles.map(f => ({
                ...f,
                status: ProcessingStatus.Completed,
                progress: 100
              }))
            );
            setIsProcessing(false);
            setDownloadUrl(ApiService.getDownloadUrl(currentJobId!));
          }
          break;
        case 'job_error':
          if (message.job_id === currentJobId) {
            setVideoFiles(prevFiles =>
              prevFiles.map(f => ({
                ...f,
                status: ProcessingStatus.Error
              }))
            );
            setIsProcessing(false);
            alert(`Erro no processamento: ${message.error}`);
          }
          break;
      }
    };

    websocketService.addMessageHandler(handleWebSocketMessage);

    return () => {
      websocketService.removeMessageHandler(handleWebSocketMessage);
      websocketService.disconnect();
    };
  }, [currentJobId]);

  const handleFilesAdded = useCallback(async (files: File[]) => {
    try {
      // Upload files to backend
      const uploadedFiles = await ApiService.uploadVideos(files);
      
      const newVideoFiles: VideoFile[] = uploadedFiles.map(uploadedFile => ({
        id: uploadedFile.id,
        file: files.find(f => f.name === uploadedFile.original_name)!,
        status: ProcessingStatus.Queued,
        progress: 0,
        url: URL.createObjectURL(files.find(f => f.name === uploadedFile.original_name)!),
      }));
      
      setVideoFiles(prevFiles => {
        const updatedFiles = [...prevFiles, ...newVideoFiles];
        if (!selectedVideo && updatedFiles.length > 0) {
          setSelectedVideo(updatedFiles[0]);
        }
        return updatedFiles;
      });
      
      // Reset download button when new files are added
      if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl);
        setDownloadUrl(null);
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Erro ao fazer upload dos arquivos. Verifique se o backend está rodando.');
    }
  }, [selectedVideo, downloadUrl]);

  const handleFileRemoved = useCallback((id: string) => {
    setVideoFiles(prevFiles => {
      const remainingFiles = prevFiles.filter(file => file.id !== id);
      if (selectedVideo?.id === id) {
        setSelectedVideo(remainingFiles.length > 0 ? remainingFiles[0] : null);
      }
      return remainingFiles;
    });
  }, [selectedVideo]);

  const handleProcessVideos = async () => {
    const filesToProcess = videoFiles.filter(f => f.status === ProcessingStatus.Queued || f.status === ProcessingStatus.Error);
    if (isProcessing || filesToProcess.length === 0) return;
    
    if (!backendConnected) {
      alert('Backend não conectado. Verifique se o servidor está rodando.');
      return;
    }
    
    // Revoke previous URL if it exists
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      setDownloadUrl(null);
    }

    try {
      setIsProcessing(true);
      
      // Convert settings to backend format
      const backendSettings = {
        noise: {
          type: settings.noise.type,
          intensity: settings.noise.intensity
        },
        color: {
          brightness: settings.color.brightness,
          contrast: settings.color.contrast,
          saturation: settings.color.saturation,
          blur: settings.color.blur,
          monochrome: settings.color.monochrome,
          mirrored: settings.color.mirrored
        },
        effects: {
          speed: settings.effects.speed
        },
        steganography: {
          signature: settings.steganography.signature,
          method: settings.steganography.method,
          intensity: settings.steganography.intensity
        },
        output: {
          quality: settings.output.quality
        },
        padrao1: applyPadrao1
      };

      // Start processing job
      const jobResponse = await ApiService.processVideos(
        filesToProcess.map(f => f.id),
        backendSettings
      );
      
      setCurrentJobId(jobResponse.job_id);
      
      // Update files to processing status
      setVideoFiles(prevFiles =>
        prevFiles.map(f =>
          filesToProcess.some(pf => pf.id === f.id)
            ? { ...f, status: ProcessingStatus.Processing }
            : f
        )
      );
      
    } catch (error) {
      console.error('Error processing videos:', error);
      setIsProcessing(false);
      alert('Erro ao processar vídeos. Verifique se o backend está rodando.');
    }
  };

  const handlePadrao1Toggle = async (enabled: boolean) => {
    try {
      const response = await fetch('http://localhost:8000/padrao1/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('🎬 Padrão 1 status updated:', result);
        setApplyPadrao1(enabled);
      } else {
        console.error('Erro ao alterar status do Padrão 1');
        alert('Erro ao alterar status do Padrão 1');
      }
    } catch (error) {
      console.error('Erro na comunicação com o backend:', error);
      alert('Erro na comunicação com o backend');
    }
  };
  
  const handleApplyProfile = (profile: Profile) => {
    setSettings(profile.settings);
    setActivePreset(null);
  };
  
  const handlePresetSelect = (presetName: PresetName) => {
    const presetSettings = PRESET_SETTINGS[presetName];
    
    setSettings(prev => ({
        ...defaultSettings, // Reset to default before applying preset
        ...prev,
        noise: { ...prev.noise, ...presetSettings.noise },
        color: { ...prev.color, ...presetSettings.color },
        effects: { ...prev.effects, ...presetSettings.effects },
    }));
    setActivePreset(presetName);
  };

  const handleCustomSettingChange = () => {
    if (activePreset) {
      setActivePreset(null);
    }
  };

  return (
    <div className="min-h-screen font-sans p-4 sm:p-6 lg:p-8">
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-screen-2xl mx-auto">
        
        <div className="lg:col-span-3 bg-white rounded-lg shadow-md p-4 flex flex-col gap-4">
          <div className="flex-shrink-0">
             <h3 className="font-bold text-sm mb-2 text-gray-500 uppercase tracking-wider">▷ Baixe o padrão</h3>
             <FileUpload onFilesAdded={handleFilesAdded} label="Vídeo principal" />
          </div>
          <div className="flex-shrink-0">
            <h3 className="font-bold text-sm mb-2 text-gray-500 uppercase tracking-wider">▷ Processamento de acordo com o padrão</h3>
            <FileUpload onFilesAdded={handleFilesAdded} label="Vídeos adicionais"/>
          </div>
          
          <div className="flex-grow min-h-0">
            <FileList files={videoFiles} onRemoveFile={handleFileRemoved} onSelectFile={setSelectedVideo} selectedFileId={selectedVideo?.id}/>
          </div>
        </div>
        
        <div className="lg:col-span-5 flex flex-col gap-4">
          <VideoPreview video={selectedVideo} settings={settings} />
          <Presets onSelect={handlePresetSelect} activePreset={activePreset} />
        </div>
        
        <div className="lg:col-span-4">
          <SettingsPanel 
            settings={settings} 
            setSettings={setSettings}
            onProcess={handleProcessVideos}
            isProcessing={isProcessing}
            disabled={isProcessing || videoFiles.filter(f => f.status === ProcessingStatus.Queued || f.status === ProcessingStatus.Error).length === 0}
            onCustomChange={handleCustomSettingChange}
            downloadUrl={downloadUrl}
            backendConnected={backendConnected}
            applyPadrao1={applyPadrao1}
            setApplyPadrao1={setApplyPadrao1}
            onPadrao1Toggle={handlePadrao1Toggle}
          />
        </div>
      </main>
    </div>
  );
};

export default App;
