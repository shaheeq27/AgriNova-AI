# V6 Phase 6.0.2: Evaluation Dataset Strategy & Acquisition Audit

## 1. Current Dataset Inventory

**Existing Datasets Evaluated:**
- **PlantVillage (PV)**: ~15,000 images currently assigned to TRAIN.
  - *Condition*: Strict laboratory conditions (single leaf, homogenous backgrounds).
  - *Status*: Valid for feature representation training but **useless** for measuring real-world field generalization (severe domain shift).
- **PlantDoc (PD)**: ~1,350 images currently assigned to TEST/VALIDATION.
  - *Condition*: Field conditions, internet-scraped.
  - *Status*: Phase 6.0.1 audit revealed catastrophic label noise (41% exact image duplication across conflicting classes). When cleaned, 5 of our 12 required classes dropped to zero support. **Cannot be used as a primary standalone benchmark**.

**Bottom Line**: We currently possess exactly **zero** trustworthy, field-condition evaluation datasets that cover the required 12 classes with sufficient statistical support.

## 2. Research: Candidate External Datasets

We researched public datasets known to feature uncontrolled, real-world field conditions for the target crops (Tomato, Potato, Maize, Chili).

| Dataset | Source/Repository | Crops Covered | Conditions | Label Quality | Overlap Risk w/ PV & PD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AI Challenger 2018 (PDR2018)** | AI Challenger Competition | Corn (Maize), Pepper (Chili), Potato, Tomato (+6 others) | Real-world / Field (smartphone captures by Chinese farmers) | High (Competition curated, 61 strict classes including severity) | Low (Independent collection) |
| **PLDD-UP** | Mendeley Data | Potato | Field (Uttar Pradesh, India) | High (15k+ images) | Low |
| **FieldPlant** | Mendeley Data | Maize, Tomato, Cassava | Field plantations | Expert-annotated | Low |
| **TOM2024** | NIH / WASCAL | Tomato, Maize, Onion | Field (Burkina Faso) | High (25k+ raw images) | Low |
| **Chili Leaf Dataset** | Mendeley Data | Chili (Bell Pepper) | Field (India) | High | Low |

## 3. Coverage Analysis for AgriNova's 12 Classes

To establish a singular benchmark, a dataset must cover all 12 of our classes (including healthy representations).

- **Chili Healthy**
- **Chili Bacterial Spot**
- **Maize Healthy**
- **Maize Northern Leaf Blight**
- **Potato Healthy**
- **Potato Early Blight**
- **Potato Late Blight**
- **Tomato Healthy**
- **Tomato Bacterial Spot**
- **Tomato Early Blight**
- **Tomato Late Blight**
- **Tomato Septoria Leaf Spot**

**Single-Source Viability**:
- Datasets like *PLDD-UP*, *FieldPlant*, and *TOM2024* are highly robust but crop-specific. None can serve as a unified 12-class benchmark alone.
- **AI Challenger 2018** is the only candidate that structurally encompasses Corn (Maize), Pepper (Chili), Potato, and Tomato simultaneously within a single curated taxonomy. It is highly probable that PDR2018 covers the exact required diseases (e.g., Northern Leaf Blight, Early/Late Blight).

## 4. Proposed Evaluation Structure

We cannot rely on a single flawed dataset. We propose a dual-tier evaluation framework:

### A. PRIMARY TEST: The Trustworthy Benchmark
**Composition**: A composite dataset primarily derived from **AI Challenger 2018 (PDR2018)**, supplemented by crop-specific field datasets (e.g., PLDD-UP for Potato, FieldPlant for Maize) if AI Challenger lacks support for specific minor classes like Chili Bacterial Spot.
**Purpose**: To definitively measure the model's accuracy, precision, and recall on clean, undisputed, real-world data. This determines if the model is ready for production.

### B. SECONDARY TEST: The Robustness/Adversarial Benchmark
**Composition**: The **Cleaned PlantDoc Dataset** (166 images).
**Purpose**: PlantDoc contains extreme internet-scraped noise, unusual angles, and multiple diseases per leaf. While it lacks support for 5 classes, testing the remaining 7 classes against it will provide a strict "stress test" for out-of-distribution robustness.

## 5. Minimum Requirements for the PRIMARY TEST

Before accepting any dataset into the PRIMARY TEST, it must pass these strict gates:
1. **Zero Known Label Conflicts**: Must pass the exact MD5/dHash intra-dataset duplication audit (Phase 6.0.1 protocol) to ensure no conflicting labels exist.
2. **Adequate Support**: A minimum of 50 images per class strictly allocated to the TEST split.
3. **Field Authenticity**: Images must feature complex backgrounds, variable lighting, and uncropped contexts (no black/white lab backgrounds).
4. **Zero Data Leakage**: Absolute guarantee that the dataset does not overlap with the PlantVillage TRAIN set (verified via perceptual hashing).
5. **Image-Level Disease Labels**: Severity labels are optional (since V6 is currently classification-only), but the discrete disease label must be exact and unambiguous.

## 6. Next Steps

1. **Acquisition Audit**: Download the index/manifest for **AI Challenger 2018 (PDR2018)** to map its 61 classes against our 12 required classes.
2. **Supplementation Strategy**: If AI Challenger lacks specific classes (e.g., Chili Bacterial Spot), define the exact supplementary dataset (e.g., Mendeley Chili Leaf Dataset) to fill the gap.
3. **Primary Test Compilation**: Construct a new `primary_benchmark_manifest.csv` adhering to the minimum requirements.
