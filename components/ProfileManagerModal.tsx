import React, { useState } from 'react';
import { Profile, ProcessingSettings } from '../types';
import Modal from './ui/Modal';
import { TrashIcon, SaveIcon } from './icons';

interface ProfileManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  profiles: Profile[];
  setProfiles: React.Dispatch<React.SetStateAction<Profile[]>>;
  currentSettings: ProcessingSettings;
  onApplyProfile: (profile: Profile) => void;
}

const ProfileManagerModal: React.FC<ProfileManagerModalProps> = ({ isOpen, onClose, profiles, setProfiles, currentSettings, onApplyProfile }) => {
  const [newProfileName, setNewProfileName] = useState('');

  const handleSaveProfile = () => {
    if (newProfileName.trim() === '') return;
    const newProfile: Profile = {
      id: `profile-${Date.now()}`,
      name: newProfileName,
      settings: currentSettings,
    };
    setProfiles(prev => [...prev, newProfile]);
    setNewProfileName('');
  };
  
  const handleDeleteProfile = (id: string) => {
    setProfiles(prev => prev.filter(p => p.id !== id));
  };
  
  const handleApply = (profile: Profile) => {
      onApplyProfile(profile);
      onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Gerenciar Perfis">
        <div className="space-y-6">
            <div>
                <h4 className="text-lg font-semibold text-gray-700 mb-2">Salvar Configuração Atual</h4>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newProfileName}
                        onChange={(e) => setNewProfileName(e.target.value)}
                        placeholder="Nome do novo perfil..."
                        className="flex-grow bg-gray-100 border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <button onClick={handleSaveProfile} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2">
                        <SaveIcon className="w-5 h-5"/> Salvar
                    </button>
                </div>
            </div>

            <div>
                <h4 className="text-lg font-semibold text-gray-700 mb-2">Carregar Perfil Existente</h4>
                {profiles.length > 0 ? (
                    <ul className="space-y-2 max-h-60 overflow-y-auto border border-gray-200 rounded-lg p-2 bg-gray-50">
                        {profiles.map(profile => (
                            <li key={profile.id} className="flex items-center justify-between p-2 rounded-md hover:bg-gray-200">
                                <span className="text-gray-800">{profile.name}</span>
                                <div className="flex gap-2">
                                    <button onClick={() => handleApply(profile)} className="px-3 py-1 text-sm bg-cyan-600 text-white rounded hover:bg-cyan-700">Aplicar</button>
                                    <button onClick={() => handleDeleteProfile(profile.id)} className="p-1.5 text-gray-500 hover:text-red-500">
                                        <TrashIcon className="w-5 h-5" />
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-500 text-center py-4">Nenhum perfil salvo ainda.</p>
                )}
            </div>
        </div>
    </Modal>
  );
};

export default ProfileManagerModal;