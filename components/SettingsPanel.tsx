import React from 'react';
import { ProcessingSettings, OutputQuality } from '../types';
import Slider from './ui/Slider';
import Checkbox from './ui/Checkbox';
import Dropdown from './ui/Dropdown';
import { 
    FilterIcon, SunIcon, ContrastIcon, SaturationIcon, BlurIcon, NoiseIcon, MonochromeIcon, MirrorIcon, ClockIcon, SparklesIcon, ExternalLinkIcon, WrenchIcon, DownloadIcon
} from './icons';

interface SettingsPanelProps {
  settings: ProcessingSettings;
  setSettings: React.Dispatch<React.SetStateAction<ProcessingSettings>>;
  onProcess: () => void;
  isProcessing: boolean;
  disabled: boolean;
  onCustomChange: () => void;
  downloadUrl: string | null;
  backendConnected: boolean;
  applyPadrao1: boolean;
  setApplyPadrao1: (value: boolean) => void;
  onPadrao1Toggle: (enabled: boolean) => void;
}

const SettingItem: React.FC<{icon: React.ReactNode, children: React.ReactNode}> = ({ icon, children }) => (
    <div className="flex items-center gap-4">
        <div className="flex-shrink-0 text-gray-500 w-5 h-5">{icon}</div>
        <div className="flex-grow">{children}</div>
    </div>
);


const SettingsPanel: React.FC<SettingsPanelProps> = ({ settings, setSettings, onProcess, isProcessing, disabled, onCustomChange, downloadUrl, backendConnected, applyPadrao1, setApplyPadrao1, onPadrao1Toggle }) => {
  
    const handleSettingChange = (group: keyof ProcessingSettings, field: string, value: any) => {
        setSettings(prev => ({
            ...prev,
            [group]: {
                ...prev[group],
                [field]: value,
            },
        }));
        onCustomChange();
    };
    
    const handleCheckboxChange = (group: keyof ProcessingSettings, field: string, checked: boolean) => {
        handleSettingChange(group, field, checked);
    };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full flex flex-col">
        <h3 className="text-lg font-bold flex items-center gap-2 mb-6">
            <FilterIcon className="w-5 h-5" />
            Filtros de vídeo
        </h3>
        
        <div className="space-y-5 flex-grow">
            <SettingItem icon={<SunIcon />}>
                <Slider label="Brilho" value={settings.color.brightness} onChange={e => handleSettingChange('color', 'brightness', +e.target.value)} min={-100} max={100} displaySuffix="%" />
            </SettingItem>
            <SettingItem icon={<ContrastIcon />}>
                <Slider label="Contraste" value={settings.color.contrast} onChange={e => handleSettingChange('color', 'contrast', +e.target.value)} min={-100} max={100} displaySuffix="%" />
            </SettingItem>
            <SettingItem icon={<SaturationIcon />}>
                <Slider label="Saturação" value={settings.color.saturation} onChange={e => handleSettingChange('color', 'saturation', +e.target.value)} min={-100} max={100} displaySuffix="%" />
            </SettingItem>
             <SettingItem icon={<BlurIcon />}>
                <Slider label="Borrão" value={settings.color.blur} onChange={e => handleSettingChange('color', 'blur', +e.target.value)} min={0} max={100} displaySuffix="%" />
            </SettingItem>
            <SettingItem icon={<NoiseIcon />}>
                <Slider label="Ruído/Grunge" value={settings.noise.intensity} onChange={e => handleSettingChange('noise', 'intensity', +e.target.value)} min={0} max={100} displaySuffix="%" />
            </SettingItem>
            <SettingItem icon={<MonochromeIcon />}>
                <Checkbox label="P/B (Monocromático)" checked={settings.color.monochrome} onChange={e => handleCheckboxChange('color', 'monochrome', e.target.checked)} />
            </SettingItem>
            <SettingItem icon={<MirrorIcon />}>
                <Checkbox label="Espelhado" checked={settings.color.mirrored} onChange={e => handleCheckboxChange('color', 'mirrored', e.target.checked)} />
            </SettingItem>
            <SettingItem icon={<ClockIcon />}>
                <Slider label="Velocidade" value={settings.effects.speed} onChange={e => handleSettingChange('effects', 'speed', +e.target.value)} min={50} max={200} displayValue={`${(settings.effects.speed / 100).toFixed(2)}x`} />
            </SettingItem>
            <SettingItem icon={<SparklesIcon />}>
                 <Dropdown
                    label="Qualidade de Saída"
                    value={settings.output.quality}
                    onChange={e => handleSettingChange('output', 'quality', e.target.value)}
                    options={Object.values(OutputQuality)}
                 />
            </SettingItem>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200 space-y-2">
            {/* Backend Status Indicator */}
            <div className={`text-sm px-3 py-2 rounded-lg flex items-center gap-2 ${
                backendConnected 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
            }`}>
                <div className={`w-2 h-2 rounded-full ${
                    backendConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                {backendConnected ? 'Backend Conectado' : 'Backend Desconectado'}
            </div>

            <div className="mb-4">
                <Checkbox
                    checked={applyPadrao1}
                    onChange={(e) => {
                        const enabled = e.target.checked;
                        setApplyPadrao1(enabled);
                        onPadrao1Toggle(enabled);
                    }}
                    label="Padrão 1"
                />
            </div>

            {downloadUrl ? (
                <a
                    href={downloadUrl}
                    download="videos_processados.zip"
                    className="w-full text-base font-bold px-6 py-3 bg-green-600 text-white rounded-lg shadow-sm hover:bg-green-700 transition-all duration-200 flex items-center justify-center gap-2"
                >
                    <DownloadIcon className="w-5 h-5" />
                    Baixar Arquivos ZIP
                </a>
            ) : (
                <button
                    onClick={onProcess}
                    disabled={disabled || !backendConnected}
                    className="w-full text-base font-bold px-6 py-3 bg-gray-800 text-white rounded-lg shadow-sm hover:bg-gray-900 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
                >
                    <ExternalLinkIcon className={`w-5 h-5 ${isProcessing ? 'animate-spin' : ''}`} />
                    {isProcessing ? 'Processando...' : 'Monitore o resultado'}
                </button>
            )}
             <button
                onClick={() => alert('Função de reportar bug ainda não implementada.')}
                className="w-full text-base font-bold px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-all duration-200 flex items-center justify-center gap-2"
            >
                <WrenchIcon className="w-5 h-5"/> Reportar um bug
            </button>
        </div>
    </div>
  );
};

export default SettingsPanel;