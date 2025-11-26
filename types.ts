export enum ProcessingStatus {
  Queued = 'Queued',
  Processing = 'Processing',
  Completed = 'Completed',
  Error = 'Error',
}

export interface VideoFile {
  id: string;
  file: File;
  status: ProcessingStatus;
  progress: number;
  url: string;
}

export enum NoiseType {
  Perlin = 'Perlin',
  Gaussian = 'Gaussian',
  SaltAndPepper = 'Salt & Pepper',
}

export enum ColorPreset {
  None = 'None',
  Vintage = 'Vintage',
  Monochrome = 'Monochrome',
  Vivid = 'Vivid',
}

export enum InsertionMethod {
  LSB = 'LSB - Least Significant Bit',
  FrequencyModulation = 'Subtle Frequency Modulation',
}

export enum OutputQuality {
    Preserve = 'Preservar Original',
    HD = 'HD (720p)',
    FullHD = 'Full HD (1080p)',
}

export interface ProcessingSettings {
  noise: {
    type: NoiseType;
    intensity: number; // This is Ruído/Grunge
  };
  color: {
    brightness: number;
    contrast: number;
    saturation: number;
    blur: number; // New
    monochrome: boolean; // New
    mirrored: boolean; // New
  };
  effects: {
      speed: number; // New, 100 = 1.00x
  };
  steganography: {
    signature: string;
    method: InsertionMethod;
    intensity: number;
  };
  output: {
    quality: OutputQuality;
  };
}

export type PresetName = 'YouTube' | 'Facebook' | 'Instagram' | 'TikTok';

export interface Profile {
  id: string;
  name: string;
  settings: ProcessingSettings;
}