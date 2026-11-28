# euclid-uchvc-stars

Do compact high-velocity clouds, candidate gas-rich minihalos around the Local Group, contain stars? This is a pre-registered search for resolved-star overdensities at the cloud positions in Euclid's DR1-Foundation release (12 November 2026). Known dwarf galaxies serve as positive controls and random null circles as negative controls.

Two arms:
- **v0.1.0, north:** the 59 ALFALFA ultra-compact HVCs (Adams, Giovanelli & Haynes 2013). Rules: [PREREGISTRATION.md](PREREGISTRATION.md). Coverage probes made after it was filed found no DR1 Wide data anywhere in the ALFALFA cloud sky, so it is expected to end NO_COVERAGE ([notes/coverage-probe-2026-11-25.md](notes/coverage-probe-2026-11-25.md)).
- **v0.2.0, south:** the 179 HIPASS compact HVCs (Putman et al. 2002). Rules: [AMENDMENT-2026-11-25-south.md](AMENDMENT-2026-11-25-south.md), frozen before any star counts at these positions were fetched. **Graded 2026-11-28: NO_COUNTERPART** ([GRADING-south.md](GRADING-south.md), output in `results/south-v0.2.0/`). 8 clouds are fully covered and none shows a star excess; the Eridanus II control is detected (p = 4e-18). The frozen star selection (point_like_flag = 1) keeps almost nothing fainter than IE 22.5, so the limits reach only the bright red-giant branch and are not deeper than ground-based DES coverage. GRADING-south.md explains this in full.

Code: `uchvc.py` (statistics), `io_euclid.py` (IRSA TAP, stdlib only), `job.py` (north run), `chvc_south.py` + `job_chvc.py` (south run: `python job_chvc.py --out-dir out`), `test_uchvc.py` and `test_chvc.py` (offline tests: `python -m unittest -v`).

Data: the Euclid DR1 MER catalogue (Wide Survey), through the NASA/IPAC Infrared Science Archive. North targets were transcribed from arXiv:1303.6967 Table 1 (gate G0). South targets are read by the job from VizieR J/AJ/123/873.

Credit: cloud catalogues by Adams, Giovanelli & Haynes (2013, ApJ 768, 77) and Putman et al. (2002, AJ 123, 873). Earlier counterpart searches: Simon & Blitz 2002; Willman et al. 2002; Hopp et al. 2003, 2007; Siegel et al. 2005; Bellazzini et al. 2015 (SECCO); Sand et al. 2015; Janesh et al. 2015. Euclid DR1: Euclid Collaboration (arXiv:2611.16510; survey description arXiv:2611.17040; MER processing arXiv:2611.17832).

Made by MV2, Munim, Inc. (mv2@munimtech.com), with AI agents working in his name; no human expert has checked it yet. Code Apache-2.0; text and results CC BY 4.0.
