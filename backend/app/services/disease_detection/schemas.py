from pydantic import BaseModel, Field
from typing import List

class DiseasePrediction(BaseModel):
    crop: str
    disease: str
    probability: float = Field(..., description="Raw softmax probability [0.0, 1.0]. Not calibrated confidence.")
    is_healthy: bool

class EngineMetadata(BaseModel):
    model_version: str = "V6.6"
    architecture: str = "ResNet-18"
    num_classes: int = 12
    training_seed: int = 42
    training_data: str = "PlantVillage + PlantDoc"
    external_benchmark_classes: int = 11

class DiseaseDetectionResult(BaseModel):
    predictions: List[DiseasePrediction]
    inference_time_ms: float
    metadata: EngineMetadata
