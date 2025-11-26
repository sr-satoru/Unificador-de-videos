from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"

class NoiseType(str, Enum):
    Perlin = "Perlin"
    Gaussian = "Gaussian"
    SaltAndPepper = "Salt & Pepper"

class InsertionMethod(str, Enum):
    LSB = "LSB - Least Significant Bit"
    FrequencyModulation = "Subtle Frequency Modulation"

class OutputQuality(str, Enum):
    Preserve = "Preservar Original"
    HD = "HD (720p)"
    FullHD = "Full HD (1080p)"

class NoiseSettings(BaseModel):
    type: NoiseType
    intensity: int  # 0-100

class ColorSettings(BaseModel):
    brightness: int  # -100 to 100
    contrast: int    # -100 to 100
    saturation: int # -100 to 100
    blur: int        # 0 to 100
    monochrome: bool
    mirrored: bool

class EffectsSettings(BaseModel):
    speed: int  # 50 to 200 (50 = 0.5x, 100 = 1.0x, 200 = 2.0x)

class SteganographySettings(BaseModel):
    signature: str
    method: InsertionMethod
    intensity: int  # 0-100

class OutputSettings(BaseModel):
    quality: OutputQuality

class ProcessingSettings(BaseModel):
    noise: NoiseSettings
    color: ColorSettings
    effects: EffectsSettings
    steganography: SteganographySettings
    output: OutputSettings

class VideoFile(BaseModel):
    id: str
    filename: str
    original_name: str
    file_path: str
    status: ProcessingStatus
    progress: int  # 0-100
    size: int
    created_at: Optional[str] = None
    processed_at: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    file_ids: List[str]
    settings: ProcessingSettings
    status: str
    progress: int
    started_at: str
    completed_at: Optional[str] = None
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None
