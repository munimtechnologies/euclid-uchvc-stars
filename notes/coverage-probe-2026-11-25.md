# Euclid DR1 coverage probes, 2026-11-25 (~17:45-18:25 UTC)

All queries: IRSA TAP sync, `SELECT COUNT(*) AS n FROM euclid_dr1_mer_catalogue_wide_survey WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',RA,DEC,R))`. All sources, no cuts. (`right_ascension` is not a column; `ra`/`dec` are. io_euclid.py already falls back to them.)

## ALFALFA UCHVC sky (v0.1.0 targets)
| RA | Dec | R (deg) | n |
|---|---|---|---|
| 156.7546 | +8.7856 | 0.5 | 0 |
| 1.476 | +31.337 | 1.0 | 0 |
| 118.86 | +24.69 | 1.0 | 0 |
| 190.05 | +8.0 | 1.0 | 0 |
| 241.4 | +14.7 | 1.0 | 0 |
| 332.5 | +25.0 | 1.0 | 0 |
| 215.0 | +6.0 | 1.0 | 0 |

## Other positions
| Position | RA | Dec | R (deg) | n |
|---|---|---|---|---|
| South control | 70.0 | -50.0 | 0.01 | 131 |
| Eridanus II | 56.09 | -43.53 | 0.01 | 592 |
| Fornax cluster centre (NGC 1399 masked?) | 54.62 | -35.45 | 0.01 | 1 |
| ~1.2 deg E of Fornax dSph | 41.5 | -34.0 | 0.01 | 0 |
| North, RA 255 | 255.0 | +60.0 | 0.05 | 0 |
| North, RA 240 | 240.0 | +70.0 | 0.01 | 0 |
| WALLABY dark cloud C1 (Wong et al. 2021) | 54.796 | -22.389 | 0.02 | 0 |
| WALLABY dark cloud C2 | 54.346 | -23.963 | 0.02 | 0 |
| Hydra field | 158.78 | -28.58 | 0.02 | 0 |
| CHVC 264.7-55.7+184 | 46.075 | -50.417 | 0.01 | 149 |
| CHVC 260.4-35.0+139 | 79.875 | -53.017 | 0.01 | 145 |
| CHVC 255.5-59.6+188 | 44.15 | -44.25 | 0.01 | 107 |
| CHVC 312.3-59.8+145 | 4.3 | -56.733 | 0.01 | 0 |

Two queries (RA 39.997, Dec -34.449, R 0.3; RA 60, Dec -48, R 0.05) timed out after 60 s.

Conclusion: no DR1 Wide coverage was found anywhere in the ALFALFA cloud sky, so v0.1.0 should end NO_COVERAGE. The southern CHVCs near RA 3-5h, Dec -44 to -53 are covered. The DR1 survey paper (arXiv:2611.17040) gives 561 deg^2 north and 1,539 deg^2 south, built outward from the ecliptic poles.

## Scoop check for the southern arm (same day)
1. web: "Euclid compact high velocity clouds stellar counterpart search resolved stars minihalo HIPASS CHVC 2026": no Euclid study; only ground-based work (SECCO 2015; Janesh et al. 2015; Hopp et al. 2003, 2007; Simon & Blitz 2002, astro-ph/0204042).
2. web: "compact high-velocity clouds Putman 2002 stellar populations search deep imaging dwarf galaxy counterpart Siegel Hopp": Hopp et al. 2003 (VLT FORS, 5 clouds, I~24, 6.8' field) and 2007 (5 more); Willman et al. 2002; Siegel et al. 2005. No space-based or wide deep search.
3. web: "dark HI clouds without optical counterpart southern sky MeerKAT OR WALLABY OR ASKAP catalogue 2025 2026": WALLABY dark sources (O'Beirne et al. 2025, PASA 42, e087); not CHVCs and not in DR1 at the probed positions.
4. web: "arXiv 2026 Euclid Q1 OR Euclid DR1 predicted candidate confirmed dwarf galaxy dark HI cloud stellar counterpart": Euclid Q1 dwarf census, Fornax-7 (arXiv:2609.14535); none targets HI clouds.
Recheck right before publishing any result.
