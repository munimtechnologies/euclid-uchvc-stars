# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""euclid-uchvc-stars southern arm (v0.2.0): resolved-star search at the 179 HIPASS
compact high-velocity clouds (Putman et al. 2002) in Euclid DR1.

Per-object processing is job.process from v0.1.0, unchanged. Rules:
AMENDMENT-2026-11-25-south.md.

Usage: python job_chvc.py --out-dir /out
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uchvc as U  # noqa: E402
import io_euclid as E  # noqa: E402
import job as J  # noqa: E402  (v0.1.0 job; its main() is not run)
import chvc_south as S  # noqa: E402

T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:8.1f}s] {msg}", flush=True)


def fetch_catalogue(out):
    last = None
    for host in S.VIZIER_HOSTS:
        url = host + S.VIZIER_QUERY
        try:
            req = urllib.request.Request(url, headers={"User-Agent": E.UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                txt = r.read().decode("utf-8", "replace")
            rows = S.parse_vizier_tsv(txt)
            log(f"VizieR {host}: {len(rows)} rows")
            if rows:
                open(os.path.join(out, "putman2002_chvc_vizier.tsv"), "w").write(txt)
                return rows, host
        except Exception as e:
            last = e
            log(f"VizieR {host} failed: {e!r}")
    raise RuntimeError(f"all VizieR mirrors failed: {last!r}")


def load_controls():
    out = J.load_controls()
    with open(os.path.join(HERE, "controls_south.csv"), newline="") as f:
        for r in csv.DictReader(f):
            ra, dec = U.sexa_to_deg(r["ra"], r["dec"])
            out.append({"name": r["name"], "ra": ra, "dec": dec,
                        "dist_mpc": float(r["dist_mpc"]), "kind": "control"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args()
    out = a.out_dir
    os.makedirs(os.path.join(out, "sources"), exist_ok=True)
    res = {"version": "0.2.0-south", "table": E.TABLE,
           "n_trials_per_object": U.n_trials()}

    rows, host = fetch_catalogue(out)
    targets = S.rows_to_targets(rows)
    bad = S.g0_check(targets)
    res.update({"vizier_host": host, "n_catalogue_rows": len(rows),
                "n_targets": len(targets), "g0_bad_rows": bad})
    res["G0"] = S.catalogue_gate(len(targets), len(bad))
    log(f"catalogue: {len(targets)} CHVCs; G0 {res['G0']}; {len(bad)} rows off by > "
        f"{S.G0_TOL_DEG} deg: {bad}")
    if res["G0"] != "PASS":
        res["outcome"] = res["G0"]
        json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1, default=str)
        log(f"OUTCOME {res['outcome']}")
        return
    targets = [t for t in targets if t["name"] not in bad]
    controls = load_controls()
    res["n_controls"] = len(controls)

    try:
        cols, txt = E.schema(log=log)
    except Exception as e:
        log(f"TAP_SCHEMA failed: {e!r}")
        cols, txt = [], ""
    open(os.path.join(out, "schema.csv"), "w").write(txt)
    m, ok = E.map_columns(cols)
    res["column_map"], res["schema_ok"] = m, ok
    log(f"schema: {len(cols)} columns; map {m}; ok={ok}")
    if not ok:
        res["outcome"] = "SCHEMA_MISMATCH"
        json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1, default=str)
        log("OUTCOME SCHEMA_MISMATCH")
        return

    for obj in controls + targets:
        try:
            J.process(obj, m, out)
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
    res["n_error"] = sum(1 for o in controls + targets if str(o.get("status", "")).startswith("ERROR"))
    res["outcome"] = U.overall(True, len(cov_t), len(cov_c), [c["label"] for c in cov_c],
                               [t["label"] for t in cov_t])

    with open(os.path.join(out, "per_object.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "ra", "dec", "vlsr", "maj_deg", "sep_lmc_deg", "status",
                    "n_all_cone", "n_point", "n_kept", "cov_inner", "cov_ann", "minp",
                    "best_r", "best_window", "best_n", "best_bkg", "null_minp_min", "label"])
        for o in controls + targets:
            bt = min(o["trials"], key=lambda t: t["p"]) if o.get("trials") else {}
            w.writerow([o["kind"], o["name"], f"{o['ra']:.5f}", f"{o['dec']:.5f}",
                        o.get("vlsr", ""), o.get("maj_deg", ""),
                        "" if "sep_lmc_deg" not in o else f"{o['sep_lmc_deg']:.2f}",
                        o["status"], o.get("n_all_cone", ""), o.get("n_point", ""),
                        o.get("n_kept", ""), o.get("cov_inner", ""), o.get("cov_ann", ""),
                        o.get("minp", ""), bt.get("r_arcmin", ""), bt.get("window", ""),
                        bt.get("n", ""), "" if not bt else f"{bt['bkg']:.3f}",
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
