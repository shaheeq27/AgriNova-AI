# Phase 7.6 — Production Model Promotion & Integration Lock

## Final Production Artifacts
Following the read-only audits in Phase 7.5, the AgriNova Disease Detection Engine has been locked to the robust baseline checkpoint from Phase 6.6.

- **Production Model Weights:** `backend/ml_assets/models/robust_best_model.pth`
- **SHA-256 Hash:** `188a11f301797ebaa7353b70a446a37507f6a2ce029049fe57bfd37356799b49`
- **Class Mapping:** `backend/ml_assets/class_mapping.json` (12-class standard taxonomy)

*Note: The candidate `final_disease_model_v1.pth` (Epoch 12) from Phase 7.5 was intentionally rejected and omitted from production because its external validation scores did not surpass the rigorous Phase 6.6 checkpoint reference.*

## Architectural Integrity
The backend `DiseaseDetectionEngine` class explicitly references the exact approved production artifacts without hardcoded local developer paths:
```python
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
default_model = str(backend_dir / "ml_assets" / "models" / "robust_best_model.pth")
```
### Preprocessing
The exact Phase 6.6 unaugmented evaluation preprocessing pipeline has been structurally codified and verified in `preprocessor.py`:
- `Resize(256)`
- `CenterCrop(224)`
- `ToTensor()`
- `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`

### API & Semantic Contracts
The backend strictly enforces the semantic distinction between probabilistic inference and deterministically applied knowledge:
- **Raw Probability:** The PyTorch softmax output is strictly returned in the API schema as `model_probability: float`. The system does **not** map this to pseudo-calibrated "confidence".
- **Deterministic Knowledge:** Features like "Severity", "Symptoms", and "Treatments" are solely sourced from the deterministic `kb_disease_library` join. The model is explicitly not tasked with predicting qualitative severities.

## Test Suite Sign-off
No architecture, code, schemas, or tests were altered during Phase 7.6. All tests successfully passed under the locked production footprint:
- **Engine Unit Tests:** Passed (4/4)
- **Service Integration Tests:** Passed (7/7)
- **API Tests:** Passed (7/7)
- **End-to-End Tests:** Passed (2/2)
- **Real Image E2E Audit:** A real Maize Northern Leaf Blight image successfully resolved through the ResNet-18 model pipeline and seamlessly enriched with KB symptoms, treatment, and severity directly from the database connection.

## Status
**Phase 7.6 Complete.** The ML disease detection backend is functionally locked, tested, and structurally sound for production consumption by the frontend client.
