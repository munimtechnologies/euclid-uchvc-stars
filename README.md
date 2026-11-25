# euclid-uchvc-stars

Do compact high-velocity clouds, candidate gas-rich minihalos around the Local Group, contain stars? This is a pre-registered search for resolved-star overdensities at the cloud positions in Euclid's DR1-Foundation release (12 November 2026), with known dwarf galaxies as positive controls and random null circles as negative controls.

Two arms:
- **v0.1.0, north:** the 59 ALFALFA ultra-compact HVCs (Adams, Giovanelli & Haynes 2013). Rules: [PREREGISTRATION.md](PREREGISTRATION.md). Coverage probes made after it was filed found no DR1 Wide data anywhere in the ALFALFA cloud sky, so it is expected to end NO_COVERAGE ([notes/coverage-probe-2026-11-25.md](notes/coverage-probe-2026-11-25.md)).
- **v0.2.0, south:** the 179 HIPASS compact HVCs (Putman et al. 2002), many inside DR1's southern region. Rules: [AMENDMENT-2026-11-25-south.md](AMENDMENT-2026-11-25-south.md) (frozen before any star counts at these positions were fetched).

Code: `uchvc.py` (statistics), `io_euclid.py` (IRSA TAP, stdlib only), `job.py` (north run), `chvc_south.py` + `job_chvc.py` (south run: `python job_chvc.py --out-dir out`), `test_uchvc.py` and `test_chvc.py` (offline tests: `python -m unittest -v`).

Data: Euclid DR1 MER catalogue (Wide Survey) through the NASA/IPAC Infrared Science Archive; north targets transcribed from arXiv:1303.6967 Table 1 (gate G0); south targets read by the job from VizieR J/AJ/123/873.

Status: both arms pre-registered; results will be added under `results/` with GRADING files.

Credit: cloud catalogues by Adams, Giovanelli & Haynes (2013, ApJ 768, 77) and Putman et al. (2002, AJ 123, 873). Earlier counterpart searches: Simon & Blitz 2002; Willman et al. 2002; Hopp et al. 2003, 2007; Siegel et al. 2005; Bellazzini et al. 2015 (SECCO); Sand et al. 2015; Janesh et al. 2015. Euclid DR1: Euclid Collaboration (arXiv:2611.16510; survey description arXiv:2611.17040).

Made by MV2, Munim, Inc. (mv2@munimtech.com), with AI agents working in his name; no human expert has checked it yet. Code Apache-2.0; text and results CC BY 4.0.
