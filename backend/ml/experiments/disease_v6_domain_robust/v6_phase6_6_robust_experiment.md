# V6 Phase 6.6 — Domain-Robust Augmentation Controlled Experiment Results

## 1. Overall 11-Class External Benchmark
- **Accuracy:** 0.3692
- **Macro Precision:** 0.3794
- **Macro Recall:** 0.4118
- **Macro F1:** 0.3280
- **Weighted F1:** 0.3701

## 2. Crop Recognition
- **Crop Accuracy:** 0.6502
- **Crop Macro F1:** 0.6245

**Crop Confusion Matrix (Rows: True, Cols: Pred)**
['Chili', 'Maize', 'Potato', 'Tomato']
[[ 463    3   66   65]
 [  19  569    0    2]
 [1376  108 7332 3482]
 [ 165   69  905 3273]]

## 3. Disease-Status Recognition
- **Healthy/Diseased Accuracy:** 0.8418
- **Macro F1:** 0.7972

**Status Confusion Matrix (Rows: Healthy, Diseased | Cols: Pred)**
[[ 3337  1476]
 [ 1356 11728]]

## 4. Failure Analysis
- **Potato → Tomato Errors:** 3482
- **Cross-Crop Errors:** 6260
- **Within-Crop Errors:** 5029
- **Healthy → Diseased:** 1476
- **Diseased → Healthy:** 1356

**Top Confusion Pairs:**
- True: **Potato - Late Blight** ➔ Pred: **Potato - Early Blight** (1453)
- True: **Potato - Early Blight** ➔ Pred: **Potato - Late Blight** (1160)
- True: **Potato - Early Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (1144)
- True: **Potato - Healthy** ➔ Pred: **Chili - Healthy** (1039)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (844)

**Prediction Distribution:**
- Chili - Bacterial Spot: 183
- Chili - Healthy: 1840
- Maize - Healthy: 81
- Maize - Northern Leaf Blight: 668
- Potato - Early Blight: 3411
- Potato - Healthy: 678
- Potato - Late Blight: 4214
- Tomato - Bacterial Spot: 479
- Tomato - Early Blight: 403
- Tomato - Healthy: 2094
- Tomato - Late Blight: 1311
- Tomato - Septoria Leaf Spot: 2535

## 5. Per-Dataset Results
### chili_krishna_v3
- Accuracy: 0.7085
- Macro F1: 0.1743

### maize_enlin_li
- Accuracy: 0.5373
- Macro F1: 0.1828

### potato_pldd_up
- Accuracy: 0.3056
- Macro F1: 0.0911

### tomato_pakistan
- Accuracy: 0.4782
- Macro F1: 0.1777


## 6. Per-Class F1 Scores
- Chili - Bacterial Spot: 0.1752
- Chili - Healthy: 0.3443
- Maize - Healthy: 0.2036
- Maize - Northern Leaf Blight: 0.5856
- Potato - Early Blight: 0.2806
- Potato - Healthy: 0.3247
- Potato - Late Blight: 0.4447
- Tomato - Bacterial Spot: 0.0000
- Tomato - Early Blight: 0.3080
- Tomato - Healthy: 0.5350
- Tomato - Late Blight: 0.5203
- Tomato - Septoria Leaf Spot: 0.2135

## 7. Baseline Comparison (Phase 6.2 vs Phase 6.6)
| Metric | Flat Baseline (Phase 6.2) | Robust Augmentation (Phase 6.6) | Difference |
| :--- | :--- | :--- | :--- |
| **External Accuracy** | 27.20% | 36.92% | +9.72% |
| **Macro F1** | 0.2814 | 0.3280 | +0.0466 |
| **Crop Accuracy** | 45.67% | 65.02% | +19.35% |
| **Potato → Tomato** | 8,212 | 3482 | -4730 |
| **Healthy/Diseased Acc** | 73.18% | 84.18% | +11.00% |

## 8. Success Criteria Check
1. **Overall External Accuracy > 29.20%**: Passed
2. **Crop Accuracy > 60%**: Passed
3. **Potato → Tomato ≤ 5,748 errors**: Passed
