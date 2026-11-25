# Pre-registration: euclid-uchvc-stars v0.1.0 (frozen 2026-11-25, before any Euclid data was fetched)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert has checked it yet. Licence: Apache-2.0 (code), CC BY 4.0 (text and results).

## 1. The question and why it is open
Adams, Giovanelli & Haynes (2013, ApJ 768, 77; arXiv:1303.6967) listed 59 ultra-compact high-velocity clouds (UCHVCs) from ALFALFA and asked whether they are gas-rich minihalos in and around the Local Group, some with faint stars (one of their clouds became Leo P). Searches since then were ground-based: SECCO (Bellazzini et al. 2015, A&A 575, A126; LBT g, r to r~26.5 for 25 clouds) found no stellar counterpart within ~1.5 Mpc; Sand et al. (2015, ApJ 806, 95) found one distant dwarf (ALFALFA-Dw1 = HVC274.68+74.70-123); Janesh et al. (2015, ApJ 811, 35) reported a possible counterpart to AGC 198606. Sand et al. noted that if deeper searches keep finding no stars, the shortage could conflict with LCDM expectations. Euclid's DR1-Foundation (12 November 2026; arXiv:2611.16510) is the first space-based, wide, deep imaging with NIR colours over ~1,900 deg^2. Our searches (notes/scoop-check-2026-11-25.md) found no Euclid study of these clouds.

**The test:** for every UCHVC inside Euclid DR1 Wide, is there a resolved-star overdensity at the cloud position, and if not, how many stars could hide there?
**Wow, if it works:** a new gas-rich dwarf galaxy in or near the Local Group (a second Leo P), or the first space-based, colour-filtered "starless" limits for these minihalo candidates (RELHIC-type objects, cf. Cloud-9, Anand et al. 2025).

## 2. Data
- Targets: Table 1 of Adams et al. (2013), 59 rows, transcribed to `targets_uchvc.csv`.
- Positive controls: 16 known dwarfs at 0.4-1.9 Mpc (`controls_dwarfs.csv`); only those inside DR1 are used.
- Euclid DR1 MER catalogue, Wide Survey table `euclid_dr1_mer_catalogue_wide_survey`, via IRSA TAP (sync, CSV). Point-like sources (point_like_flag = 1, else point_like_prob > 0.5), spurious_flag = 0 if present, IE < 26.5 (AB, from the VIS PSF flux).

## 3. Rules (fixed)
- **G0 (transcription):** galactic (l, b) recomputed from each row's RA/Dec must match the (l, b) in the cloud's name within 0.1 deg (l scaled by cos b). Rows that fail are dropped and listed; more than 5 failing rows aborts (G0_FAILED).
- **Schema:** columns are found from TAP_SCHEMA by fixed candidate names (io_euclid.py). If RA, Dec, a VIS flux or a point-like column is missing: SCHEMA_MISMATCH; the schema is saved and only the I/O mapping may be fixed in a declared deviation.
- **Coverage:** 20' cone. 2'x2' cells; covered if >= 90% of cells within 4' and >= 80% of cells in the 8'-20' annulus hold a source. Otherwise NOT_IN_DR1 or PARTIAL_COVERAGE (no claims either way).
- **Colour rule:** a source is dropped only if HE is detected (S/N >= 3, or flux > 0 if no error column) and IE - HE is outside [-0.3, 1.3] (AB), which removes most foreground M dwarfs and red galaxies while keeping red giants.
- **Statistic:** counts in circles of radius 2' and 4' around the cloud position, in four IE windows [21.5, 23.0), [22.5, 24.0), [23.5, 25.0), [24.5, 26.0) (tip of the RGB at roughly 0.5 to 2.5 Mpc); 8 trials per object. Background = coverage-corrected density in the 8'-20' annulus. One-sided Poisson p per trial; object statistic = min p.
- **Null circles:** 40 seeded random centres 12'-16' from the cloud, the same 8 trials each.
- **Targets:** global threshold p_thr = 0.01 / (8 x N_covered_targets). CANDIDATE if min p < p_thr AND below every null circle's min p; EXCESS_NOT_UNIQUE if below p_thr but not below all nulls; else NO_COUNTERPART.
- **Controls:** DETECTED if min p < 0.01/8 and below every null circle; else MISSED.
- **Overall:** SCHEMA_MISMATCH / NO_COVERAGE / CONTROL_FAILED (controls covered, none detected: no claims) / CANDIDATES / NO_COUNTERPART; suffix _UNCALIBRATED if no control is covered.
- **Limits:** for every covered cloud, the 95% upper limit on excess stars per trial (trials.csv).

## 4. What follows each outcome
- CANDIDATES: eyeball every candidate (sources/<name>.csv spatial map and colour-magnitude diagram), check known galaxies/clusters at the position (NED, Legacy Surveys), and only then report; a confirmed one goes to needs_sheehan before any article.
- NO_COUNTERPART with a detected control: a negative result with per-cloud limits; a later amendment may convert limits to M_V by scaling a detected control's own star counts by distance.
- CONTROL_FAILED: the method is not sensitive enough at Euclid Wide depth; report that honestly.
- Not pre-registered and not to be claimed: anything found by changing radii, windows or the colour box after seeing data.
