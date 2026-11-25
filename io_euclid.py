# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""I/O for euclid-uchvc-stars: IRSA TAP (sync, CSV) with stdlib urllib only."""
import csv
import io
import time
import urllib.parse
import urllib.request

TAP_SYNC = "https://irsa.ipac.caltech.edu/TAP/sync"
TABLE = "euclid_dr1_mer_catalogue_wide_survey"
UA = "euclid-uchvc-stars/0.1 (research; github.com/munimtechnologies/euclid-uchvc-stars)"

CANDIDATES = {
    "ra": ["right_ascension", "ra"],
    "dec": ["declination", "dec"],
    "flux_vis": ["flux_vis_psf", "flux_vis_1fwhm_aper", "flux_vis_2fwhm_aper", "flux_detection_total"],
    "flux_h": ["flux_h_templfit", "flux_h_psf", "flux_h_1fwhm_aper", "flux_h_2fwhm_aper"],
    "fluxerr_h": ["fluxerr_h_templfit", "fluxerr_h_psf", "fluxerr_h_1fwhm_aper", "fluxerr_h_2fwhm_aper"],
    "point_flag": ["point_like_flag"],
    "point_prob": ["point_like_prob"],
    "spurious": ["spurious_flag"],
}
REQUIRED = ("ra", "dec", "flux_vis")


def tap(query, timeout=600, tries=3, log=print):
    data = urllib.parse.urlencode({"QUERY": query, "LANG": "ADQL", "REQUEST": "doQuery",
                                   "FORMAT": "csv"}).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(TAP_SYNC, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "replace")
            rows = [{(k or "").strip().lower(): v for k, v in r.items()}
                    for r in csv.DictReader(io.StringIO(txt))]
            return rows, txt
        except Exception as e:  # network or server error: retry
            last = e
            log(f"TAP attempt {i + 1} failed: {e!r}")
            time.sleep(10 * (i + 1))
    raise RuntimeError(f"TAP failed: {last!r}")


def schema(table=TABLE, log=print):
    rows, txt = tap("SELECT column_name, datatype, unit, description FROM TAP_SCHEMA.columns "
                    f"WHERE table_name = '{table}'", log=log)
    return [r.get("column_name", "").strip().lower() for r in rows], txt


def map_columns(cols):
    s = set(cols)
    m = {}
    for key, cands in CANDIDATES.items():
        for c in cands:
            if c in s:
                m[key] = c
                break
    ok = all(k in m for k in REQUIRED) and ("point_flag" in m or "point_prob" in m)
    return m, ok


def cone_query(m, ra, dec, r_deg, ie_faint, table=TABLE):
    flux_min = 10 ** ((23.9 - ie_faint) / 2.5)
    cols = [m[k] for k in ("ra", "dec", "flux_vis", "flux_h", "fluxerr_h", "point_flag",
                           "point_prob", "spurious") if k in m]
    where = [f"1 = CONTAINS(POINT('ICRS', {m['ra']}, {m['dec']}), "
             f"CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {r_deg:.6f}))",
             f"{m['flux_vis']} > {flux_min:.6g}"]
    if "point_flag" in m:
        where.append(f"{m['point_flag']} = 1")
    else:
        where.append(f"{m['point_prob']} > 0.5")
    if "spurious" in m:
        where.append(f"{m['spurious']} = 0")
    return f"SELECT {', '.join(cols)} FROM {table} WHERE " + " AND ".join(where)


def count_query(m, ra, dec, r_deg, table=TABLE):
    return (f"SELECT COUNT(*) AS n FROM {table} WHERE 1 = CONTAINS(POINT('ICRS', {m['ra']}, "
            f"{m['dec']}), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {r_deg:.6f}))")


def fnum(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v else None
