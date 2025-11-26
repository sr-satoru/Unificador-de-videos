import React, { useMemo, useRef, useEffect, useState } from 'react';
import { VideoFile, ProcessingSettings } from '../types';
import { PlayIcon, CreomixerIcon } from './icons';

interface VideoPreviewProps {
  video: VideoFile | null;
  settings: ProcessingSettings;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({ video, settings }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [aspectRatio, setAspectRatio] = useState('16 / 9');

  // Apply visual filters and transformations via CSS
  // FIX: Explicitly type the return value as React.CSSProperties to resolve
  // the type mismatch for the 'objectFit' property.
  const videoStyle = useMemo((): React.CSSProperties => {
    const filters = [
      `brightness(${100 + settings.color.brightness}%)`,
      `contrast(${100 + settings.color.contrast}%)`,
      `saturate(${100 + settings.color.saturation}%)`,
      `blur(${settings.color.blur / 10}px)`,
      `grayscale(${settings.color.monochrome ? 1 : 0})`,
    ];

    return {
      filter: filters.join(' '),
      transform: `scaleX(${settings.color.mirrored ? -1 : 1})`,
      width: '100%',
      height: '100%',
      objectFit: 'contain',
    };
  }, [settings]);

  // Apply playback speed
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = settings.effects.speed / 100;
    }
  }, [settings.effects.speed]);

  // Dynamically set aspect ratio from video metadata
  const handleMetadata = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    const { videoWidth, videoHeight } = e.currentTarget;
    if (videoWidth > 0 && videoHeight > 0) {
      setAspectRatio(`${videoWidth} / ${videoHeight}`);
    }
  };
  
  // Reset aspect ratio if video is removed
  useEffect(() => {
    if (!video) {
      setAspectRatio('16 / 9');
    }
  }, [video]);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <CreomixerIcon className="w-6 h-6 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-800">Creomixer 0.9f Beta</h2>
      </div>
      <div 
        className="relative flex-grow bg-black rounded flex items-center justify-center w-full"
        style={{ aspectRatio }}
      >
        {video ? (
          <>
            <video 
              ref={videoRef}
              key={video.id} 
              controls 
              style={videoStyle}
              className="rounded" 
              loop
              onLoadedMetadata={handleMetadata}
            >
              <source src={video.url} type={video.file.type} />
              Seu navegador não suporta a tag de vídeo.
            </video>
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                opacity: settings.noise.intensity / 100,
                backgroundImage: `url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(%23noise)"/></svg>')`,
                mixBlendMode: 'overlay',
              }}
            />
          </>
        ) : (
          <div className="text-center text-gray-500 flex flex-col items-center">
            <PlayIcon className="w-24 h-24 text-gray-300" />
            <p className="mt-2 font-medium">Nenhum vídeo selecionado</p>
            <p className="text-sm">Envie um vídeo para começar</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPreview;