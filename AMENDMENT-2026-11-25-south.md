# Amendment 2026-11-25 (south): the HIPASS compact high-velocity clouds (v0.2.0)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert has checked it yet. Licence: Apache-2.0 (code), CC BY 4.0 (text).

Frozen 2026-11-25 (~18:30 UTC), before any Euclid source list or star count at a CHVC position was fetched. The v0.1.0 rules (PREREGISTRATION.md) and the queued v0.1.0 job are unchanged; this adds a second, separate arm.

## 1. Why a southern arm
After v0.1.0 was filed, we probed the DR1 Wide catalogue (IRSA table `euclid_dr1_mer_catalogue_wide_survey`) at six positions spread over the ALFALFA cloud sky (RA 0.5h-22h, Dec +8 to +31). Every probe returned **zero sources** in a 1-degree circle, while a control position at RA 70, Dec -50 returned 131 sources in a 0.6' circle (notes/coverage-probe-2026-11-25.md). The DR1 survey paper (Tereno et al., arXiv:2611.17040) explains why: DR1 was built outward from the ecliptic poles, with a 561 deg^2 northern mainland and a 1,539 deg^2 southern mainland inside the DES footprint. The ALFALFA UCHVCs are at low and middle ecliptic latitudes, so **v0.1.0 is expected to end as NO_COVERAGE**. That is a design error on our side (we did not check the footprint before freezing), and we say so here instead of editing v0.1.0.

The HIPASS survey (Dec < +2) covers the southern DR1 region. Putman et al. (2002, AJ 123, 873) list **179 compact high-velocity clouds (CHVCs)**, the southern counterparts of the minihalo candidates that Blitz et al. (1999) and Braun & Burton (1999) proposed and that ground-based searches (Simon & Blitz 2002; Willman et al. 2002; Hopp et al. 2003, 2007; Siegel et al. 2005) found starless in small fields or at shallow depth. Euclid DR1 is the first deep space-based imaging over many of them.

## 2. Data
- **Targets:** every row of VizieR `J/AJ/123/873/table1` whose name starts with "CHVC" (fetched by the job from the VizieR mirrors in `chvc_south.py`, raw TSV saved). No hand transcription.
- **Controls:** the 16 dwarfs of v0.1.0 (controls_dwarfs.csv, unchanged) plus two southern dwarfs, Eridanus II (0.37 Mpc) and IC 5152 (1.97 Mpc) (controls_south.csv). Only controls inside DR1 count.
- **Coverage probes made before freezing (disclosed):** total-source counts (all sources, no magnitude, colour or point-like cut) in 0.6' circles at four CHVC positions: 149, 145, 107 and 0. No point-source list, magnitude or star count at any CHVC position was looked at.

## 3. Rules (fixed)
- **Gate C (catalogue):** exactly 179 CHVC rows, else CATALOGUE_MISMATCH (no claims; the raw TSV is kept).
- **Gate G0 (names vs coordinates):** galactic (l, b) recomputed from the catalogue RA/Dec must match the (l, b) in the name within 0.15 deg (l scaled by cos b; catalogue RA is rounded to 0.1 min and Dec to 1', names to 0.1 deg). Failing rows are dropped and listed; more than 10% failing aborts (G0_FAILED).
- **Everything else is v0.1.0, unchanged:** the same schema rule, 20' cone, coverage rule, colour rule, IE windows, 2' and 4' circles, 8 trials per object, 40 seeded null circles, global threshold 0.01 / (8 x N_covered_targets), the same CANDIDATE / EXCESS_NOT_UNIQUE / NO_COUNTERPART labels, control rule and overall outcomes (uchvc.py and job.process are imported unchanged).
- **Reported, not used for inference:** each cloud's angular distance from the LMC centre (sep_lmc_deg), because many southern CHVCs with high positive velocities may belong to the Magellanic system.

## 4. What follows each outcome
- CANDIDATES: eyeball every candidate (sources/<name>.csv map and colour-magnitude diagram), check known galaxies, clusters and the LMC/SMC outskirts at the position (NED, Legacy Surveys DR10), then needs_sheehan before any article. A confirmed one would be a new gas-rich dwarf galaxy around the Local Group.
- NO_COUNTERPART with a detected control: a negative result with per-cloud limits, the first space-based limits for these clouds.
- CONTROL_FAILED, NO_COVERAGE, CATALOGUE_MISMATCH or G0_FAILED: an honest note in a GRADING file; no article.
- Not pre-registered and not to be claimed: anything found by changing radii, windows, the colour box or the target list after seeing data.
