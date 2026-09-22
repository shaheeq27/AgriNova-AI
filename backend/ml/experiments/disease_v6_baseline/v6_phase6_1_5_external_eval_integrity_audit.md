# V6 Phase 6.1.5C — Final External Benchmark Integrity Fix

## 1. Class Coverage
The current usable benchmark contains images across **11 of the 12 target classes**.
**Missing Target Class:** Tomato - Bacterial Spot

**Why Tomato Bacterial Spot is unavailable:**
The `tomato_bangladesh` dataset stores annotations in a format containing numerical class IDs (e.g., `6 0.56 0.65 ...`). There is no `classes.txt`, `.yaml`, or `.json` mapping file available within the repository to resolve these IDs into explicit class names. To enforce strict labeling integrity and avoid inferring labels from ambiguous file patterns, the Bangladesh dataset has been excluded in its entirety.

## 2. Global Inventory
- **Total Physical Files**: 38851
- **Corrupt / Unreadable**: 0
- **Excluded (Augmented)**: 12000
- **Excluded (Taxonomy/Unsupported/Ambiguous)**: 5325

## 3. Leakage Claim
- **Exact MD5 overlap with training**: 0
- **Identical dHash overlap with training**: 0
- **Limitations of dHash equality**: While dHash indicates strong perceptual similarity, a dHash collision does not mathematically guarantee zero visual overlap. Manual inspection of near-matches would be required for absolute certainty, though the absence of identical hashes strongly supports independent provenance.

## 4. Internal Duplicate Conflicts
- **Internal Exact Duplicates**: 334
- **Internal Perceptual Duplicates**: 3295

**Conflict Analysis:**
- **Exact MD5 Conflicts**: 5 (These represent genuine label conflicts where the exact same image file was assigned two different labels).
- **dHash Conflicts**: 1200 (These likely represent perceptual collisions or near-similar images—such as different crops or augmented variations that ended up in different folders).

**Examples of Conflicting Labels:**
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Early Blight)
- dHash: tomato_pakistan (Tomato - Early Blight) vs tomato_pakistan (Tomato - Late Blight)
- dHash: tomato_pakistan (Tomato - Septoria Leaf Spot) vs tomato_pakistan (Tomato - Late Blight)
- dHash: tomato_pakistan (Tomato - Early Blight) vs tomato_pakistan (Tomato - Late Blight)
- dHash: tomato_pakistan (Tomato - Early Blight) vs tomato_pakistan (Tomato - Late Blight)

## 5. Dataset Breakdown
### tomato_pakistan
- **Usable Count**: 4412
  - Tomato - Septoria Leaf Spot: 1119
  - Tomato - Healthy: 1121
  - Tomato - Early Blight: 1019
  - Tomato - Late Blight: 1153

### maize_enlin_li
- **Usable Count**: 590
  - Maize - Northern Leaf Blight: 278
  - Maize - Healthy: 312

### potato_pldd_up
- **Usable Count**: 12298
  - Potato - Healthy: 2931
  - Potato - Early Blight: 3974
  - Potato - Late Blight: 5393

### chili_krishna_v3
- **Usable Count**: 597
  - Chili - Bacterial Spot: 148
  - Chili - Healthy: 449

## 6. Final Readiness
**EVALUATION_READY_11_CLASS**
The benchmark is ready for 11 classes. Tomato Bacterial Spot requires further dataset acquisition to be included.
