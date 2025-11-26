// API service for backend integration
const API_BASE_URL = 'http://localhost:8000';

export interface VideoFileResponse {
  id: string;
  filename: string;
  original_name: string;
  file_path: string;
  status: string;
  progress: number;
  size: number;
  created_at?: string;
  processed_at?: string;
}

export interface ProcessingSettingsRequest {
  noise: {
    type: string;
    intensity: number;
  };
  color: {
    brightness: number;
    contrast: number;
    saturation: number;
    blur: number;
    monochrome: boolean;
    mirrored: boolean;
  };
  effects: {
    speed: number;
  };
  steganography: {
    signature: string;
    method: string;
    intensity: number;
  };
  output: {
    quality: string;
  };
}

export interface JobResponse {
  job_id: string;
  message: string;
  status: string;
}

export interface JobStatus {
  job_id: string;
  file_ids: string[];
  settings: ProcessingSettingsRequest;
  status: string;
  progress: number;
  started_at: string;
  completed_at?: string;
  results: Array<{
    file_id: string;
    output_path: string;
    status: string;
  }>;
  error?: string;
}

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  static async uploadVideos(files: File[]): Promise<VideoFileResponse[]> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload Error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data.files;
  }

  static async processVideos(
    fileIds: string[],
    settings: ProcessingSettingsRequest
  ): Promise<JobResponse> {
    return this.request<JobResponse>('/process', {
      method: 'POST',
      body: JSON.stringify({
        file_ids: fileIds,
        settings: settings,
      }),
    });
  }

  static async getJobStatus(jobId: string): Promise<JobStatus> {
    return this.request<JobStatus>(`/jobs/${jobId}`);
  }

  static async downloadProcessedVideos(jobId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/download`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Download Error: ${response.status} - ${errorText}`);
    }

    return response.blob();
  }

  static async getPresets(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/presets');
  }

  static getDownloadUrl(jobId: string): string {
    return `${API_BASE_URL}/jobs/${jobId}/download`;
  }
}

export default ApiService;
