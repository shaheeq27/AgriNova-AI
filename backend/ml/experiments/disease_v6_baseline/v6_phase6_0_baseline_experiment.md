# V6 Phase 6.0: Disease Image Classification Baseline Experiment

## A. Baseline Architecture
- **Model**: ResNet-18
- **Pretrained Weights**: `IMAGENET1K_V1`
- **Head**: Replaced final fully connected layer to output 12 logits.

## B. Training Configuration
- **Optimizer**: Adam (`lr=1e-4`)
- **Loss Function**: Weighted Cross Entropy (inverse class frequency) to handle the 14.65x imbalance.
- **Batch Size**: 32
- **Epochs**: 3 (Fast baseline evaluation on MPS)
- **Scheduler**: ReduceLROnPlateau (`factor=0.5, patience=2`)
- **Augmentation**: Random Resized Crop (0.8-1.0), Random Horizontal Flip, Random Rotation (15 deg), Color Jitter (Brightness/Contrast 0.1)
- **Input Resolution**: 224x224
- **Normalization**: ImageNet standard (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`)

## C. Dataset Used
- **Source**: `dataset_manifest.csv` (16,524 usable images)
- **Split Strategy**: 100% PlantVillage in TRAIN; PlantDoc divided into TRAIN/VAL/TEST deterministically at the perceptual group level.
- **Corruptions/Exclusions**: 0 (all images opened successfully).

## D. Class Distribution
The dataset features a **14.65×** class imbalance (Min: 152 images for Potato Healthy, Max: 2,227 images for Tomato Bacterial Spot).

## E. Training/Validation Behavior
- **Best Validation Macro F1**: 0.4417
- **Final Epoch Train Loss**: ~0.0949
- **Duration**: ~14.5 minutes

## F. Overall TEST Metrics
- **Accuracy**: 45.42%
- **Macro Precision**: 34.49%
- **Macro Recall**: 35.49%
- **Macro F1**: 32.17%
- **Weighted F1**: 41.16%

## G. PlantDoc TEST Metrics
Since PlantVillage is restricted exclusively to TRAIN, the TEST set is 100% PlantDoc imagery. Therefore, the Overall TEST Metrics (45.4% Accuracy) directly represent generalization to field-condition (PlantDoc) data. The steep drop from training loss indicates a domain shift and ground-truth label noise.

## H. Per-class Metrics (TEST)
| Class | Precision | Recall | F1 Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| Chili - Bacterial Spot | 0.00 | 0.00 | 0.00 | 13 |
| Chili - Healthy | 0.52 | 0.44 | 0.48 | 27 |
| Maize - Healthy | 0.00 | 0.00 | 0.00 | 0 (No Data) |
| Maize - Northern Leaf Blight | 0.97 | 1.00 | 0.99 | 37 |
| Potato - Early Blight | 0.50 | 0.12 | 0.19 | 26 |
| Potato - Healthy | 0.00 | 0.00 | 0.00 | 0 (No Data) |
| Potato - Late Blight | 0.23 | 0.58 | 0.33 | 19 |
| Tomato - Bacterial Spot | 0.00 | 0.00 | 0.00 | 21 |
| Tomato - Early Blight | 0.14 | 0.06 | 0.08 | 17 |
| Tomato - Healthy | 0.45 | 0.61 | 0.52 | 74 |
| Tomato - Late Blight | 0.27 | 0.14 | 0.18 | 22 |
| Tomato - Septoria Leaf Spot | 0.35 | 0.61 | 0.45 | 28 |

## I. Confusion Matrix
Stored in `backend/ml/experiments/disease_v6_baseline/confusion_matrix.npy`. Severe cross-crop confusion is observed between Solanaceae crops (Chili, Tomato, Potato).

## J. Mapping-Quality Breakdown
- **INFERRED_MAPPING Accuracy**: 62.25%
- **EQUIVALENT_MAPPING Accuracy**: 26.31%
*(Note: No PlantDoc labels are EXACT_MATCH to AgriNova classes, so all TEST samples fall into these two categories).*

## K. Failure Analysis
Reviewing `misclassified.json` reveals classic **domain shift failures**. The model, dominated by PlantVillage's lab-like single-leaf black-background images, fails to generalize to PlantDoc's messy field backgrounds.
- *Example*: Healthy chili leaves in field conditions (`Bell_pepper leaf`) are confidently misclassified as `Potato - Late Blight` or `Tomato - Septoria Leaf Spot`.
- *Cross-Crop Confusion*: While lacking explicit biological crop grounding, the model confuses visually similar leaves across the Solanaceae family.

## L. Reproducibility Information
- **Random Seed**: 42
- **Hardware/Device**: MPS / Apple Silicon
- **Manifest Hash**: (Implicit from Phase 5.1 deterministic generation)
- **Artifacts**: Checkpoint (`best_model.pth`), metrics JSON, numpy confusion matrix, and misclassification logs are saved to `backend/ml/experiments/disease_v6_baseline`.

## M. Limitations
- **Evaluation Blindspots**: Potato Healthy and Maize Healthy have no PlantDoc representation, meaning their TEST metrics are 0 and their true generalization is unknown.
- **Domain Shift**: The baseline proves that naively training on a heavily PV-dominated dataset achieves low test accuracy, heavily confounded by label noise in the evaluation set (45.4% accuracy).
- **Out of Distribution (OOD)**: The baseline model lacks confidence calibration or an OOD rejection pipeline. Unrelated images will be confidently misclassified into one of the 12 classes.
- **No Severity Prediction**: The model is purely a classifier. Severity prediction is fundamentally unsupported by the dataset and cannot be inferred.

## N. Recommended NEXT EXPERIMENT
To address the domain shift and label noise and cross-crop confusion, the next experiment should introduce a hierarchical or dual-input approach (e.g., providing the known crop ID as a separate input) and apply heavier background augmentation/domain adaptation to bridge the PlantVillage-to-PlantDoc gap.
