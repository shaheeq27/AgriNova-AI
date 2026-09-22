# V6 Phase 6.1: Primary Benchmark Dataset Research

## 1. Candidate Dataset Inventory

1. **PLDD-UP (Potato Leaf Disease Dataset)**
   - **Host:** Mendeley Data (Stable, Authoritative)
   - **Author/Org:** Prakash Kumar Singh et al.
   - **Year:** 2026
   - **Crops:** Potato
   - **Disease Classes:** Early Blight, Late Blight, Healthy
   - **Image Counts:** 15,519 (EB: 4,803, LB: 6,116, Healthy: 4,600)
   - **Field/Lab:** Field (Rabi season, Uttar Pradesh, India)
   - **Label Type:** Image-level
   - **License:** CC BY 4.0 (Mendeley Default)
   - **Commercial-use:** PASS
   - **Redistribution:** PASS
   - **Download Reproducibility:** PASS

2. **Tomato Leaf Disease Classification Dataset (Pakistan)**
   - **Host:** Mendeley Data (Stable, Authoritative)
   - **Author/Org:** Malik, Mohammad Naeem et al.
   - **Year:** 2026
   - **Crops:** Tomato
   - **Disease Classes:** Early Blight, Late Blight, Septoria Leaf Spot, Leaf Mold, Yellow Leaf Curl Virus, Healthy
   - **Image Counts:** 7,200
   - **Field/Lab:** Field (Agricultural fields in Pakistan via smartphone)
   - **Label Type:** Image-level
   - **License:** CC BY 4.0 (Mendeley Default)
   - **Commercial-use:** PASS
   - **Redistribution:** PASS
   - **Download Reproducibility:** PASS

3. **Tomato Leaf Dataset (Multiclass Bangladesh)**
   - **Host:** Mendeley Data (Stable, Authoritative)
   - **Author/Org:** Ahmed Imtiaz et al.
   - **Year:** 2025
   - **Crops:** Tomato
   - **Disease Classes:** Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Target Spot, Healthy, Black Spot
   - **Image Counts:** 731 total
   - **Field/Lab:** Field (Tomato gardens in Bangladesh)
   - **Label Type:** Image-level
   - **License:** CC BY 4.0
   - **Commercial-use:** PASS
   - **Redistribution:** PASS
   - **Download Reproducibility:** PASS

4. **Chili Leaf Diseases Dataset (Krishna River Basin)**
   - **Host:** Mendeley Data (Stable, Authoritative)
   - **Author/Org:** Independent researchers (India)
   - **Year:** 2023-2025
   - **Crops:** Chili (Bell Pepper)
   - **Disease Classes:** Bacterial Spot, Curl Virus, Cercospora Leaf Spot, Nutrition Deficiency, White Spot, Healthy
   - **Image Counts:** 1,856 original images
   - **Field/Lab:** Field (Deccan Plateau, India)
   - **Label Type:** Image-level
   - **License:** CC BY 4.0 (Mendeley Default)
   - **Commercial-use:** PASS
   - **Redistribution:** PASS
   - **Download Reproducibility:** PASS

5. **OSF Maize NLB Dataset**
   - **Host:** OSF / Open Science Framework (Stable, Authoritative)
   - **Author/Org:** Wiesner-Hanks et al.
   - **Year:** 2017/2019
   - **Crops:** Maize
   - **Disease Classes:** Northern Leaf Blight, Healthy
   - **Image Counts:** 8,766
   - **Field/Lab:** Field
   - **Label Type:** Image-level & annotations
   - **License:** Academic/Research Use Only
   - **Commercial-use:** FAIL
   - **Redistribution:** PASS (within academic bounds)
   - **Download Reproducibility:** PASS

## 2. Evidence/Source Quality
All candidates selected are hosted on **authoritative, permanent repositories** (Mendeley Data, OSF) with valid DOIs. None rely on Kaggle or GitHub third-party mirrors. Primary documentation (methods, locations, devices) is explicitly available for all datasets.

## 3. License/Provenance
With the exception of the OSF dataset (Academic use only), the Mendeley datasets default to standard Creative Commons attribution licenses (e.g., CC BY 4.0), permitting redistribution and derivative works.

## 4. Field-Condition Verification
Every dataset was explicitly selected for being captured in **real-world agricultural fields** using smartphones or consumer digital cameras under natural lighting and complex backgrounds, entirely distinct from laboratory constraints.

## 5. Class-Level Coverage & Mapping Table
| AgriNova Class | Candidate Dataset | Mapping Type | Contributed |
| :--- | :--- | :--- | :--- |
| Chili Healthy | Dataset 4 (Chili Leaf) | `EXACT_MATCH` | Yes |
| Chili Bacterial Spot | Dataset 4 (Chili Leaf) | `EXACT_MATCH` | Yes |
| Maize Healthy | Dataset 5 (OSF NLB) | `EXACT_MATCH` | Yes |
| Maize Northern Leaf Blight | Dataset 5 (OSF NLB) | `EXACT_MATCH` | Yes |
| Potato Healthy | Dataset 1 (PLDD-UP) | `EXACT_MATCH` | Yes |
| Potato Early Blight | Dataset 1 (PLDD-UP) | `EXACT_MATCH` | Yes |
| Potato Late Blight | Dataset 1 (PLDD-UP) | `EXACT_MATCH` | Yes |
| Tomato Healthy | Dataset 2 (Tomato Pakistan) | `EXACT_MATCH` | Yes |
| Tomato Bacterial Spot | Dataset 3 (Tomato Bangladesh) | `EXACT_MATCH` | Yes |
| Tomato Early Blight | Dataset 2 (Tomato Pakistan) | `EXACT_MATCH` | Yes |
| Tomato Late Blight | Dataset 2 (Tomato Pakistan) | `EXACT_MATCH` | Yes |
| Tomato Septoria Leaf Spot | Dataset 2 (Tomato Pakistan) | `EXACT_MATCH` | Yes |

*Note: All mappings are conservative direct matches without assumptions.*

## 6. Image Counts
All datasets provide thousands of images, easily guaranteeing `>=50` images per class, **except** Dataset 3 (Tomato Bangladesh) which contains 731 images across 7 classes (~104 per class). This likely exceeds 50 for Bacterial Spot, but poses a slight statistical risk if severely imbalanced.

## 7. Coverage Matrix

| Class | Dataset 1 (PLDD-UP) | Dataset 2 (Tom-Pak) | Dataset 3 (Tom-Ban) | Dataset 4 (Chili) | Dataset 5 (Maize) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chili Healthy** | FAIL | FAIL | FAIL | **PASS** | FAIL |
| **Chili Bacterial Spot** | FAIL | FAIL | FAIL | **PASS** | FAIL |
| **Maize Healthy** | FAIL | FAIL | FAIL | FAIL | **PASS** |
| **Maize NLB** | FAIL | FAIL | FAIL | FAIL | **PASS** |
| **Potato Healthy** | **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Potato Early Blight** | **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Potato Late Blight** | **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Tomato Healthy** | FAIL | **PASS** | PASS | FAIL | FAIL |
| **Tomato Bacterial Spot**| FAIL | FAIL | **UNKNOWN** (Count) | FAIL | FAIL |
| **Tomato Early Blight** | FAIL | **PASS** | PASS | FAIL | FAIL |
| **Tomato Late Blight** | FAIL | **PASS** | PASS | FAIL | FAIL |
| **Tomato Septoria Spot** | FAIL | **PASS** | FAIL | FAIL | FAIL |

## 8. Minimum Coverage Set
The absolute minimum set required to cover all 12 classes with reproducible, authoritative field imagery consists of **5 independent datasets** (Datasets 1 through 5). While exceeding the preferred 2-4 limit, quality and provenance took absolute priority, guaranteeing verifiable origin and licensing over dataset count reduction.

## 9. Uncovered Classes
- None. All 12 classes are covered.
- *Risk note:* Tomato Bacterial Spot (Dataset 3) must be verified to contain `>=50` images upon download.

## 10. PlantDoc Secondary Benchmark Role
PlantDoc retains its role purely as a secondary robustness/adversarial benchmark. It will not be used to fill any gaps in the primary benchmark due to its unresolved label-conflict integrity issues.

## 11. Risks and Limitations
- **Cross-Dataset Leakage:** Because these datasets were collected independently across India, Pakistan, Bangladesh, and the US, cross-dataset leakage is impossible.
- **Overlap with PlantVillage:** Since these datasets were created between 2017-2026 from independent field collection drives, they are fundamentally distinct from the 2015 lab-based PlantVillage. Regardless, cryptographic hashing will be enforced.
- **Dataset 5 Commercial Status:** The OSF Maize dataset restricts commercial use. Depending on AgriNova's corporate classification, this dataset's usage may remain strictly academic/internal.

## 12. Recommended Acquisition Plan
1. Download the 5 authoritative datasets via their direct DOIs/Mendeley/OSF links.
2. Filter explicitly for the 12 target classes.
3. Apply MD5 and dHash to deduplicate against PlantVillage TRAIN and within the new benchmark itself.
4. Finalize the `primary_benchmark_manifest.csv`.

## 13. Final Decision
**PARTIALLY READY — SPECIFIC GAPS**

*Gap:* We must verify if the 731-image Tomato Bangladesh dataset contains precisely `>=50` images of Tomato Bacterial Spot. Assuming it passes, the benchmark is otherwise fully ready for acquisition.

---

## Phase 6.1.1 — Metadata & Class-Count Verification

### 1. Chili Dataset Verification
- **Dataset**: Image Dataset on Chili Leaf Diseases in the Krishna River Basin
- **Bacterial Spot Count**: UNKNOWN
- **Healthy Count**: UNKNOWN
- **Original vs Augmented**: The dataset explicitly contains 1,856 original images and 12,000 augmented images. Because the exact class distribution among the *original* subset is not verifiable without downloading the index, we cannot guarantee `>=50` original images per class.
- **Status**: UNKNOWN (Requires manifest download)

### 2. Bangladesh Tomato Dataset Verification
- **Dataset**: Tomato Leaf Dataset : A dataset for multiclass disease detection and classification
- **Bacterial Spot Count**: UNKNOWN
- **Healthy Count**: UNKNOWN
- **Early Blight Count**: UNKNOWN
- **Late Blight Count**: UNKNOWN
- **Status**: UNKNOWN (We refuse to use the `731 / 7` assumption. Explicit metadata is required.)

### 3. Pakistan Tomato Dataset Verification
- **Dataset**: Tomato Leaf Disease Classification Dataset in Pakistan
- **Healthy Count**: UNKNOWN
- **Early Blight Count**: UNKNOWN
- **Late Blight Count**: UNKNOWN
- **Septoria Leaf Spot Count**: UNKNOWN
- **Status**: UNKNOWN (Total is 7,200, but explicit per-class counts are unavailable via small metadata search.)

### 4. PLDD-UP Verification
- **Dataset**: Potato Leaf Disease Dataset from Uttar Pradesh, India
- **Healthy Count**: 4,600 (Verified)
- **Early Blight Count**: 4,803 (Verified)
- **Late Blight Count**: 6,116 (Verified)
- **Authoritative Source**: Mendeley Data (DOI: 10.17632/3j4nfkvp2n.1)
- **Status**: PASS

### 5. Maize Dataset (OSF) Verification
- **Dataset**: OSF Northern Leaf Blight (Wiesner-Hanks et al. 2019)
- **Total Image Count**: 8,766 (Per-class counts UNKNOWN)
- **Annotation Type**: The dataset provides bounding box/spline annotations for NLB lesions, not image-level classification labels.
- **Healthy Class Validity**: While the literature states non-infected images are included, there is no explicit image-level "Healthy" label; deriving one from the mere absence of an NLB lesion annotation is an invalid manufacturing of a label.
- **Maize Healthy Mapping**: `NOT_AVAILABLE`
- **Field Conditions**: Field ("Field-acquired images")
- **License**: Academic / Research Use Only
- **Provenance**: Open Science Framework (DOI: 10.17605/OSF.IO/P67RZ)

### 6. Mapping Types (Revised & Conservative)
| AgriNova Class | Candidate Dataset | Original Label | Mapping Type |
| :--- | :--- | :--- | :--- |
| Chili Healthy | Chili (Mendeley) | Healthy Leaves | `EXACT_MATCH` |
| Chili Bacterial Spot | Chili (Mendeley) | Bacterial Spot | `EXACT_MATCH` |
| Maize Healthy | OSF Maize NLB | N/A | `NOT_AVAILABLE` |
| Maize Northern Leaf Blight | OSF Maize NLB | NLB (Lesion) | `INFERRED_MAPPING` (Deriving image-level class from lesion-level annotation) |
| Potato Healthy | PLDD-UP | Healthy | `EXACT_MATCH` |
| Potato Early Blight | PLDD-UP | EB | `EQUIVALENT_MAPPING` |
| Potato Late Blight | PLDD-UP | LB | `EQUIVALENT_MAPPING` |
| Tomato Healthy | Tomato Pakistan | Healthy leaves | `EXACT_MATCH` |
| Tomato Bacterial Spot | Tomato Bangladesh | Bacterial Spot | `EXACT_MATCH` |
| Tomato Early Blight | Tomato Pakistan | Early Blight | `EXACT_MATCH` |
| Tomato Late Blight | Tomato Pakistan | Late Blight | `EXACT_MATCH` |
| Tomato Septoria Leaf Spot | Tomato Pakistan | Septoria Leaf Spot | `EXACT_MATCH` |

### 7. Explicit Licenses
- **Chili Dataset**: UNKNOWN
- **Tomato Bangladesh**: CC BY 4.0 (Verified via metadata search)
- **Tomato Pakistan**: UNKNOWN
- **PLDD-UP**: UNKNOWN
- **OSF Maize**: Academic / Research Use Only

### 8. Verified Field Conditions
- **Chili Dataset**: Field ("plantations")
- **Tomato Bangladesh**: Garden ("tomato gardens")
- **Tomato Pakistan**: Field ("real-time agricultural field conditions")
- **PLDD-UP**: Field ("operational potato fields")
- **OSF Maize**: Field ("field-acquired imagery")

### 9. Leakage Claims
Independent collection provenance reduces expected overlap risk; exact MD5 and dHash checks are required during acquisition against PlantVillage TRAIN and PlantDoc.

### 10. Final Coverage Matrix
| Class | PLDD-UP | Tomato Pak | Tomato Ban | Chili | OSF Maize |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chili Healthy** | FAIL | FAIL | FAIL | **UNKNOWN** | FAIL |
| **Chili Bacterial Spot** | FAIL | FAIL | FAIL | **UNKNOWN** | FAIL |
| **Maize Healthy** | FAIL | FAIL | FAIL | FAIL | **NOT_AVAILABLE** |
| **Maize NLB** | FAIL | FAIL | FAIL | FAIL | **UNKNOWN** |
| **Potato Healthy** | **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Potato Early Blight**| **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Potato Late Blight** | **PASS** | FAIL | FAIL | FAIL | FAIL |
| **Tomato Healthy** | FAIL | **UNKNOWN** | UNKNOWN | FAIL | FAIL |
| **Tomato Bacterial Spot**| FAIL | FAIL | **UNKNOWN** | FAIL | FAIL |
| **Tomato Early Blight**| FAIL | **UNKNOWN** | UNKNOWN | FAIL | FAIL |
| **Tomato Late Blight** | FAIL | **UNKNOWN** | UNKNOWN | FAIL | FAIL |
| **Tomato Septoria Spot** | FAIL | **UNKNOWN** | FAIL | FAIL | FAIL |

*Note: "PASS" requires verified >=50 original images, verified license, verified field conditions, and unambiguous mapping. Any missing element yields UNKNOWN or NOT_AVAILABLE.*

### 11. Final Decision
**PARTIALLY READY — SPECIFIC GAPS**

Unresolved Gaps preventing acquisition:
1. **Unverified Class Counts**: The exact per-class counts of *original* images are unverified for Chili, Tomato Pakistan, Tomato Bangladesh, and OSF Maize.
2. **Missing Licenses**: The explicit dataset licenses for PLDD-UP, Tomato Pakistan, and Chili are unverified.
3. **Maize Healthy Unavailability**: The OSF Maize dataset lacks an explicit image-level classification label for "Healthy", rendering the class `NOT_AVAILABLE`.
4. **Maize NLB Inferred Mapping**: The OSF Maize dataset provides lesion-level bounding boxes, meaning an image-level "Northern Leaf Blight" class must be inferred, which violates strict benchmark labeling requirements.

---

## Phase 6.1.3 — Maize Candidate Metadata Verification

### 1. Candidate Comparison Table

| Metric | Cand 1: Corn Leaf Disease (Mendeley) | Cand 2: Maize Leaf Dataset (Figshare) |
| :--- | :--- | :--- |
| **Exact Healthy Count** | UNKNOWN | UNKNOWN |
| **Exact NLB Count** | UNKNOWN | 342 (CNLB) |
| **Orig vs Aug** | UNKNOWN | UNKNOWN |
| **Label Semantics** | `EQUIVALENT_MAPPING` (Blight) | `EXACT_MATCH` (CNLB) |
| **Field Conditions** | Field ("real-world field conditions") | Field ("field-collected") |
| **License** | CC BY 4.0 | UNKNOWN |
| **Overlap Risk** | Unresolved (Suspected PV overlap) | Unresolved |
| **Decision** | FAIL | FAIL |

### 2. Exact Class Counts
- **Candidate 1:** While the total dataset is ~17,000 images, explicit per-class counts for Healthy and Corn Leaf Blight cannot be derived from the description or API metadata without downloading the dataset archive. We cannot confirm >=50 original images.
- **Candidate 2:** The dataset explicitly confirms 342 images for Northern Leaf Blight (CNLB). However, the exact count for the Healthy class is completely omitted from the metadata summary. We cannot confirm >=50 original images for Healthy.

### 3. Original vs Augmented Evidence
- **Candidate 1:** Unresolved. The metadata states the dataset was "collected from various sources—including field observations and public repositories," but there is no metadata manifest distinguishing original captures from augmented images.
- **Candidate 2:** Unresolved. The description does not clarify if the 342 NLB images are raw originals or if they include synthetic augmentations.

### 4. License Evidence
- **Candidate 1:** Verified as **CC BY 4.0** via the specific Mendeley DOI (10.17632/hmkd6nbngr.1). This permits commercial use and redistribution.
- **Candidate 2:** The explicit license on Figshare is UNKNOWN from small metadata search alone. We cannot assume commercial or redistribution permissions.

### 5. Mapping Evidence
- **Candidate 1:**
  - Maize Healthy -> "Healthy" (`EXACT_MATCH`)
  - Maize Northern Leaf Blight -> "Corn Leaf Blight" (`EQUIVALENT_MAPPING`)
- **Candidate 2:**
  - Maize Healthy -> "Healthy" (`EXACT_MATCH`)
  - Maize Northern Leaf Blight -> "Northern Leaf Blight (CNLB)" (`EXACT_MATCH`)

### 6. Remaining Gaps
Both datasets suffer from opaque metadata that blocks pre-acquisition verification. The most critical gaps are the unverified counts for Healthy images and the inability to distinguish original images from augmented copies (or copies derived directly from PlantVillage).

### 7. Candidate 1 Decision
**FAIL**. The dataset fails the pre-acquisition gates because exact counts, original vs. augmented status, and PlantVillage overlap remain strictly UNKNOWN without a full archive download.

### 8. Candidate 2 Decision
**FAIL**. The dataset fails because the exact Healthy class count, original vs. augmented status, and exact license remain UNKNOWN.

### 9. Whether Maize Healthy + NLB are READY FOR ACQUISITION
**NOT READY**. Both prime candidates failed the metadata verification constraints. We cannot securely acquire a primary evaluation benchmark for Maize without verifying that we have >=50 guaranteed original, non-augmented, field-condition images that definitively do not overlap with PlantVillage.
