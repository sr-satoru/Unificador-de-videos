import React from 'react';
import { PresetName } from '../types';
import { YouTubeIcon, FacebookIcon, InstagramIcon, TikTokIcon } from './icons';

interface PresetsProps {
    onSelect: (preset: PresetName) => void;
    activePreset: PresetName | null;
}

const presetOptions: { name: PresetName; icon: React.ReactNode; }[] = [
    { name: 'YouTube', icon: <YouTubeIcon className="w-6 h-6" /> },
    { name: 'Facebook', icon: <FacebookIcon className="w-6 h-6" /> },
    { name: 'Instagram', icon: <InstagramIcon className="w-6 h-6" /> },
    { name: 'TikTok', icon: <TikTokIcon className="w-6 h-6" /> },
];

const Presets: React.FC<PresetsProps> = ({ onSelect, activePreset }) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-center font-semibold text-gray-600 mb-4">Predefinições</h3>
            <div className="flex justify-around items-center">
                {presetOptions.map(({ name, icon }) => (
                    <button
                        key={name}
                        onClick={() => onSelect(name)}
                        className="flex-1 flex flex-col items-center gap-2 text-gray-700 hover:text-pink-500 transition-colors group"
                        aria-label={`Aplicar predefinição ${name}`}
                    >
                        <div className="flex items-center gap-2">
                            {icon}
                            <span className="font-medium text-sm sm:text-base">{name}</span>
                        </div>
                        <div className={`w-3/4 h-1 rounded-full ${activePreset === name ? 'bg-pink-500' : 'bg-gray-200 group-hover:bg-pink-200'}`} />
                    </button>
                ))}
            </div>
        </div>
    );
};

export default Presets;
