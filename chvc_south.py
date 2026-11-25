# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Southern arm of euclid-uchvc-stars: the 179 HIPASS compact high-velocity clouds
(Putman et al. 2002, AJ 123, 873; VizieR J/AJ/123/873/table1, names starting 'CHVC').

Pure functions (stdlib only). Rules are fixed in AMENDMENT-2026-11-25-south.md.
The star statistic itself is uchvc.py, unchanged.
"""
import math

import uchvc as U

EXPECTED_N = 179          # Putman et al. (2002) report 179 CHVCs
G0_TOL_DEG = 0.15         # name (l, b) vs catalogue RA/Dec; names and coords are rounded
G0_MAX_BAD_FRAC = 0.10    # more failing rows than this aborts (G0_FAILED)
LMC_RA, LMC_DEC = 80.894, -69.756   # LMC centre (reported column only, no inference)

VIZIER_QUERY = ("/viz-bin/asu-tsv?-source=J/AJ/123/873/table1&Name=CHVC*&-out.max=1000"
                "&-out=Name,RAJ2000,DEJ2000,VLSR,MajAxis,MinAxis,Flux")
VIZIER_HOSTS = ("https://vizier.cfa.harvard.edu", "https://vizier.cds.unistra.fr",
                "https://vizier.u-strasbg.fr", "https://vizier.nao.ac.jp")


def parse_vizier_tsv(text):
    """VizieR asu-tsv -> list of dicts. Skips '#' comments and blank lines; the first
    remaining line is the header; data start after the first all-dashes line."""
    lines = [ln.rstrip("\r\n") for ln in text.splitlines()]
    lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    if not lines:
        return []
    header = [h.strip() for h in lines[0].split("\t")]
    start = None
    for i, ln in enumerate(lines[1:], start=1):
        if ln.replace("\t", "").replace(" ", "") and set(ln.replace("\t", "").replace(" ", "")) == {"-"}:
            start = i + 1
            break
    if start is None:
        start = 2  # header + units line
    rows = []
    for ln in lines[start:]:
        parts = ln.split("\t")
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        rows.append({header[k]: parts[k].strip() for k in range(len(header))})
    return rows


def ra_hm_to_deg(s):
    """'02 56.6' (h, decimal min) or '02 56 36' (h m s) -> degrees."""
    p = s.split()
    h, m = int(p[0]), float(p[1])
    sec = float(p[2]) if len(p) > 2 else 0.0
    return 15.0 * (h + m / 60.0 + sec / 3600.0)


def dec_dm_to_deg(s):
    """'-44 15' (d, min) or '-44 15 30' -> degrees; the sign is read from the string,
    so '-00 30' is -0.5."""
    t = s.strip()
    sign = -1.0 if t.startswith("-") else 1.0
    p = t.lstrip("+-").split()
    d, m = abs(int(p[0])), float(p[1])
    sec = float(p[2]) if len(p) > 2 else 0.0
    return sign * (d + m / 60.0 + sec / 3600.0)


def norm_name(name):
    """'CHVC 255.5-59.6+188' -> 'HVC255.5-59.6+188' (the form uchvc.parse_hvc_name reads)."""
    s = name.replace(" ", "")
    if s.upper().startswith("CHVC"):
        s = s[1:]
    return s


def rows_to_targets(rows):
    out = []
    for r in rows:
        name = r.get("Name", "")
        if not name.replace(" ", "").upper().startswith("CHVC"):
            continue
        ra, dec = ra_hm_to_deg(r["RAJ2000"]), dec_dm_to_deg(r["DEJ2000"])
        out.append({"name": name.strip(), "ra": ra, "dec": dec,
                    "vlsr": r.get("VLSR", ""), "maj_deg": r.get("MajAxis", ""),
                    "flux": r.get("Flux", ""),
                    "sep_lmc_deg": U.sep_arcmin(ra, dec, LMC_RA, LMC_DEC) / 60.0,
                    "kind": "target"})
    return out


def g0_check(targets, tol=G0_TOL_DEG):
    """Recompute (l, b) from RA/Dec and compare with the (l, b) in each name.
    Returns the list of failing names; sets l, b, g0_dl, g0_db on each target."""
    bad = []
    for t in targets:
        l, b = U.eq_to_gal(t["ra"], t["dec"])
        ln, bn, _ = U.parse_hvc_name(norm_name(t["name"]))
        t["l"], t["b"] = l, b
        dl, db = U.ang_diff_deg(l, ln), abs(b - bn)
        t["g0_dl"], t["g0_db"] = dl, db
        if dl * max(0.05, abs(math.cos(math.radians(b)))) > tol or db > tol:
            bad.append(t["name"])
    return bad


def catalogue_gate(n_rows, n_bad):
    """CATALOGUE_MISMATCH if the row count is not the published 179; G0_FAILED if more
    than 10% of rows fail the name/coordinate check; else PASS."""
    if n_rows != EXPECTED_N:
        return "CATALOGUE_MISMATCH"
    if n_bad > G0_MAX_BAD_FRAC * n_rows:
        return "G0_FAILED"
    return "PASS"
