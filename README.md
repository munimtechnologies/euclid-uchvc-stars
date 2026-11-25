# euclid-uchvc-stars

Do the ALFALFA ultra-compact high-velocity clouds (Adams, Giovanelli & Haynes 2013), candidate gas-rich minihalos around the Local Group, contain stars? This is a pre-registered search for resolved-star overdensities at all 59 cloud positions in Euclid's DR1-Foundation release (12 November 2026), with known dwarf galaxies as positive controls and random null circles as negative controls.

- Rules: [PREREGISTRATION.md](PREREGISTRATION.md) (frozen 2026-11-25, before any Euclid data was fetched)
- Prior work and scoop check: [notes/scoop-check-2026-11-25.md](notes/scoop-check-2026-11-25.md)
- Code: `uchvc.py` (statistics), `io_euclid.py` (IRSA TAP, stdlib only), `job.py` (run: `python job.py --out-dir out`), `test_uchvc.py` (offline tests: `python -m unittest -v`)
- Data: Euclid DR1 MER catalogue (Wide Survey) through the NASA/IPAC Infrared Science Archive; target table transcribed from arXiv:1303.6967 Table 1 and checked against the galactic coordinates in each cloud's name (gate G0).

Status: v0.1.0 pre-registered; results will be added under `results/` with a GRADING file.

Credit: the cloud catalogue is Adams, Giovanelli & Haynes (2013, ApJ 768, 77). Earlier counterpart searches: Bellazzini et al. 2015 (SECCO), Sand et al. 2015, Janesh et al. 2015. Euclid DR1: Euclid Collaboration (arXiv:2611.16510).

Made by MV2, Munim, Inc. (mv2@munimtech.com), with AI agents working in his name; no human expert has checked it yet. Code Apache-2.0; text and results CC BY 4.0.
