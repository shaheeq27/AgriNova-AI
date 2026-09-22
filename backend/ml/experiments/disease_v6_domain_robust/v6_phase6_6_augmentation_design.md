# V6 Phase 6.6 — Domain-Robust Augmentation Controlled Experiment

## 1. Experimental Overview
This experiment tests the hypothesis that the dominant failure mode on the external benchmark (catastrophic cross-crop confusion, e.g., Potato ➔ Tomato) is caused by the model overfitting to artificial laboratory conditions (static lighting, flat perspectives, solid backgrounds) present in the PlantVillage dataset.

By applying aggressive, domain-targeted spatial and color augmentations to the lab data, we aim to force the ResNet-18 backbone to learn intrinsic plant morphology and pathology, rather than relying on brittle environmental artifacts.

## 2. Hypothesis & Controls
**Hypothesis:**
Replacing the mild baseline augmentations with domain-robust spatial and photometric transformations (simulating field illumination, varied camera distances, depth-of-field blur, and leaf occlusions) **may improve** field-domain generalization and crop-level accuracy on zero-shot external data without requiring any external field images in the training set.

**Control (Phase 6.0 Baseline):**
- Architecture: ResNet-18 (12 classes)
- Training Data: PV/PD manifest (`dataset_manifest.csv`)
- Baseline Transforms:
  - `RandomResizedCrop(224, scale=(0.8, 1.0))`
  - `RandomHorizontalFlip(p=0.5)`
  - `RandomRotation(15 degrees)`
  - `ColorJitter(brightness=0.1, contrast=0.1)`

**Experimental Condition (Phase 6.6):**
- Exactly the same architecture, optimizer, learning rate, epochs (3), batch size (32), and training split.
- **Change:** Replacement of the augmentation pipeline.

## 3. Proposed Domain-Robust Augmentation Pipeline
The new transformations are designed to mimic real-world field conditions without destroying critical disease morphology (such as lesion shape or leaf yellowing).

```python
train_transform_robust = transforms.Compose([
    # Scale & Viewpoint Variation
    transforms.RandomResizedCrop(224, scale=(0.5, 1.0), ratio=(0.75, 1.33)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.RandomRotation(30),
    transforms.RandomPerspective(distortion_scale=0.15, p=0.25),

    # Illumination & Sensor Variation
    transforms.ColorJitter(
        brightness=0.4,
        contrast=0.4,
        saturation=0.4,
        hue=0.1
    ),

    # Mild Context Variation
    transforms.RandomApply([transforms.GaussianBlur(kernel_size=5, sigma=(0.1, 2.0))], p=0.3),

    transforms.ToTensor(),

    # Occlusion (Simulating overlapping leaves, shadows, or debris)
    transforms.RandomErasing(p=0.1, scale=(0.02, 0.05), ratio=(0.5, 2.0), value=0, inplace=False),

    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

## 4. Reproducibility Safeguards
- **Random Seed:** 42 (Enforced for PyTorch, CUDA, and NumPy).
- **Training Manifest:** `dataset_manifest.csv` (No modifications).
- **Evaluation Manifest:** `external_evaluation_manifest.csv` (Strictly quarantined).
- **No Test Images Used:** The external benchmark will NOT be used for early stopping or checkpoint selection. Checkpoint selection relies solely on the internal validation split defined in `dataset_manifest.csv`.

## 5. Evaluation Protocol
Following training, the model will be evaluated zero-shot against the untouched `external_evaluation_manifest.csv` (17,897 images).

**Metrics to Report:**
- Overall Accuracy
- Macro F1
- Crop Accuracy
- Potato ➔ Tomato Error Count
- Cross-Crop Errors
- Healthy / Diseased Binary Accuracy
- Per-Dataset Results (Accuracy/Macro F1 for PLDD-UP, Tomato Pakistan, Krishna V3, Enlin Li)
- Per-Class F1 Scores

## 6. Success Criteria
To deem domain-robust augmentation a success over the Phase 6.2 baseline:
1. **Overall External Accuracy:** External accuracy must exceed 27.20% by at least 2 percentage points (i.e. > 29.20%).
2. **Crop Accuracy:** Must increase from the 45.67% baseline to > 60%.
3. **Potato ➔ Tomato Confusion:** Must be reduced by at least 30% from the baseline (8,212 instances). This means ≤ 5,748 errors.
