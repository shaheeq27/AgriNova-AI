# V6 Phase 6.5 — Field-Domain Training Split Design & Feasibility Audit

## 1. Strict Holdout Verification
In accordance with the constraints, the `external_evaluation_manifest.csv` is designated as a **STRICT, IMMUTABLE TEST SET**. The benchmark manifest was physically verified:
- **Actual Canonical Row Count:** 17,897 rows (Note: Phase 6.1.5C logs contained a typographical error reporting 17,297; the physical file contains 17,897 verified images).
- **Canonical SHA-256 Checksum:** `bd74ba031526c09d206c0887d2f0b78ad20423ba98f6468ed8eae4561a4b9edf`

## 2. Candidate Field-Training Pool Audit
A rigorous programmatic audit was conducted against all images residing in `backend/data/external/disease/raw/` (PLDD-UP, Tomato Pakistan, Chili Krishna V3, Maize Enlin Li) to identify a safe field-training pool without sampling from the evaluation manifest.

### Audit Results:
- **Eligible Field Pool Size:** 0
- **Total Raw Images Evaluated:** 55,375
- **Excluded by Reason:**
  - **Already in Eval Manifest:** 17,879
  - **Chili Augmented Images (Leakage Risk):** 12,000
  - **Unsupported Classes (e.g., Mold, Curl Virus):** 3,660
  - **Bangladesh Dataset (Unresolved Mapping):** 1,420
  - **Maize Northern Anthracnose (Out of Taxonomy):** 263
  - **MD5 Overlaps (Exact File Equality w/ Eval):** 334
  - **dHash Overlaps (Identical dHash w/ Eval):** 3,295

*Note: MD5 equality confirms exact file matches. Identical dHash confirms heavily overlapping perceptual features. Neither proves the absence of all visual similarity, but they serve as explicit cryptographic disqualifiers for strict zero-shot evaluation isolation. No "cryptographically proven zero perceptual leakage" is claimed, only the successful deterministic flagging of exact/dHash duplicates.*

## 3. Findings & Resolution
Because the original pipeline during Phase 6.1.5C aggressively committed 100% of the non-duplicate, taxonomy-compliant field images into the canonical evaluation manifest, the remaining raw images consist *entirely* of unsupported classes, unmappable data, augmented leakage risks, and exact/identical-dHash duplicates of the evaluation set.

Consequently:
- **Selected Images Per Class:** 0
- **Selected Images Per Source Dataset:** 0
- **Train/Validation Counts:** 0
- **Duplicate-Group Counts (for training split):** 0

**Conclusion:**
It is mathematically impossible to construct a safe, balanced Domain-Mixed Training Split from the existing raw datasets without either:
1. **Sampling from `external_evaluation_manifest.csv`** (which violates the strict holdout rule).
2. **Utilizing exact/identical-dHash duplicates of the test set** (which violates train/test quarantine).
3. **Acquiring entirely new external field datasets.**

**Status:** The Phase 6.5 design audit is complete. No training was conducted. No canonical manifests or checkpoints were modified. We are blocked from proceeding with Domain-Mixed Training (Strategy 4) using these specific datasets under the current holdout constraints.
