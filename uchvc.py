# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Pure functions for the euclid-uchvc-stars test (stdlib only).

Looks for resolved-star overdensities at the positions of the 59 ALFALFA
ultra-compact high-velocity clouds (Adams, Giovanelli & Haynes 2013, ApJ 768, 77)
in the Euclid DR1 MER catalogue. All rules are fixed in PREREGISTRATION.md.
"""
import math
import random

# ---- fixed analysis constants (PREREGISTRATION.md section 3) ----
R_CONE_ARCMIN = 20.0          # fetch radius
R_INNER_ARCMIN = (2.0, 4.0)   # search radii
ANN_IN_ARCMIN = 8.0           # background annulus
ANN_OUT_ARCMIN = 20.0
MAG_WINDOWS = (21.5, 22.5, 23.5, 24.5)   # IE (AB) window starts
MAG_WIDTH = 1.5
IE_FAINT_LIMIT = 26.5
COLOR_MIN, COLOR_MAX = -0.3, 1.3         # IE - HE (AB), applied only when HE is detected
HE_SNR_MIN = 3.0
CELL_ARCMIN = 2.0
COVER_INNER_MIN = 0.9
COVER_ANN_MIN = 0.8
N_NULL = 40
GLOBAL_ALPHA = 0.01
G0_TOL_DEG = 0.1


def n_trials():
    return len(R_INNER_ARCMIN) * len(MAG_WINDOWS)


# ---- coordinates ----
def hms_to_deg(s):
    """'hhmmss.s' -> degrees."""
    s = s.strip()
    h, m, sec = int(s[0:2]), int(s[2:4]), float(s[4:])
    return 15.0 * (h + m / 60.0 + sec / 3600.0)


def dms_to_deg(s):
    """'+ddmmss' or '-ddmmss(.s)' -> degrees."""
    s = s.strip()
    sign = -1.0 if s[0] == '-' else 1.0
    body = s[1:] if s[0] in '+-' else s
    d, m, sec = int(body[0:2]), int(body[2:4]), float(body[4:])
    return sign * (d + m / 60.0 + sec / 3600.0)


def sexa_to_deg(ra, dec):
    """'hh:mm:ss.s', '+dd:mm:ss' -> (ra_deg, dec_deg)."""
    h, m, s = [float(x) for x in ra.split(':')]
    dpart = dec.strip()
    sign = -1.0 if dpart.startswith('-') else 1.0
    d, dm, ds = [abs(float(x)) for x in dpart.lstrip('+-').split(':')]
    return 15.0 * (h + m / 60.0 + s / 3600.0), sign * (d + dm / 60.0 + ds / 3600.0)


# ICRS -> Galactic rotation matrix (Hipparcos / Perryman 1997 values)
_RG = ((-0.0548755604162154, -0.8734370902348850, -0.4838350155487132),
       (+0.4941094278755837, -0.4448296299600112, +0.7469822444972189),
       (-0.8676661490190047, -0.1980763734312015, +0.4559837761750669))


def eq_to_gal(ra_deg, dec_deg):
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    v = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
    g = [sum(_RG[i][j] * v[j] for j in range(3)) for i in range(3)]
    l = math.degrees(math.atan2(g[1], g[0])) % 360.0
    b = math.degrees(math.asin(max(-1.0, min(1.0, g[2]))))
    return l, b


def parse_hvc_name(name):
    """'HVC274.68+74.70-123' -> (274.68, 74.70, -123)."""
    s = name.strip()[3:]
    # split on the sign characters after the first number
    i = 1
    while s[i] not in '+-':
        i += 1
    l = float(s[:i])
    rest = s[i:]
    j = 1
    while rest[j] not in '+-':
        j += 1
    b = float(rest[:j])
    v = float(rest[j:])
    return l, b, v


def ang_diff_deg(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def sep_arcmin(ra1, dec1, ra2, dec2):
    """Great-circle separation (haversine), arcmin."""
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    h = math.sin((d2 - d1) / 2) ** 2 + math.cos(d1) * math.cos(d2) * math.sin((r2 - r1) / 2) ** 2
    return math.degrees(2 * math.asin(min(1.0, math.sqrt(h)))) * 60.0


def offset_xy_arcmin(ra0, dec0, ra, dec):
    """Gnomonic-ish small-field offsets (arcmin), x east."""
    dra = ((ra - ra0 + 180.0) % 360.0) - 180.0
    return dra * math.cos(math.radians(dec0)) * 60.0, (dec - dec0) * 60.0


# ---- photometry ----
def flux_to_ab(flux_ujy):
    if flux_ujy is None or not (flux_ujy > 0):
        return None
    return -2.5 * math.log10(flux_ujy) + 23.9


def keep_source(ie, he_flux, he_err):
    """Pre-registered colour rule: drop only if HE is detected (S/N >= 3, or flux > 0
    when no error is available) and IE-HE lies outside [COLOR_MIN, COLOR_MAX]."""
    if ie is None or ie > IE_FAINT_LIMIT:
        return False
    if he_flux is None or not (he_flux > 0):
        return True
    if he_err is not None and he_err > 0 and he_flux / he_err < HE_SNR_MIN:
        return True
    c = ie - flux_to_ab(he_flux)
    return COLOR_MIN <= c <= COLOR_MAX


def in_window(ie, k):
    lo = MAG_WINDOWS[k]
    return lo <= ie < lo + MAG_WIDTH


# ---- Poisson statistics ----
def _logpmf(k, mu):
    return -mu + k * math.log(mu) - math.lgamma(k + 1)


def poisson_cdf(n, mu):
    """P(N <= n | mu)."""
    if n < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    return min(1.0, sum(math.exp(_logpmf(k, mu)) for k in range(0, int(n) + 1)))


def poisson_sf(n, mu):
    """P(N >= n | mu)."""
    n = int(n)
    if n <= 0:
        return 1.0
    if mu <= 0:
        return 0.0
    if n <= mu:
        return max(0.0, 1.0 - poisson_cdf(n - 1, mu))
    tot, k = 0.0, n
    while True:
        t = math.exp(_logpmf(k, mu))
        tot += t
        if t < 1e-18 * max(tot, 1e-300) or k > n + 100000:
            break
        k += 1
    return min(1.0, tot)


def excess_upper95(n, bkg):
    """Smallest s >= 0 with P(N <= n | bkg + s) <= 0.05 (classical 95% upper limit)."""
    lo, hi = 0.0, float(n) + 10.0 * math.sqrt(n + 1.0) + 50.0
    if poisson_cdf(n, bkg) <= 0.05:
        return 0.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if poisson_cdf(n, bkg + mid) <= 0.05:
            hi = mid
        else:
            lo = mid
    return hi


# ---- coverage ----
def coverage_fractions(xy, r_inner, ann_in, ann_out, cell=CELL_ARCMIN):
    """Fraction of grid cells (centres inside each region) that hold >= 1 source."""
    occ = set()
    for x, y in xy:
        occ.add((math.floor(x / cell), math.floor(y / cell)))
    n_in = o_in = n_an = o_an = 0
    m = int(math.ceil(ann_out / cell)) + 1
    for i in range(-m, m):
        for j in range(-m, m):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            r = math.hypot(cx, cy)
            if r <= r_inner:
                n_in += 1
                o_in += (i, j) in occ
            elif ann_in <= r <= ann_out:
                n_an += 1
                o_an += (i, j) in occ
    f_in = o_in / n_in if n_in else 0.0
    f_an = o_an / n_an if n_an else 0.0
    return f_in, f_an


# ---- the statistic ----
def circle_counts(xy_mag, cx, cy, r):
    """Counts per magnitude window inside circle (cx, cy, r). xy_mag: list of (x, y, ie)."""
    c = [0] * len(MAG_WINDOWS)
    r2 = r * r
    for x, y, ie in xy_mag:
        if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
            for k in range(len(MAG_WINDOWS)):
                if in_window(ie, k):
                    c[k] += 1
    return c


def annulus_density(xy_mag, cov_ann):
    """Per-window source density (arcmin^-2) in the background annulus, coverage-corrected."""
    area = math.pi * (ANN_OUT_ARCMIN ** 2 - ANN_IN_ARCMIN ** 2) * max(cov_ann, 1e-9)
    c = [0] * len(MAG_WINDOWS)
    for x, y, ie in xy_mag:
        r = math.hypot(x, y)
        if ANN_IN_ARCMIN <= r <= ANN_OUT_ARCMIN:
            for k in range(len(MAG_WINDOWS)):
                if in_window(ie, k):
                    c[k] += 1
    return [ck / area for ck in c], c


def trials_at(xy_mag, cx, cy, dens):
    """All (radius, window) trials at one centre: list of dicts."""
    out = []
    for r in R_INNER_ARCMIN:
        cnt = circle_counts(xy_mag, cx, cy, r)
        area = math.pi * r * r
        for k in range(len(MAG_WINDOWS)):
            bkg = dens[k] * area
            out.append({"r_arcmin": r, "window": MAG_WINDOWS[k], "n": cnt[k],
                        "bkg": bkg, "p": poisson_sf(cnt[k], bkg),
                        "excess": cnt[k] - bkg,
                        "excess_ul95": excess_upper95(cnt[k], bkg)})
    return out


def null_centres(seed, n=N_NULL, rmin=None, rmax=None):
    """Deterministic random centres inside the annulus such that a 4' circle stays inside it."""
    rmin = ANN_IN_ARCMIN + max(R_INNER_ARCMIN) if rmin is None else rmin
    rmax = ANN_OUT_ARCMIN - max(R_INNER_ARCMIN) if rmax is None else rmax
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        rr = math.sqrt(rng.uniform(rmin ** 2, rmax ** 2))
        th = rng.uniform(0.0, 2.0 * math.pi)
        out.append((rr * math.cos(th), rr * math.sin(th)))
    return out


def min_p(trials):
    return min(t["p"] for t in trials) if trials else 1.0


def classify_target(target_minp, null_minps, p_thr):
    """CANDIDATE only if the target beats the global threshold AND every null circle."""
    beats_nulls = all(target_minp < q for q in null_minps)
    if target_minp < p_thr and beats_nulls:
        return "CANDIDATE"
    if target_minp < p_thr:
        return "EXCESS_NOT_UNIQUE"
    return "NO_COUNTERPART"


def classify_control(target_minp, null_minps):
    """Positive control passes at the per-object threshold GLOBAL_ALPHA / n_trials."""
    return "DETECTED" if (target_minp < GLOBAL_ALPHA / n_trials()
                          and all(target_minp < q for q in null_minps)) else "MISSED"


def overall(schema_ok, n_cov_targets, n_cov_controls, control_labels, target_labels):
    if not schema_ok:
        return "SCHEMA_MISMATCH"
    if n_cov_targets == 0:
        return "NO_COVERAGE"
    if n_cov_controls > 0 and "DETECTED" not in control_labels:
        return "CONTROL_FAILED"
    base = "CANDIDATES" if "CANDIDATE" in target_labels else "NO_COUNTERPART"
    if n_cov_controls == 0:
        base += "_UNCALIBRATED"
    return base
