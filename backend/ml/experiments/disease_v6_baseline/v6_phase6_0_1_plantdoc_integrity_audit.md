# V6 Phase 6.0.1: PlantDoc Evaluation Integrity Audit

## 1. Executive Summary
A comprehensive integrity scan of the complete PlantDoc dataset was performed using exact file hashing (MD5) and perceptual hashing (dHash). The scan identified catastrophic ground-truth label noise—specifically, identical images assigned to multiple conflicting disease classes. By quarantining these conflicting duplicate groups, the TEST set was reduced by 41.5%, but the baseline model's accuracy on the remaining CLEAN TEST set jumped from 45.4% to 62.05%.

## 2. Integrity Scan Results (Complete PlantDoc)
- **Total PlantDoc Images**: 1,353
- **Exact Duplicate Groups (MD5) with Conflicting Labels**: 265
- **Perceptual Groups (dHash) with Conflicting Labels**: 7 (above exact matches)
- **Conflicting Groups Crossing Splits**: 0 *(Phase 5 grouped all hashes deterministically into the same splits, meaning conflicts were safely contained within their respective splits rather than leaking across them).*
- **Duplicate Groups in TEST**: 56
- **Conflicting Duplicate Groups in TEST**: 56 (100% of duplicates in TEST were conflicting labels).

## 3. Quarantine Statistics
Every image belonging to a conflicting group was quarantined to prevent evaluating the model against contradictory ground-truth labels.
- **Original TEST Count**: 284
- **TEST Samples Quarantined**: 118 (41.5%)
- **Proposed CLEAN TEST Count**: 166

### Affected Class Support in CLEAN TEST:
Quarantining exposed severe deficits in PlantDoc's reliability for several classes:
- **Chili - Bacterial Spot**: 0 (All 13 original samples were quarantined)
- **Chili - Healthy**: 14 (Fewer than 20)
- **Maize - Healthy**: 0 (Never existed)
- **Maize - Northern Leaf Blight**: 37
- **Potato - Early Blight**: 23
- **Potato - Healthy**: 0 (Never existed)
- **Potato - Late Blight**: 19 (Fewer than 20)
- **Tomato - Bacterial Spot**: 0 (All 21 original samples were quarantined)
- **Tomato - Early Blight**: 16 (Fewer than 20)
- **Tomato - Healthy**: 31
- **Tomato - Late Blight**: 0 (All 22 original samples were quarantined)
- **Tomato - Septoria Leaf Spot**: 26

*Note: For Chili Bacterial Spot, Tomato Bacterial Spot, and Tomato Late Blight, literally 100% of the TEST images were found to be exact copies of images that also existed in conflicting classes.*

## 4. Model Re-Evaluation (CLEAN TEST)
The existing ResNet-18 checkpoint from Phase 6.0 was re-evaluated on the 166 CLEAN TEST images. **No retraining occurred.**
- **Accuracy**: 62.05%
- **Macro Precision**: 41.73%
- **Macro Recall**: 38.75%
- **Macro F1**: 37.31%
- **Weighted F1**: 58.95%

### Per-Class Metrics (CLEAN TEST)
| Class | Precision | Recall | F1 Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| Chili - Bacterial Spot | 0.00 | 0.00 | 0.00 | 0 |
| Chili - Healthy | 0.69 | 0.64 | 0.67 | 14 |
| Maize - Healthy | 0.00 | 0.00 | 0.00 | 0 |
| Maize - Northern Leaf Blight | 0.97 | 1.00 | 0.99 | 37 |
| Potato - Early Blight | 0.75 | 0.13 | 0.22 | 23 |
| Potato - Healthy | 0.00 | 0.00 | 0.00 | 0 |
| Potato - Late Blight | 0.46 | 0.58 | 0.51 | 19 |
| Tomato - Bacterial Spot | 0.00 | 0.00 | 0.00 | 0 |
| Tomato - Early Blight | 0.20 | 0.06 | 0.10 | 16 |
| Tomato - Healthy | 0.53 | 0.81 | 0.64 | 31 |
| Tomato - Late Blight | 0.00 | 0.00 | 0.00 | 0 |
| Tomato - Septoria Leaf Spot | 0.57 | 0.65 | 0.61 | 26 |

## 5. Comparison: ORIGINAL vs CLEAN TEST
| Metric | Original TEST (N=284) | CLEAN TEST (N=166) | Delta |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 45.42% | 62.05% | **+16.63%** |
| **Macro F1** | 32.17% | 37.31% | **+5.14%** |
| **Weighted F1** | 41.16% | 58.95% | **+17.79%** |

*Analysis: The baseline model was heavily penalized in the Original TEST set because it was being graded against contradictory ground-truth labels. When evaluating only on unambiguously labeled field images, the model's domain generalization is actually much stronger (62%) than originally measured (45%).*

## 6. Trustworthiness Statement
**Is the CLEAN TEST set sufficiently trustworthy to become our benchmark?**
**NO.**

While cleaning the dataset restored accuracy metrics by removing explicit contradictions, it completely destroyed the support for five critical classes (bringing them to 0). A benchmark that cannot evaluate Tomato Late Blight, Tomato Bacterial Spot, Chili Bacterial Spot, Maize Healthy, or Potato Healthy is fundamentally incapable of acting as a reliable generalization benchmark for this 12-class product.

PlantDoc is too small and noisy to serve as a robust, balanced evaluation benchmark.
