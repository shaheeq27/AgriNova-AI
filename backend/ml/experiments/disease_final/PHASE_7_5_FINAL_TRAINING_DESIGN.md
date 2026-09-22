# Phase 7.5 — Final Disease Detection Model Training Design

## Objective
Design a reproducible, rigorous final training protocol for the AgriNova Disease Detection Engine. This transitions the validated V6.6 domain-robust research pipeline into a production-ready artifact without introducing unverified variables or data leakage.

## 1. Dataset and Split
- **Canonical Training Manifest:** `dataset_manifest.csv`
  - Required SHA-256: `e5bda640783b80aa589106d8666dad18d48f491622846659c0cbf75a772a996d`
- **Splits:** Strictly preserve the existing `TRAIN` and `VALIDATION` splits.
- **Class Distribution:** 12 classes spanning Chili, Maize, Potato, and Tomato.
- **External Benchmark Immunity:** The `external_evaluation_manifest.csv` (17,897 images, 11 classes, SHA-256: `bd74ba031526c09d206c0887d2f0b78ad20423ba98f6468ed8eae4561a4b9edf`) remains a strict holdout. It will **not** be used for training, validation, early stopping, checkpoint selection, or hyperparameter tuning.

## 2. Model
- **Architecture:** ResNet-18
- **Initialization:** ImageNet-1K (`models.ResNet18_Weights.IMAGENET1K_V1`)
- **Output Head:** Flat 12-class linear layer.
- **Class Mapping:** Retain the exact JSON ordering from the current `class_mapping.json`.

## 3. Augmentation
Utilize the validated Phase 6.6 domain-robust augmentation pipeline identically:
- `RandomResizedCrop(224, scale=(0.5, 1.0), ratio=(0.75, 1.33))`
- `RandomHorizontalFlip(p=0.5)`
- `RandomVerticalFlip(p=0.2)`
- `RandomRotation(30)`
- `RandomPerspective(distortion_scale=0.15, p=0.25)`
- `ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1)`
- `RandomApply([GaussianBlur(kernel_size=5, sigma=(0.1, 2.0))], p=0.3)`
- `ToTensor()`
- `RandomErasing(p=0.1, scale=(0.02, 0.05), ratio=(0.5, 2.0), value=0, inplace=False)`
- `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])`
*No new augmentation strategies or experiments will be introduced.*

## 4. Optimization
- **Optimizer:** Adam
- **Initial Learning Rate:** `1e-4`
- **Scheduler:** `ReduceLROnPlateau(mode='max', patience=3, factor=0.5)` (monitoring validation Macro F1).
- **Weight Decay:** `1e-5` (Added minimally over the baseline to gently penalize large weights and prevent overfitting during the extended epoch window).
- **Batch Size:** 32
- **Maximum Epochs:** 30 (Increased from the 3-epoch fast iteration baseline to allow full convergence).
- **Early Stopping & Checkpoint Selection:** The training script must explicitly assert and guarantee that the saved checkpoint corresponds to the epoch with the **highest Validation Macro F1**, not simply the final epoch. Stop early if no improvement is observed for 7 consecutive epochs.

## 5. Class Imbalance
- **Weighting Strategy:** Weighted Cross-Entropy Loss.
- **Verification:** Verification logic will explicitly assert that loss weights are calculated *exclusively* using the `TRAIN` split statistics to prevent validation distribution leakage into the gradients.

## 6. Validation
- **Primary Checkpoint Metric:** Validation Macro F1.
- **Secondary Logged Metrics:** Accuracy, Macro Precision, Macro Recall, Weighted F1, Per-class metrics, and Confusion Matrix.

## 7. Final Evaluation
Upon freezing the final training checkpoint, a rigorous zero-shot evaluation will be conducted on:
1. Canonical Validation Set
2. Frozen External Benchmark

The following metrics will be reported:
- Overall Accuracy
- Macro F1
- Crop-level Accuracy
- Potato→Tomato confusion errors
- Healthy/Diseased Accuracy
- Detailed per-class precision/recall/F1

## 8. Reproducibility
The following parameters will be logged and enforced:
- **Seed:** `42` (Propagated to Python, PyTorch, NumPy, and DataLoader workers).
- **Environment Details:** Python/PyTorch versions, OS, Hardware device.
- **Data Integrities:** SHA-256 hashes of dataset and external manifests.
- **Output Integrities:** SHA-256 hash of the final `.pth` checkpoint and `class_mapping.json`.

## 9. Production Artifact
The final model will be packaged for production in `backend/ml_assets/`:
- `models/final_disease_model_v1.pth`
- `class_mapping.json`
- `metadata.json` (Includes all training configurations, hashes, timestamps, and evaluation metrics to ensure lifecycle traceability).

## 10. Inference Parity
The final script will conclude with an explicit inference parity audit. It will pass a test image through the production `DiseaseDetectionEngine` transform pipeline:
`Resize(256) → CenterCrop(224) → ToTensor → ImageNet normalization`
This guarantees preprocessing transform parity is verified between the external benchmark evaluation and the backend API service layer.

## 11. Leakage Audit
Prior to `model.train()`, the training pipeline will programmatically verify:
- Intersection of `train_df['image_path']` and `external_df['image_path']` == 0.
- Intersection of `val_df['image_path']` and `external_df['image_path']` == 0.
- Target `dataset_manifest.csv` SHA-256 perfectly matches the historical canonical hash.

## 12. Success Criteria
The final production model will be accepted if:
1. Training completes with zero data leakage or contamination alerts.
2. The model uses Phase 6.6 as a reference baseline. The final model is accepted only after examining validation + external metrics and confirming no leakage or regression makes the model unsuitable. (A rigid numerical threshold is avoided to allow for natural variations from longer convergence/regularization).
3. Potato→Tomato cross-crop confusion remains significantly suppressed compared to Phase 6.0.
4. Preprocessing transform parity is verified when loaded via the backend singleton engine.
