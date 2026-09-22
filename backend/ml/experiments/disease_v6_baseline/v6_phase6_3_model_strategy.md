# V6 Phase 6.3 — Model Strategy & Controlled Experiment Design

## Empirical Foundation (Phase 6.2 Findings)
- **External accuracy:** 27.20%
- **External Macro F1:** 0.2814
- **Crop-level accuracy:** 45.67%
- **Potato → Tomato confusion:** 8,212 images
- **Conditional disease accuracy:** Chili (91.4%), Tomato (60.7%), Maize (58.3%), Potato (53.7%)
- **Healthy/Diseased binary accuracy:** 73.18%
- **Non-Potato true-label accuracy:** 58.06%

*Note: While conditional disease accuracy shows some capability, disease classification is far from solved (e.g., Potato conditional accuracy is only 53.7%). Furthermore, while the non-Potato accuracy (58.06%) is a useful reference point, previous PlantDoc clean results (62.05%) cannot be treated as a definitive field-generalization baseline.*

---

## Strategy Comparison

### 1. Current Flat 12-Class ResNet-18
- **Addresses:** N/A (Baseline condition)
- **Architectural Changes:** None
- **Training-Data Requirements:** Existing `dataset_manifest.csv`
- **Leakage Risks:** Minimal (strict zero-shot evaluation barrier maintained)
- **Evaluation Requirements:** External field benchmark evaluation
- **Implementation Complexity:** Low
- **Expected Experimental Value:** Provides the baseline. Proves that flat classification collapses under crop-level domain shift in field conditions.

### 2. Hierarchical Crop → Disease Classification
- **Addresses:** Severe crop misclassification (45.67% crop accuracy) masking downstream disease recognition.
- **Architectural Changes:** Two-stage sequential pipeline (Model A: Crop Classifier ➔ Model B: Disease Classifier per crop).
- **Training-Data Requirements:** Existing dataset, partitioned for separate training routines.
- **Leakage Risks:** Minimal.
- **Evaluation Requirements:** Independent evaluation of Crop accuracy vs. Disease accuracy.
- **Implementation Complexity:** Medium (requires managing, chaining, and evaluating multiple checkpoints).
- **Expected Experimental Value:** Isolates crop failures from pathology failures, but downstream disease accuracy becomes strictly bottlenecked by the first-stage crop model's errors.

### 3. Multi-task Crop + Disease Classification
- **Addresses:** Feature conflation; forcing the model to explicitly disentangle host-plant morphology from localized pathology features.
- **Architectural Changes:** Single shared backbone with two parallel classification heads (Head 1: Crop [4 classes], Head 2: Disease Status).
- **Training-Data Requirements:** Existing dataset, remapped to output two target labels per image.
- **Leakage Risks:** Minimal.
- **Evaluation Requirements:** Track separate loss weighting and dual metrics (Crop vs. Disease).
- **Implementation Complexity:** Medium (requires custom PyTorch `nn.Module` and multi-task loss formulation).
- **Expected Experimental Value:** High. Encourages robust representation sharing and directly penalizes cross-crop confusion (e.g., predicting Potato as Tomato) without relying on new external training data.

### 4. Field-Data Domain Mixing / Fine-Tuning
- **Addresses:** The profound domain shift between the training data and real agricultural field data.
- **Architectural Changes:** None.
- **Training-Data Requirements:** Requires sampling verified external field images into the training split.
- **Leakage Risks:** High. Breaking the zero-shot integrity of the external benchmark requires extremely rigid train/test stratification to prevent data leakage.
- **Evaluation Requirements:** Cross-validation on a strictly quarantined hold-out subset of the field data.
- **Implementation Complexity:** Medium (demands rigorous manifest engineering and leakage auditing).
- **Expected Experimental Value:** High. Directly bridges the domain gap, but masks whether the architecture itself is robust or simply memorizing a new domain.

### 5. Background Robustness Augmentation
- **Addresses:** Suspected (but unproven) reliance on artificial training context and irrelevant background artifacts.
- **Architectural Changes:** None.
- **Training-Data Requirements:** Existing dataset processed with heavy spatial/color augmentation (e.g., CutMix, aggressive cropping) or foreground segmentation.
- **Leakage Risks:** Minimal.
- **Evaluation Requirements:** Standard zero-shot external evaluation.
- **Implementation Complexity:** Low (for torchvision transforms) to High (for segmentation pipelines).
- **Expected Experimental Value:** Moderate. Forces the model to extract intrinsic foliar features, though it may not fully resolve deep morphological crop confusion.

---

## Proposed Next Experiment

**Hypothesis:**
Forcing explicit disentanglement of host-plant morphology from pathological features via a **Multi-Task Learning (MTL) architecture** will significantly reduce catastrophic cross-crop confusion (e.g., Potato ➔ Tomato) and improve overall 11-class zero-shot field generalization, without requiring external domain mixing.

**Controlled Experiment: Multi-Task Crop + Disease Architecture**
- **Action:** Implement a ResNet-18 with a shared backbone and dual classification heads (Crop: 4 classes; Disease Status).
- **Control:** The current flat 12-class ResNet-18 baseline.
- **Training Data:** Exactly the same `dataset_manifest.csv` as the baseline. No new datasets. No domain mixing.
- **Success Criteria:**
  1. Crop-level accuracy on the external benchmark increases from the 45.67% baseline to > 70%.
  2. The massive Potato ➔ Tomato confusion (8,212 images) is reduced by at least 50%.
  3. Overall 11-class external accuracy exceeds the 27.20% baseline.
