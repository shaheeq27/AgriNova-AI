# V6 Phase 6.7 — Final Research Conclusion & Audit

## 1. Experimental Verification Audit
Before concluding the V6 disease classification experiments, a final cryptographic and computational audit was performed to guarantee the integrity of Phase 6.6 results.

- **External Evaluation Manifest Hash:** `bd74ba031526c09d206c0887d2f0b78ad20423ba98f6468ed8eae4561a4b9edf` (Unchanged from Phase 6.5 audit).
- **External Evaluation Count:** 17,897 images (11-class benchmark. *Note: Tomato Bacterial Spot remains unsupported in the field benchmark*).
- **Training Manifest Leakage Check:** The canonical `dataset_manifest.csv` hash remains entirely unchanged. Zero external field images entered the training or validation splits.
- **Checkpoint Consistency:** `robust_best_model.pth` exists and corresponds identically to the logged Phase 6.6 configuration.
- **Error Calculations Verified:**
  - Within-crop errors: 5,029 confirmed.
  - Potato Late Blight ➔ Potato Early Blight: 1,453 confirmed.

## 2. Success Criteria Verification
The Phase 6.6 Domain-Robust Augmentation experiment altered **only** the augmentation pipeline (targeting lighting, viewpoint, blur, and occlusion) while freezing the ResNet-18 architecture, optimizer, and training data.

| Predefined Criterion | Target | Actual (Phase 6.6) | Result |
| :--- | :--- | :--- | :--- |
| **1. Overall External Accuracy** | Exceed 29.20% | 36.92% (+9.72 pp) | ✅ Passed |
| **2. Crop Accuracy** | Exceed 60.00% | 65.02% (+19.35 pp) | ✅ Passed |
| **3. Potato ➔ Tomato Errors** | ≤ 5,748 errors | 3,482 errors (-57.6%) | ✅ Passed |

## 3. Configuration & Artifact Record
- **Model:** ResNet-18 (Flat 12-class head).
- **Seed:** 42 (Deterministic).
- **Training Split:** `dataset_manifest.csv` (PlantVillage + PlantDoc).
- **Evaluation Split:** `external_evaluation_manifest.csv` (Strict zero-shot holdout).
- **Phase 6.6 Artifacts:**
  - Design: `v6_phase6_6_augmentation_design.md`
  - Training Script: `train_robust.py`
  - Evaluation Script: `evaluate_robust.py`
  - Raw Results: `v6_phase6_6_robust_experiment.md`
  - Metrics: `robust_confusion_matrix.npy`, `class_mapping.json`
  - Checkpoint: `robust_best_model.pth`

## 4. Final Scientific Conclusion
The experimental chain (Phases 6.0 through 6.6) provides strong evidence regarding the failure modes of lab-trained CNNs in agricultural environments.

**Finding 1: Cross-Domain Crop Recognition**
Under the current PlantVillage/PlantDoc training data, ResNet-18 architecture, and training procedure, the domain-targeted augmentation intervention substantially improved external crop recognition (45.67% ➔ 65.02%) and reduced catastrophic cross-crop errors (e.g., Potato ➔ Tomato dropped by 57.6%). The results are consistent with the model gaining improved robustness to domain variation (lighting, background, perspective) without requiring the acquisition of new field data.

**Finding 2: The Disease-Discrimination Bottleneck**
As crop-level recognition improved, the dominant failure mode decisively shifted. The new primary bottleneck is **fine-grained within-crop disease discrimination**, evidenced by 5,029 within-crop errors (including 1,453 Potato Late Blight images misclassified as Potato Early Blight).

**Conclusion:**
Domain-robust augmentation substantially improves cross-domain crop recognition, while fine-grained disease discrimination remains constrained by the lack of sufficiently representative field-labeled training data. Therefore, the classifier's limitation is fundamentally grounded in the training data distribution, and further architecture or augmentation tuning is unlikely to yield reliable 12-class field performance without acquiring comprehensive, field-annotated pathology datasets.

**Model experiments for V6 Disease Classification are now officially locked.**
