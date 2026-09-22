# Phase 7.0 — Crop Disease Detection Engine Architecture

## Overview
This document defines the architecture for the standalone Crop Disease Detection Engine and its integration into the AgriNova backend. The design strictly preserves the findings, limitations, and boundaries established in the locked V6.7 research conclusion.

The engine acts as a pure inference boundary: it takes an image, runs it through the locked Phase 6.6 robust model, and returns raw probabilities. It does not fabricate confidence, make Out-Of-Distribution (OOD) claims, or query the database itself.

---

## 1. Engine Responsibilities
- **Ingestion:** Accept raw image bytes (or PIL Images) from the upstream service.
- **Preprocessing:** Apply the exact deterministic evaluation transforms used in Phase 6.6.
- **Inference:** Execute a forward pass on the frozen V6 ResNet-18 checkpoint (`robust_best_model.pth`).
- **Post-processing:** Apply softmax to raw logits to produce model probabilities.
- **Mapping:** Translate output indices to human-readable Crop and Disease labels using `class_mapping.json`.

## 2. Input/Output Contract
The engine operates strictly on Pydantic schemas to ensure type safety.

**Input:** `PIL.Image.Image` or raw bytes.
**Output (`DiseaseDetectionResult`):**
```python
class DiseasePrediction(BaseModel):
    crop: str
    disease: str
    probability: float  # Raw softmax model probability [0.0, 1.0] - NOT confidence
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
```

## 3. Preprocessing Pipeline
To guarantee reproducibility against Phase 6.6, the preprocessing pipeline must exactly match the evaluation script.
- `transforms.Resize(256)`
- `transforms.CenterCrop(224)`
- `transforms.ToTensor()`
- `transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
- *No data augmentation is applied during inference.*

## 4. Model Loading Architecture
The PyTorch model (approx. 45MB) must not be loaded per request.
- **Singleton Loader:** The engine will utilize a Singleton pattern to load the model into memory exactly once at application startup.
- **Device Management:** Auto-detects device fallback: `MPS` (Apple Silicon) -> `CUDA` -> `CPU`.
- **State Dictionary:** Instantiates `models.resnet18(weights=None)` with a modified 12-class fully connected layer, then loads the locked `.pth` state dict via `torch.no_grad()`.

## 5. Class Mapping
The engine maps the output tensor index (0-11) to string identifiers using the locked `class_mapping.json`.
String formatting follows the established convention: `"{Crop} - {Disease}"`. The engine safely parses this string into separate `crop` and `disease` fields for the API consumer.

## 6. Error Handling
- **ImageProcessingError:** Raised if the uploaded file is corrupt, unreadable, or not a valid image format.
- **ModelLoadError:** Raised at startup if the checkpoint or mapping file is missing or corrupted.
- **EngineInferenceError:** Raised if the tensor forward pass fails (e.g., OOM).

## 7. Supported/Unsupported Crop Semantics & OOD
- **Supported Crops:** The model is strictly trained on 12 classes across 4 crops (Chili, Maize, Potato, Tomato).
- **No OOD / Abstention:** The engine *does not* include an out-of-distribution detector. The engine *will* output probabilities for one of the 12 supported classes regardless of input.

## 8. Integration Boundary with the Existing Backend
The Engine is mathematically decoupled from the backend's business logic.
- **`app/services/disease_detection/engine.py`:** Holds the pure PyTorch inference code.
- **`app/services/disease_service.py`:** Handles the API request, parses the file, calls the Engine, and then takes the top prediction string to query the database.

## 9. Disease Knowledge-Base Integration
The model prediction is clearly separated from disease evidence.

## 10. Testing Strategy
- Verify that the production inference implementation uses the same model weights, class mapping, preprocessing, and output ordering as the locked Phase 6.6 experiment.

## 11. Proposed Directory Structure
The standalone engine will be placed in the backend services directory, while model artifacts will be stored in a dedicated `ml_assets` folder.

```text
backend/
├── app/
│   ├── services/
│   │   ├── disease_detection/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── preprocessor.py
│   │   │   ├── schemas.py
│   │   │   └── exceptions.py
├── ml_assets/
│   ├── models/
│   │   └── robust_best_model.pth
│   └── class_mapping.json
```

## 12. Reused vs. Newly Created Files
- **Reused (Copied from ML Experiments):**
  - `backend/ml/experiments/disease_v6_domain_robust/robust_best_model.pth` ➔ `ml_assets/models/`
  - `backend/ml/experiments/disease_v6_domain_robust/class_mapping.json` ➔ `ml_assets/`
- **Newly Created:**
  - The entire `app/services/disease_detection/` module.
