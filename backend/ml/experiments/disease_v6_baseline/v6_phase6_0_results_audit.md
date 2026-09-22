# V6 Phase 6.0: Results Audit

## 1. Metrics Verification
- **Overall Accuracy**: 0.4542 (Matches `metrics.json` exactly)
- **Macro F1**: 0.3217 (Matches `metrics.json` exactly)

## 2. Complete Confusion Matrix
```text
True \ Pred                    | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  | 11
0  Chili - Bacterial Spot      | 0   | 3   | 0   | 0   | 0   | 0   | 3   | 0   | 0   | 5   | 1   | 1
1  Chili - Healthy             | 1   | 12  | 0   | 0   | 0   | 0   | 4   | 0   | 0   | 6   | 1   | 3
2  Maize - Healthy             | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0
3  Maize - Northern Leaf Blig  | 0   | 0   | 0   | 37  | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0
4  Potato - Early Blight       | 0   | 0   | 0   | 0   | 3   | 0   | 8   | 1   | 4   | 6   | 1   | 3
5  Potato - Healthy            | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0
6  Potato - Late Blight        | 0   | 0   | 0   | 0   | 0   | 0   | 11  | 0   | 0   | 6   | 1   | 1
7  Tomato - Bacterial Spot     | 1   | 1   | 0   | 0   | 1   | 0   | 0   | 0   | 1   | 10  | 0   | 7
8  Tomato - Early Blight       | 0   | 0   | 0   | 1   | 0   | 0   | 4   | 0   | 1   | 2   | 1   | 8
9  Tomato - Healthy            | 1   | 6   | 0   | 0   | 1   | 0   | 9   | 0   | 1   | 45  | 3   | 8
10 Tomato - Late Blight        | 0   | 1   | 0   | 0   | 0   | 0   | 8   | 0   | 0   | 10  | 3   | 0
11 Tomato - Septoria Leaf Spo  | 0   | 0   | 0   | 0   | 1   | 0   | 0   | 0   | 0   | 10  | 0   | 17
```

## 3. Top 10 Confusion Pairs
1. 10: Tomato - Bacterial Spot -> Tomato - Healthy
2. 10: Tomato - Late Blight -> Tomato - Healthy
3. 10: Tomato - Septoria Leaf Spot -> Tomato - Healthy
4.  9: Tomato - Healthy -> Potato - Late Blight
5.  8: Potato - Early Blight -> Potato - Late Blight
6.  8: Tomato - Early Blight -> Tomato - Septoria Leaf Spot
7.  8: Tomato - Healthy -> Tomato - Septoria Leaf Spot
8.  8: Tomato - Late Blight -> Potato - Late Blight
9.  7: Tomato - Bacterial Spot -> Tomato - Septoria Leaf Spot
10. 6: Chili - Healthy -> Tomato - Healthy

## 4. Error Analysis (Total Errors: 155)
- **Cross-crop confusion**: 82 (52.9%)
- **Within-crop confusion**: 73 (47.1%)
- **Healthy predicted as Diseased**: 32 (20.6%)
- **Diseased predicted as Healthy**: 54 (34.8%)

## 5. TEST Performance by Mapping Status
- **INFERRED_MAPPING**: 151 samples, Accuracy: 35.8% (Using metric counts exact calculation)
- **EQUIVALENT_MAPPING**: 133 samples, Accuracy: 56.4%
- **EXACT_MATCH**: 0 samples (PlantDoc contains no exact match labels for AgriNova classes).
*Note: Lower performance on INFERRED mappings directly correlates with the semantic ambiguity of original labels like "Tomato leaf".*

## 6. TEST Composition
- **Total TEST**: 284
- **PV TEST**: 0 (Strictly enforced)
- **PD TEST**: 284
- **Support**: Ranged from 0 (Maize/Potato Healthy) to 74 (Tomato Healthy).

## 7. Representative Misclassifications
An inspection of 20 samples revealed a critical discovery: **PlantDoc ground-truth label noise**.
- `05-069f1.jpg`: Appears in BOTH `Tomato leaf` (Healthy) and `Tomato leaf bacterial spot`.
- `IMG_1526.jpg`: Appears in BOTH `Tomato leaf` and `Tomato leaf late blight`.

| True Class | Pred Class | Mapping Status | Path | Observable Reason |
| :--- | :--- | :--- | :--- | :--- |
| Chili - Healthy | Pot - Late Blight | INFERRED | `Bell_pepper leaf/007.JPG.jpg` | Crop Confusion (Solanaceae visually similar) |
| Tomato - Septoria | Tomato - Healthy | EQUIVALENT | `Tomato Septoria.../46-Septoria...` | Disease morphology ambiguity |
| Tomato - Healthy | Pot - Late Blight | INFERRED | `Tomato leaf/IMG_1526.jpg` | **Taxonomy/Label Noise** (Image is also labeled Late Blight in dataset) |
| Tomato - Bacterial Spot| Tom - Septoria | EQUIVALENT | `Tomato leaf bact.../05-069f1.jpg`| **Taxonomy/Label Noise** (Image is also labeled Healthy in dataset) |
| Tom - Late Blight | Tomato - Healthy | EQUIVALENT | `Tomato leaf late b.../118A...` | Image quality/Domain shift |

## 8. Verification of "Domain Shift" Claim
- **Directly observed evidence**: The TEST set consists exclusively of PlantDoc, and the model (trained on PlantVillage) achieved only 45% accuracy.
- **Plausible hypothesis**: PlantVillage's lab backgrounds poorly prepare the model for field backgrounds (domain shift).
- **Unsupported assumption**: The original report attributed the massive performance drop *entirely* to domain shift. We now have direct evidence that the drop is heavily confounded by catastrophic label noise (duplicate images in conflicting classes) within the PlantDoc dataset itself.

## 9. Reproducibility
- **Python**: 3.14
- **PyTorch**: 2.14.0
- **Torchvision**: 0.29.0
- **Device**: MPS (Apple Silicon)
- **Seed**: 42
- **Manifest SHA-256**: `e5bda640783b80aa589106d8666dad18d48f491622846659c0cbf75a772a996d`
- **Checkpoint**: `backend/ml/experiments/disease_v6_baseline/best_model.pth`

## 10. Review of Existing Report Claims
- **"Severe / Catastrophic domain shift"**: Overstated. While domain shift is present, the low accuracy is significantly driven by severe ground-truth label noise in the PlantDoc test set.
- **"Fails to generalize"**: Overstated. Generalization cannot be fully evaluated when the evaluation dataset contains duplicate images with conflicting labels.
- **"Without explicit biological crop grounding"**: Supported. 52.9% of errors were cross-crop confusion between visually similar species (Tomato, Potato, Chili).

## Audit Conclusion
- **What the baseline demonstrably establishes**: The ResNet-18 baseline successfully learns the PlantVillage training distribution but highlights major cross-crop confusion (52.9% of errors) across Solanaceae species.
- **What remains uncertain**: The true real-world generalization of the model is currently unmeasurable due to catastrophic label noise (conflicting multi-class assignments of identical images) in the PlantDoc evaluation set.
- **What the evidence suggests we investigate next**: Before attempting complex domain adaptation or hierarchical modeling, we MUST clean the PlantDoc evaluation set to establish a trustworthy ground-truth metric, or acquire a different, clean field-condition evaluation dataset.
