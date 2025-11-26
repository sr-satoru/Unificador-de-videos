import React from 'react';
import { VideoFile, ProcessingStatus } from '../types';
import { TrashIcon, CheckCircleIcon, XCircleIcon, ClockIcon } from './icons';

interface FileListProps {
  files: VideoFile[];
  onRemoveFile: (id: string) => void;
  onSelectFile: (file: VideoFile) => void;
  selectedFileId?: string;
}

const FileListItem: React.FC<{ 
    file: VideoFile; 
    onRemove: () => void;
    onSelect: () => void;
    isSelected: boolean;
}> = ({ file, onRemove, onSelect, isSelected }) => {
    // FIX: Refactor to move title attribute to parent div to fix type errors.
    const getStatusInfo = () => {
        switch (file.status) {
            case ProcessingStatus.Completed:
                return { icon: <CheckCircleIcon className="w-4 h-4 text-green-500" />, title: 'Concluído' };
            case ProcessingStatus.Error:
                return { icon: <XCircleIcon className="w-4 h-4 text-red-500" />, title: 'Erro' };
            case ProcessingStatus.Processing:
                return { icon: <div className="w-4 h-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />, title: 'Processando' };
            default:
                return { icon: <ClockIcon className="w-4 h-4 text-gray-400" />, title: 'Na fila' };
        }
    };
    
    const { icon, title } = getStatusInfo();

    return (
        <li 
          className={`flex items-center gap-3 p-2 rounded-md cursor-pointer transition-colors ${isSelected ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
          onClick={onSelect}
        >
            <div className="flex-shrink-0" title={title}>{icon}</div>
            <div className="flex-grow min-w-0">
                <p className="text-sm font-medium truncate text-gray-700">{file.file.name}</p>
                 {file.status === ProcessingStatus.Processing && (
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                        <div
                            className="h-1 bg-blue-500 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                        ></div>
                    </div>
                 )}
            </div>
            <div className="flex-shrink-0">
                <button onClick={(e) => { e.stopPropagation(); onRemove(); }} className="p-1 text-gray-400 hover:text-red-500 rounded-full hover:bg-gray-200 transition-colors" aria-label={`Remover ${file.file.name}`}>
                    <TrashIcon className="w-4 h-4" />
                </button>
            </div>
        </li>
    );
};


const FileList: React.FC<FileListProps> = ({ files, onRemoveFile, onSelectFile, selectedFileId }) => {
  if (files.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-200 rounded-lg text-center">
        <p className="text-gray-500 font-medium">Sua fila está vazia.</p>
        <p className="text-sm text-gray-400">Envie um vídeo para começar.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col border border-gray-200 rounded-lg">
        <h2 className="text-base font-semibold p-3 border-b border-gray-200 text-gray-600 flex-shrink-0">Fila de Vídeos</h2>
        <ul className="space-y-1 p-2 overflow-y-auto flex-grow">
            {files.map(file => (
                <FileListItem 
                  key={file.id} 
                  file={file} 
                  onRemove={() => onRemoveFile(file.id)}
                  onSelect={() => onSelectFile(file)}
                  isSelected={file.id === selectedFileId}
                />
            ))}
        </ul>
    </div>
  );
};

export default FileList;