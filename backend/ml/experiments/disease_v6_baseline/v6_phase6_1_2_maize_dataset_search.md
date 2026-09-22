# V6 Phase 6.1.2 — Maize Classification Dataset Search

## 1. Candidate Comparison Table

| Feature | Cand 1: Corn Leaf Disease Classification | Cand 2: Maize Leaf Dataset (Figshare) | Cand 3: CD&S Dataset (Ahmad et al.) | Cand 4: Maize Ident. & Categ. (Zenodo) |
| :--- | :--- | :--- | :--- | :--- |
| **Repository** | Mendeley Data | Figshare | OSF / arXiv | Zenodo |
| **DOI / ID** | 10.17632/hmkd6nbngr.1 | "Maize Leaf Dataset" | osf.io/s6ru5 | 10.5281/zenodo.21600476 |
| **Authors/Year** | Md Shajedur Rahman (2026) | Unknown | Ahmad et al. (2021) | Gagana S. L. et al. (2026) |
| **Exact Healthy Count**| UNKNOWN (from 17k total) | UNKNOWN | FAIL (0 in raw dataset) | 1,162 (Matches PlantVillage) |
| **Exact NLB Count** | UNKNOWN (labeled Blight) | 342 | UNKNOWN (from 1597 total) | 1,146 (Matches PlantVillage) |
| **Orig vs Aug** | UNKNOWN | UNKNOWN | Both (Separated) | UNKNOWN |
| **Label Type** | Image-level | Image-level | Image-level | Image-level |
| **Field Cond.** | Field | Field | Field | FAIL (Likely Lab/PV) |
| **Location** | UNKNOWN (likely Bangladesh) | UNKNOWN | West Lafayette, IN, USA | UNKNOWN |
| **License** | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| **Commercial Use** | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| **Reproducibility**| PASS | PASS | PASS | PASS |
| **Overlap Risk** | UNKNOWN | UNKNOWN | Low | FAIL (Extreme PV overlap) |
| **NLB Mapping** | `EQUIVALENT_MAPPING` (Blight) | `EXACT_MATCH` | `EXACT_MATCH` | `EQUIVALENT_MAPPING` (Blight) |
| **Healthy Mapping**| `EXACT_MATCH` | `EXACT_MATCH` | `NOT_AVAILABLE` | `EXACT_MATCH` |

## 2. Evidence Gaps
1. **Candidate 1 (Mendeley)** provides field conditions and image-level labels, but the exact per-class counts (for Healthy and NLB) out of the 17,000 total images are unverified. Furthermore, the risk of PlantVillage overlap or augmented images is unknown without downloading the manifest.
2. **Candidate 2 (Figshare)** has a confirmed count for NLB (342 images) but an unknown exact count for Healthy. Licensing and commercial use status are also unverified.
3. **Candidate 3 (CD&S)** perfectly captures field conditions but completely fails on providing a Healthy class in the raw images (researchers typically supplement it with PlantVillage).
4. **Candidate 4 (Zenodo)** perfectly reports its counts, but the counts (1,162 Healthy, 1,146 Blight) match PlantVillage exactly, definitively failing the "no known overlap with PlantVillage" constraint.

## 3. Recommended Candidate(s)
**Candidate 1 (Corn Leaf Disease Classification Dataset, Mendeley Data, 2026)** and **Candidate 2 (Maize Leaf Dataset, Figshare)** are the only viable recommendations.

Candidate 3 is disqualified due to lacking a Healthy class, and Candidate 4 is disqualified due to extreme PlantVillage overlap risk. To proceed, Candidate 1 or 2 must be downloaded to inspect their index files, verifying exact class counts and evaluating the presence of augmented data.

## 4. Acquisition Readiness
**PARTIALLY READY — SPECIFIC GAPS** (or NOT READY)

Maize Healthy and Maize Northern Leaf Blight are **NOT** ready for immediate benchmark acquisition. No single candidate currently has fully verified, metadata-backed evidence confirming >=50 *original* images for *both* classes while guaranteeing field conditions and zero PlantVillage overlap. We are blocked by the inability to read exact class distributions and licenses from Mendeley/Figshare without downloading the datasets.
