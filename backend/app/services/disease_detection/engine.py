import json
import os
import time
import torch
import torch.nn as nn
from torchvision import models
import torch.nn.functional as F

from .exceptions import ModelLoadError, EngineInferenceError
from .preprocessor import ImagePreprocessor
from .schemas import DiseasePrediction, DiseaseDetectionResult, EngineMetadata

class DiseaseDetectionEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DiseaseDetectionEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path: str = None, mapping_path: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        from pathlib import Path
        backend_dir = Path(__file__).resolve().parent.parent.parent.parent
        default_model = str(backend_dir / "ml_assets" / "models" / "robust_best_model.pth")
        default_mapping = str(backend_dir / "ml_assets" / "class_mapping.json")

        self.model_path = model_path or os.getenv("AGRINOVA_DISEASE_MODEL_PATH", default_model)
        self.mapping_path = mapping_path or os.getenv("AGRINOVA_CLASS_MAPPING_PATH", default_mapping)

        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
        self.preprocessor = ImagePreprocessor()
        self.metadata = EngineMetadata()
        self._load_mapping()
        self._load_model()

        self._initialized = True

    def _load_mapping(self):
        if not os.path.exists(self.mapping_path):
            raise ModelLoadError(f"Class mapping file not found at {self.mapping_path}")

        try:
            with open(self.mapping_path, 'r') as f:
                mapping_str = json.load(f)
            # Ensure it maps integer index -> string
            self.idx_to_class = {int(k): v for k, v in mapping_str.items()}
        except Exception as e:
            raise ModelLoadError(f"Failed to parse class mapping: {e}")

        if len(self.idx_to_class) != self.metadata.num_classes:
            raise ModelLoadError(f"Expected {self.metadata.num_classes} classes in mapping, found {len(self.idx_to_class)}.")

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise ModelLoadError(f"Model weights file not found at {self.model_path}")

        try:
            # ResNet-18 flat 12-class architecture matching Phase 6.0/6.6
            self.model = models.resnet18(weights=None)
            self.model.fc = nn.Linear(self.model.fc.in_features, len(self.idx_to_class))

            # Load state dict
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            raise ModelLoadError(f"Failed to load ResNet-18 model: {e}")

    def _parse_class_name(self, raw_class: str):
        # Safely split "{Crop} - {Disease}" without fragile indexing
        parts = raw_class.split(" - ", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        # Fallback if the mapping format changes unexpectedly
        return "Unknown", raw_class.strip()

    def predict(self, image_bytes: bytes) -> DiseaseDetectionResult:
        start_time = time.perf_counter()

        # 1. Preprocess
        tensor = self.preprocessor.process(image_bytes).to(self.device)

        # 2. Inference
        try:
            with torch.inference_mode():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        except Exception as e:
            raise EngineInferenceError(f"Model forward pass failed: {e}")

        # 3. Format results
        predictions = []
        for idx, prob in enumerate(probs):
            raw_class_name = self.idx_to_class[idx]
            crop, disease = self._parse_class_name(raw_class_name)

            predictions.append(DiseasePrediction(
                crop=crop,
                disease=disease,
                probability=float(prob),
                is_healthy="Healthy" in disease
            ))

        # Sort predictions by probability descending
        predictions.sort(key=lambda x: x.probability, reverse=True)

        inference_time_ms = (time.perf_counter() - start_time) * 1000.0

        return DiseaseDetectionResult(
            predictions=predictions,
            inference_time_ms=inference_time_ms,
            metadata=self.metadata
        )
