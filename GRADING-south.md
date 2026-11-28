# Grading, southern arm (v0.2.0): HIPASS compact high-velocity clouds in Euclid DR1

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human expert has checked it yet. Text CC BY 4.0.

Graded 2026-11-28 from the single run of job `euclid-chvc-south-v1` (finished 2026-11-27, exit codes 0/0), under the rules frozen in AMENDMENT-2026-11-25-south.md and PREREGISTRATION.md. The job's output is committed unchanged under `results/south-v0.2.0/`.

## Pre-registered outcome: NO_COUNTERPART (with one detected control)

| Gate / item | Result |
|---|---|
| Gate C (catalogue) | PASS: 179 CHVC rows read from VizieR J/AJ/123/873 (raw TSV kept) |
| Gate G0 (names vs coordinates) | PASS: 0 rows off by more than the tolerance |
| Schema | PASS (point_like_flag, flux_vis_psf, flux_h_templfit, spurious_flag) |
| Targets fully covered | **8** of 179 (10 partial, 159 outside DR1 Wide, 2 TAP time-outs) |
| Controls covered | 1 of 18: **Eridanus II DETECTED**, p = 4.1e-18 (20 sources against 1.19 expected within 2', IE 21.5-23.0) |
| Global threshold | 0.01 / (8 trials x 8 targets) = 1.5625e-4 |
| Lowest target p | 0.031 (CHVC 257.1-26.2+123: 22 against 14.1 within 4', IE 21.5-23.0), and 0.0029 at its own null circles, so not even locally unique |
| Labels | 8 x NO_COUNTERPART, 0 CANDIDATE, 0 EXCESS_NOT_UNIQUE |

The eight covered clouds are CHVC 242.1-26.3+237, 243.1-29.0+130, 256.1-29.0+247, 257.1-26.2+123, 258.2-23.9+359, 259.1-27.9+299, 267.8-53.9+270 and 274.2-48.5+281. Per-cloud counts, backgrounds and classical 95% upper limits on the excess are in `results/south-v0.2.0/trials.csv`. In the window IE 21.5-23.0, the 95% upper limit on the excess within 4' ranges from 2.3 to 17.3 sources. Eridanus II shows an excess of 26.3 there.

## What the result is worth: the effective depth is IE of about 22.5, not 26.5

We checked this after grading, and it changes how the result should be read. The frozen star selection is `point_like_flag = 1`. The DR1 MER paper (Kümmel et al. 2026, arXiv:2611.17832) defines it as point_like_prob > 0.96, a cut tuned for 99% star purity and known to have low completeness at faint magnitudes. In the fetched cones, **66 of about 16,000 selected sources (0.4%) are fainter than IE 22.5**. Almost every trial in the windows starting at 22.5, 23.5 and 24.5 therefore has zero counts and zero background, at the targets and at the control alike (trials.csv). In practice the test only probed IE 21.5-23.0, the bright red-giant branch. The faint windows were designed to reach horizontal-branch and sub-giant stars, but the classifier removes those stars.

So, honestly:
- The pre-registered verdict stands: none of the eight covered clouds shows a resolved-star excess, and a dwarf as luminous as Eridanus II (about 370 kpc away) would have been detected at each of them.
- The limits are **not** deeper than existing ground-based coverage. DES reaches about r = 24 over the same sky, and blind DES dwarf-galaxy searches have covered these positions. We do not claim the first deep space-based limits that the amendment anticipated.
- Most covered clouds lie 16-34 degrees from the LMC with v_LSR between +123 and +359 km/s. Many are probably Magellanic-system gas (Leading Arm region), not isolated minihalos, and the test cannot tell the two apart.

## Decision
- No article. The result is a correct pre-registered negative, but too shallow to interest a researcher in the field beyond what DES already shows.
- A deeper redo would need a different star selection, for example point_like_prob with a lower threshold, or MU_MAX - MAG_AUTO with a PHZ star class. That would be a new pre-registration, chosen after seeing this run's depth problem, and must be labelled as such. We are not pursuing it now: the minihalo reading of CHVCs is already strongly disfavoured, and only 8 clouds are covered.
- The north arm (v0.1.0, job `euclid-uchvc-stars-v1`) is still expected to end NO_COVERAGE (see notes/coverage-probe-2026-11-25.md).

## Lesson recorded
Before freezing a resolved-star test on a survey catalogue, check the magnitude distribution of the exact star selection at one control field. A coverage probe alone is not enough.

## Credit
Cloud catalogue: Putman et al. 2002, AJ 123, 873. Earlier counterpart searches: Simon & Blitz 2002; Willman et al. 2002; Hopp et al. 2003, 2007; Siegel et al. 2005. Euclid DR1: Euclid Collaboration (arXiv:2611.16510; survey arXiv:2611.17040; MER processing arXiv:2611.17832).
