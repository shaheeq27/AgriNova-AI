# V6 Phase 6.4 — Multi-Task Learning Controlled Experiment

## 1. Mechanism
**Deterministic Final Prediction:** The 12-class prediction is produced solely by taking the `argmax` of the main 12-class linear head. The crop (4-class) and disease status (2-class) auxiliary heads influence the model strictly during training by backpropagating additional classification loss into the shared ResNet-18 backbone. This forces the feature extractor to explicitly encode host-plant morphology and general disease features.

## 2. Overall 11-Class External Benchmark (MTL Results)
- **Accuracy:** 0.2900
- **Macro Precision:** 0.3472
- **Macro Recall:** 0.4744
- **Macro F1:** 0.3189
- **Weighted F1:** 0.2743

## 3. Crop Recognition (Auxiliary Impact)
- **Crop Accuracy:** 0.4431
- **Crop Macro F1:** 0.4437

**Crop Confusion Matrix (Rows: True, Cols: Pred)**
['Chili', 'Maize', 'Potato', 'Tomato']
[[ 526    4   15   52]
 [   1  589    0    0]
 [ 772 1824 2726 6976]
 [ 157  146   19 4090]]

## 4. Disease-Status Recognition
- **Healthy/Diseased Accuracy:** 0.8113
- **Macro F1:** 0.7840

**Status Confusion Matrix (Rows: Healthy, Diseased | Cols: Pred)**
[[ 4080   733]
 [ 2645 10439]]

## 5. Failure Analysis
- **Potato → Tomato Errors:** 6976
- **Cross-Crop Errors:** 9966
- **Within-Crop Errors:** 2740
- **Healthy → Diseased:** 733
- **Diseased → Healthy:** 2645

**Top Confusion Pairs:**
- True: **Potato - Early Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (1578)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (1530)
- True: **Potato - Healthy** ➔ Pred: **Maize - Healthy** (947)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Late Blight** (812)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Early Blight** (675)

**Prediction Distribution:**
- Chili - Bacterial Spot: 230
- Chili - Healthy: 1226
- Maize - Healthy: 1711
- Maize - Northern Leaf Blight: 852
- Potato - Early Blight: 815
- Potato - Healthy: 883
- Potato - Late Blight: 1062
- Tomato - Bacterial Spot: 750
- Tomato - Early Blight: 1926
- Tomato - Healthy: 2905
- Tomato - Late Blight: 1953
- Tomato - Septoria Leaf Spot: 3584

## 6. Per-Crop Results (Datasets)
### chili_krishna_v3
- Accuracy: 0.8459
- Macro F1: 0.1918

### maize_enlin_li
- Accuracy: 0.6390
- Macro F1: 0.4094

### potato_pldd_up
- Accuracy: 0.1425
- Macro F1: 0.0625

### tomato_pakistan
- Accuracy: 0.5793
- Macro F1: 0.2235

## 7. Baseline Comparison (MTL vs Flat ResNet-18)
| Metric | Flat Baseline (Phase 6.2) | MTL Model (Phase 6.4) | Difference |
| :--- | :--- | :--- | :--- |
| **External Accuracy** | 27.20% | 29.00% | +1.80% |
| **Macro F1** | 0.2814 | 0.3189 | +0.0375 |
| **Crop Accuracy** | 45.67% | 44.31% | -1.36% |
| **Potato → Tomato** | 8,212 | 6976 | -1236 |

## 8. Success Criteria Check
1. **Crop accuracy > 70%**: Failed
2. **Potato → Tomato reduced by ≥50%**: Failed
3. **Overall external accuracy > 27.20%**: Passed
