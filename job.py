# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""euclid-uchvc-stars v0.1.0 job: resolved-star search at the 59 ALFALFA UCHVCs in Euclid DR1.

Usage: python job.py --out-dir /out
"""
import argparse
import csv
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uchvc as U  # noqa: E402
import io_euclid as E  # noqa: E402

T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:8.1f}s] {msg}", flush=True)


def load_targets():
    out = []
    with open(os.path.join(HERE, "targets_uchvc.csv"), newline="") as f:
        for r in csv.DictReader(f):
            ra, dec = U.hms_to_deg(r["RA_J2000"]), U.dms_to_deg(r["Dec_J2000"])
            out.append({"name": r["Name"], "agc": r["AGC"], "ra": ra, "dec": dec,
                        "a_arcmin": float(r["a_arcmin"]), "mis": r["MIS"].strip() == "Y",
                        "kind": "target"})
    return out


def load_controls():
    out = []
    with open(os.path.join(HERE, "controls_dwarfs.csv"), newline="") as f:
        for r in csv.DictReader(f):
            ra, dec = U.sexa_to_deg(r["ra"], r["dec"])
            out.append({"name": r["name"], "ra": ra, "dec": dec,
                        "dist_mpc": float(r["dist_mpc"]), "kind": "control"})
    return out


def gate_g0(targets):
    bad = []
    for t in targets:
        l, b = U.eq_to_gal(t["ra"], t["dec"])
        ln, bn, _ = U.parse_hvc_name(t["name"])
        t["l"], t["b"] = l, b
        dl, db = U.ang_diff_deg(l, ln), abs(b - bn)
        t["g0_dl"], t["g0_db"] = dl, db
        if dl * max(0.05, abs(math.cos(math.radians(b)))) > U.G0_TOL_DEG or db > U.G0_TOL_DEG:
            bad.append(t["name"])
    return bad


def process(obj, m, outdir):
    rdeg = U.R_CONE_ARCMIN / 60.0
    rows, _ = E.tap(E.count_query(m, obj["ra"], obj["dec"], rdeg), log=log)
    n_all = int(float(list(rows[0].values())[0] or 0)) if rows else 0
    obj["n_all_cone"] = n_all
    if n_all == 0:
        obj["covered"] = False
        obj["status"] = "NOT_IN_DR1"
        return
    rows, txt = E.tap(E.cone_query(m, obj["ra"], obj["dec"], rdeg, U.IE_FAINT_LIMIT), log=log)
    xy_all, xym = [], []
    safe = "".join(ch if ch.isalnum() else "_" for ch in obj["name"])
    with open(os.path.join(outdir, "sources", f"{safe}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ra", "dec", "x_arcmin", "y_arcmin", "ie", "he", "kept"])
        for r in rows:
            ra, dec = E.fnum(r.get(m["ra"])), E.fnum(r.get(m["dec"]))
            if ra is None or dec is None:
                continue
            x, y = U.offset_xy_arcmin(obj["ra"], obj["dec"], ra, dec)
            ie = U.flux_to_ab(E.fnum(r.get(m["flux_vis"])))
            hf = E.fnum(r.get(m["flux_h"])) if "flux_h" in m else None
            he_err = E.fnum(r.get(m["fluxerr_h"])) if "fluxerr_h" in m else None
            he = U.flux_to_ab(hf)
            keep = U.keep_source(ie, hf, he_err)
            xy_all.append((x, y))
            if keep:
                xym.append((x, y, ie))
            w.writerow([f"{ra:.6f}", f"{dec:.6f}", f"{x:.3f}", f"{y:.3f}",
                        "" if ie is None else f"{ie:.3f}", "" if he is None else f"{he:.3f}",
                        int(keep)])
    f_in, f_an = U.coverage_fractions(xy_all, max(U.R_INNER_ARCMIN), U.ANN_IN_ARCMIN,
                                      U.ANN_OUT_ARCMIN)
    obj.update({"n_point": len(xy_all), "n_kept": len(xym), "cov_inner": f_in, "cov_ann": f_an})
    obj["covered"] = f_in >= U.COVER_INNER_MIN and f_an >= U.COVER_ANN_MIN
    if not obj["covered"]:
        obj["status"] = "PARTIAL_COVERAGE"
        return
    dens, ann_counts = U.annulus_density(xym, f_an)
    obj["ann_counts"] = ann_counts
    obj["trials"] = U.trials_at(xym, 0.0, 0.0, dens)
    obj["minp"] = U.min_p(obj["trials"])
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(obj["name"]))
    nulls = U.null_centres(seed)
    obj["null_minps"] = [U.min_p(U.trials_at(xym, cx, cy, dens)) for cx, cy in nulls]
    obj["status"] = "COVERED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args()
    out = a.out_dir
    os.makedirs(os.path.join(out, "sources"), exist_ok=True)
    targets, controls = load_targets(), load_controls()
    res = {"version": "0.1.0", "table": E.TABLE, "n_targets": len(targets),
           "n_controls": len(controls), "n_trials_per_object": U.n_trials()}

    bad = gate_g0(targets)
    res["g0_bad_rows"] = bad
    res["G0"] = "PASS" if len(bad) <= 5 else "FAIL"
    log(f"G0 name/coordinate check: {len(bad)} rows off by > {U.G0_TOL_DEG} deg: {bad}")
    if res["G0"] == "FAIL":
        res["outcome"] = "G0_FAILED"
        json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)
        log("OUTCOME G0_FAILED")
        return
    targets = [t for t in targets if t["name"] not in bad]

    try:
        cols, txt = E.schema(log=log)
    except Exception as e:
        log(f"TAP_SCHEMA failed: {e!r}")
        cols, txt = [], ""
    if not [c for c in cols if c]:  # fall back to a one-row query
        log("TAP_SCHEMA gave no columns; trying TOP 1")
        rows, txt = E.tap(f"SELECT TOP 1 * FROM {E.TABLE}", log=log)
        cols = [c.strip().lower() for c in (rows[0].keys() if rows else [])]
    open(os.path.join(out, "schema.csv"), "w").write(txt)
    m, ok = E.map_columns(cols)
    res["column_map"], res["schema_ok"] = m, ok
    log(f"schema: {len(cols)} columns; map {m}; ok={ok}")
    if not ok:
        res["outcome"] = "SCHEMA_MISMATCH"
        json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)
        log("OUTCOME SCHEMA_MISMATCH")
        return

    for obj in controls + targets:
        try:
            process(obj, m, out)
        except Exception as e:
            obj["covered"], obj["status"] = False, f"ERROR {e!r}"[:200]
        log(f"{obj['kind']} {obj['name']}: {obj['status']} n_all={obj.get('n_all_cone')} "
            f"n_point={obj.get('n_point')} cov={obj.get('cov_inner')},{obj.get('cov_ann')} "
            f"minp={obj.get('minp')}")

    cov_t = [t for t in targets if t.get("covered")]
    cov_c = [c for c in controls if c.get("covered")]
    p_thr = U.GLOBAL_ALPHA / (U.n_trials() * max(1, len(cov_t)))
    for t in cov_t:
        t["label"] = U.classify_target(t["minp"], t["null_minps"], p_thr)
    for c in cov_c:
        c["label"] = U.classify_control(c["minp"], c["null_minps"])
    res["p_threshold_global"] = p_thr
    res["n_covered_targets"], res["n_covered_controls"] = len(cov_t), len(cov_c)
    res["outcome"] = U.overall(True, len(cov_t), len(cov_c), [c["label"] for c in cov_c],
                               [t["label"] for t in cov_t])

    with open(os.path.join(out, "per_object.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "ra", "dec", "status", "n_all_cone", "n_point", "n_kept",
                    "cov_inner", "cov_ann", "minp", "best_r", "best_window", "best_n", "best_bkg",
                    "null_minp_min", "label"])
        for o in controls + targets:
            bt = min(o["trials"], key=lambda t: t["p"]) if o.get("trials") else {}
            w.writerow([o["kind"], o["name"], f"{o['ra']:.5f}", f"{o['dec']:.5f}", o["status"],
                        o.get("n_all_cone", ""), o.get("n_point", ""), o.get("n_kept", ""),
                        o.get("cov_inner", ""), o.get("cov_ann", ""), o.get("minp", ""),
                        bt.get("r_arcmin", ""), bt.get("window", ""), bt.get("n", ""),
                        "" if not bt else f"{bt['bkg']:.3f}",
                        min(o["null_minps"]) if o.get("null_minps") else "", o.get("label", "")])
    with open(os.path.join(out, "trials.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "r_arcmin", "ie_window_start", "n", "bkg", "excess",
                    "excess_ul95", "p"])
        for o in controls + targets:
            for t in o.get("trials", []):
                w.writerow([o["kind"], o["name"], t["r_arcmin"], t["window"], t["n"],
                            f"{t['bkg']:.4f}", f"{t['excess']:.3f}", f"{t['excess_ul95']:.3f}",
                            f"{t['p']:.4g}"])
    res["targets"] = [{k: v for k, v in t.items() if k not in ("trials", "null_minps")}
                      for t in targets]
    res["controls"] = [{k: v for k, v in c.items() if k not in ("trials", "null_minps")}
                       for c in controls]
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1, default=str)
    labels = {}
    for t in cov_t:
        labels[t["label"]] = labels.get(t["label"], 0) + 1
    log(f"covered targets {len(cov_t)}, covered controls {len(cov_c)} "
        f"({[(c['name'], c['label']) for c in cov_c]}), target labels {labels}")
    log(f"OUTCOME {res['outcome']}")


if __name__ == "__main__":
    main()
