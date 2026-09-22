# V6 Phase 6.0: Disease Image Classification Baseline Experiment

## A. Baseline Architecture
- **Model**: ResNet-18
- **Pretrained Weights**: `IMAGENET1K_V1`
- **Head**: Replaced final fully connected layer to output 12 logits.

## B. Training Configuration
- **Optimizer**: Adam (`lr=1e-4`)
- **Loss Function**: Weighted Cross Entropy (inverse class frequency)
- **Batch Size**: 32
- **Epochs**: 3 (Early stopping / model selection on Validation Macro F1)
- **Scheduler**: ReduceLROnPlateau (`factor=0.5, patience=2`)
- **Augmentation**: Random Resized Crop (0.8-1.0), Random Horizontal Flip, Random Rotation (15 deg), Color Jitter (Brightness/Contrast 0.1)
- **Input Resolution**: 224x224
- **Normalization**: ImageNet standard (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`)

## C. Dataset Used
- **Source**: `dataset_manifest.csv` (16,524 usable images)
- **Split Strategy**: 100% PlantVillage in TRAIN; PlantDoc divided into TRAIN/VAL/TEST deterministically.
- **Corruptions/Exclusions**: 0 (all images opened successfully).

## D. Class Distribution
The dataset features a **14.65×** class imbalance (Min: 152 images for Potato Healthy, Max: 2,227 images for Tomato Bacterial Spot). This imbalance is mitigated using Weighted Cross Entropy.

## E. Training/Validation Behavior
*(Will be filled with final epoch loss and Val Macro F1)*

## F. Overall TEST Metrics
*(Will be filled with Accuracy, Macro Precision, Recall, F1, Weighted F1)*

## G. PlantDoc TEST Metrics
Since PlantVillage is restricted exclusively to TRAIN, the TEST set is 100% PlantDoc imagery. Therefore, the Overall TEST Metrics directly represent generalization to field-condition (PlantDoc) data.

## H. Per-class Metrics
*(Will be filled from `metrics.json`)*

## I. Confusion Matrix
*(Will be summarized/provided from `confusion_matrix.npy`)*

## J. Mapping-Quality Breakdown
*(Will report accuracy across EXACT_MATCH, EQUIVALENT_MAPPING, and INFERRED_MAPPING classes)*

## K. Failure Analysis
*(Will list representative misclassifications from `misclassified.json`)*

## L. Reproducibility Information
- **Random Seed**: 42
- **PyTorch / Torchvision**: (Will specify)
- **Hardware/Device**: MPS / Apple Silicon
- **Manifest Hash**: (Implicit from Phase 5.1 generation)
- **Artifacts**: Checkpoint, metrics, and logs saved to `backend/ml/experiments/disease_v6_baseline`.

## M. Limitations
- **Evaluation Blindspots**: Potato Healthy and Maize Healthy have no PlantDoc representation, meaning their TEST metrics are 0 and their true generalization is unknown.
- **Out of Distribution (OOD)**: The baseline model lacks confidence calibration or an OOD rejection pipeline. Unrelated images will be confidently misclassified into one of the 12 classes.
- **No Severity Prediction**: The model is purely a classifier. Severity prediction is fundamentally unsupported by the dataset and cannot be inferred.

## N. Recommended NEXT EXPERIMENT
Establish Out-of-Distribution (OOD) rejection, implement confidence thresholding, and address class imbalance beyond simple weighting if minority classes underperform.
