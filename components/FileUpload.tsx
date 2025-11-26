import React, { useRef, useState, useCallback } from 'react';
import { UploadCloudIcon } from './icons';

interface FileUploadProps {
  onFilesAdded: (files: File[]) => void;
  label: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFilesAdded, label }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = useCallback((files: FileList | null) => {
    if (files && files.length > 0) {
      const fileArray = Array.from(files);
      onFilesAdded(fileArray);
    }
  }, [onFilesAdded]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    // Reset input value to allow uploading the same file again
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-4 transition-colors ${
        isDragOver 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept="video/*"
        className="hidden"
        onChange={handleChange}
      />
      <button 
        onClick={onButtonClick} 
        className={`w-full font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${
          isDragOver
            ? 'bg-blue-100 text-blue-700'
            : 'bg-gray-200 hover:bg-gray-300 text-gray-600'
        }`}
        aria-label={`${label}, selecione arquivos para enviar`}
      >
        <UploadCloudIcon className="w-5 h-5" />
        {isDragOver ? 'Solte os arquivos aqui' : label}
      </button>
      <p className="text-xs text-gray-500 mt-2 text-center">
        Arraste e solte múltiplos vídeos ou clique para selecionar
      </p>
    </div>
  );
};

export default FileUpload;