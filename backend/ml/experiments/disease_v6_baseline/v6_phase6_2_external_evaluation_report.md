# V6 Phase 6.2 — External Field Benchmark Evaluation Report

## 1. Global Performance Metrics
The ResNet-18 baseline model (trained on PlantVillage) was evaluated completely zero-shot against the 11-class external field benchmark (17897 images). Tomato Bacterial Spot was excluded from this evaluation as it lacked a verified external dataset.

* **Overall Accuracy**: 0.2720
* **Macro Precision**: 0.3421
* **Macro Recall**: 0.3972
* **Macro F1**: 0.2814
* **Weighted F1**: 0.2522

## 2. Comparison with Phase 6.0 PlantDoc Baseline
| Metric | Original PlantDoc (Clean TEST, Phase 6.0) | New External Field Benchmark (Phase 6.2) |
| :--- | :--- | :--- |
| **Clean Support** | 166 images | 17897 images |
| **Target Classes** | 12 | 11 |
| **Accuracy** | 62.05% | 27.20% |

*Note: These external results exclusively represent the 11 acquired field classes. They should not be generalized as representative of all 12 classes without Tomato Bacterial Spot.*

## 3. Performance by Source Dataset
### chili_krishna_v3
- **Support**: 597
- **Accuracy**: 0.6466
- **Macro F1**: 0.1701

### maize_enlin_li
- **Support**: 590
- **Accuracy**: 0.5712
- **Macro F1**: 0.2601

### potato_pldd_up
- **Support**: 12298
- **Accuracy**: 0.1315
- **Macro F1**: 0.0513

### tomato_pakistan
- **Support**: 4412
- **Accuracy**: 0.5730
- **Macro F1**: 0.2125

## 4. Per-Class Metrics
| Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| Chili - Bacterial Spot | 0.3429 | 0.0811 | 0.1311 | 148.0 |
| Chili - Healthy | 0.3221 | 0.8330 | 0.4646 | 449.0 |
| Maize - Healthy | 0.1921 | 0.2179 | 0.2042 | 312.0 |
| Maize - Northern Leaf Blight | 0.4223 | 0.9676 | 0.5880 | 278.0 |
| Potato - Early Blight | 0.4623 | 0.1633 | 0.2414 | 3974.0 |
| Potato - Healthy | 0.7388 | 0.0897 | 0.1600 | 2931.0 |
| Potato - Late Blight | 0.4993 | 0.1307 | 0.2072 | 5393.0 |
| Tomato - Bacterial Spot | 0.0000 | 0.0000 | 0.0000 | 0.0 |
| Tomato - Early Blight | 0.4717 | 0.4740 | 0.4728 | 1019.0 |
| Tomato - Healthy | 0.1651 | 0.8930 | 0.2787 | 1121.0 |
| Tomato - Late Blight | 0.3476 | 0.5438 | 0.4241 | 1153.0 |
| Tomato - Septoria Leaf Spot | 0.1408 | 0.3727 | 0.2044 | 1119.0 |

## 5. Analysis
### Strongest Classes (F1)
- **Maize - Northern Leaf Blight**: 0.5880
- **Tomato - Early Blight**: 0.4728
- **Chili - Healthy**: 0.4646
### Weakest Classes (F1)
- **Chili - Bacterial Spot**: 0.1311
- **Potato - Healthy**: 0.1600
- **Maize - Healthy**: 0.2042

### Error Taxonomy
- **Healthy → Disease Errors**: 840
- **Disease → Healthy Errors**: 3960
- **Cross-Crop Errors**: 9724
- **Within-Crop Errors**: 3305

### Top 10 Confusion Pairs
- True: **Potato - Healthy** ➔ Pred: **Tomato - Healthy** (1488 errors)
- True: **Potato - Early Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (1338 errors)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Healthy** (1333 errors)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Septoria Leaf Spot** (1140 errors)
- True: **Potato - Early Blight** ➔ Pred: **Tomato - Healthy** (955 errors)
- True: **Potato - Late Blight** ➔ Pred: **Tomato - Late Blight** (750 errors)
- True: **Potato - Late Blight** ➔ Pred: **Potato - Early Blight** (555 errors)
- True: **Potato - Healthy** ➔ Pred: **Chili - Healthy** (492 errors)
- True: **Tomato - Septoria Leaf Spot** ➔ Pred: **Tomato - Healthy** (445 errors)
- True: **Potato - Early Blight** ➔ Pred: **Potato - Late Blight** (417 errors)
