# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Offline tests for the southern (HIPASS CHVC) arm. No network."""
import json
import math
import os
import random
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uchvc as U  # noqa: E402
import io_euclid as E  # noqa: E402
import chvc_south as S  # noqa: E402
import job_chvc as JC  # noqa: E402

TSV = ("#\n# VizieR Astronomical Server\n#RESOURCE=yCat_51230873\n\n"
       "Name\tRAJ2000\tDEJ2000\tVLSR\tMajAxis\tMinAxis\tFlux\n"
       "\t\"h:m\"\t\"d:m\"\tkm/s\tdeg\tdeg\tJy.km/s\n"
       "-------------------\t-------\t------\t----\t---\t---\t-----\n"
       "CHVC 255.5-59.6+188\t02 56.6\t-44 15\t188\t0.4\t0.3\t37.4\n"
       "HVC 000.0-59.4-114\t22 36.5\t-39 42\t-114\t0.3\t0.2\t5.9\n"
       "CHVC 312.3-59.8+145\t00 17.2\t-56 44\t145\t0.1\t0.1\t3.5\n")


def synth_rows(n=179):
    rows = []
    for k in range(n):
        ra = (k * 2.0) % 360.0
        h = int(ra / 15.0)
        m = (ra / 15.0 - h) * 60.0
        d = 30 + (k % 40)
        ra_s, dec_s = f"{h:02d} {m:04.1f}", f"-{d:02d} 00"
        l, b = U.eq_to_gal(S.ra_hm_to_deg(ra_s), S.dec_dm_to_deg(dec_s))
        rows.append({"Name": f"CHVC {l:05.1f}{b:+05.1f}+100", "RAJ2000": ra_s,
                     "DEJ2000": dec_s, "VLSR": "100", "MajAxis": "0.2", "MinAxis": "0.1",
                     "Flux": "10.0"})
    return rows


class TestParsing(unittest.TestCase):
    def test_tsv(self):
        rows = S.parse_vizier_tsv(TSV)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["Name"], "CHVC 255.5-59.6+188")
        self.assertEqual(rows[2]["DEJ2000"], "-56 44")

    def test_coords(self):
        self.assertAlmostEqual(S.ra_hm_to_deg("02 56.6"), 44.15, places=9)
        self.assertAlmostEqual(S.dec_dm_to_deg("-44 15"), -44.25, places=9)
        self.assertAlmostEqual(S.dec_dm_to_deg("-00 30"), -0.5, places=9)
        self.assertAlmostEqual(S.dec_dm_to_deg("+01 06"), 1.1, places=9)
        self.assertAlmostEqual(S.ra_hm_to_deg("23 59 30"), 359.875, places=9)

    def test_names_and_targets(self):
        self.assertEqual(S.norm_name("CHVC 255.5-59.6+188"), "HVC255.5-59.6+188")
        self.assertEqual(U.parse_hvc_name(S.norm_name("CHVC 005.3-05.1-090")), (5.3, -5.1, -90.0))
        t = S.rows_to_targets(S.parse_vizier_tsv(TSV))
        self.assertEqual([x["name"] for x in t], ["CHVC 255.5-59.6+188", "CHVC 312.3-59.8+145"])
        self.assertTrue(all(x["sep_lmc_deg"] > 0 for x in t))


class TestGates(unittest.TestCase):
    def test_g0_roundtrip_and_failure(self):
        t = S.rows_to_targets(synth_rows())
        self.assertEqual(len(t), 179)
        self.assertEqual(S.g0_check(t), [])
        bad = S.rows_to_targets(synth_rows(3))
        l, b, v = U.parse_hvc_name(S.norm_name(bad[0]["name"]))
        bad[0]["name"] = f"CHVC {l:05.1f}{b + 1.0:+05.1f}+100"
        self.assertEqual(S.g0_check(bad), [bad[0]["name"]])

    def test_catalogue_gate(self):
        self.assertEqual(S.catalogue_gate(179, 0), "PASS")
        self.assertEqual(S.catalogue_gate(179, 17), "PASS")
        self.assertEqual(S.catalogue_gate(179, 18), "G0_FAILED")
        self.assertEqual(S.catalogue_gate(178, 0), "CATALOGUE_MISMATCH")

    def test_controls(self):
        c = JC.load_controls()
        self.assertEqual(len(c), 18)
        eri = [x for x in c if x["name"] == "Eridanus II"][0]
        self.assertAlmostEqual(eri["ra"], 56.08375, places=4)
        self.assertAlmostEqual(eri["dec"], -43.53389, places=4)


class TestEndToEnd(unittest.TestCase):
    """main() with a fake VizieR and a fake TAP: one covered target (uniform field) and one
    covered control (Eridanus II position, with 80 injected stars inside 1')."""

    def setUp(self):
        self._tap, self._fetch, self._argv = E.tap, JC.fetch_catalogue, sys.argv
        rows = synth_rows()
        t0 = S.rows_to_targets(rows)[0]
        self.covered = [(t0["ra"], t0["dec"], False), (56.08375, -43.533889, True)]
        cols = ["ra", "dec", "flux_vis_psf", "flux_h_templfit", "fluxerr_h_templfit",
                "point_like_flag", "spurious_flag"]

        def fake_tap(query, timeout=600, tries=3, log=print):
            if "TAP_SCHEMA" in query:
                return [{"column_name": c} for c in cols], "column_name\n" + "\n".join(cols)
            mm = re.search(r"CIRCLE\('ICRS', ([-\d.]+), ([-\d.]+),", query)
            ra0, dec0 = float(mm.group(1)), float(mm.group(2))
            hit = [c for c in self.covered
                   if abs(c[0] - ra0) < 1e-3 and abs(c[1] - dec0) < 1e-3]
            if "COUNT(*)" in query:
                return [{"n": "5000" if hit else "0"}], ""
            rng = random.Random(7 if hit and hit[0][2] else 11)
            out = []

            def add(x, y, ie):
                ra = (ra0 + x / 60.0 / math.cos(math.radians(dec0))) % 360.0
                out.append({"ra": f"{ra:.7f}", "dec": f"{dec0 + y / 60.0:.7f}",
                            "flux_vis_psf": f"{10 ** ((23.9 - ie) / 2.5):.6g}",
                            "flux_h_templfit": "", "fluxerr_h_templfit": "",
                            "point_like_flag": "1", "spurious_flag": "0"})
            for _ in range(3000):
                r = 20.0 * math.sqrt(rng.random())
                th = rng.uniform(0, 2 * math.pi)
                add(r * math.cos(th), r * math.sin(th), rng.uniform(21.5, 26.0))
            if hit and hit[0][2]:
                for _ in range(80):
                    r = math.sqrt(rng.random())
                    th = rng.uniform(0, 2 * math.pi)
                    add(r * math.cos(th), r * math.sin(th), rng.uniform(24.0, 24.9))
            return out, ""

        E.tap = fake_tap
        JC.fetch_catalogue = lambda out: (rows, "fake")

    def tearDown(self):
        E.tap, JC.fetch_catalogue, sys.argv = self._tap, self._fetch, self._argv

    def test_main(self):
        with tempfile.TemporaryDirectory() as d:
            sys.argv = ["job_chvc.py", "--out-dir", d]
            JC.main()
            res = json.load(open(os.path.join(d, "results.json")))
            self.assertEqual(res["G0"], "PASS")
            self.assertEqual(res["n_targets"], 179)
            self.assertEqual(res["n_covered_targets"], 1)
            self.assertEqual(res["n_covered_controls"], 1)
            eri = [c for c in res["controls"] if c["name"] == "Eridanus II"][0]
            self.assertEqual(eri["label"], "DETECTED")
            self.assertIn(res["outcome"], ("NO_COUNTERPART", "CANDIDATES"))
            self.assertEqual(res["n_error"], 0)
            self.assertTrue(os.path.exists(os.path.join(d, "per_object.csv")))
            self.assertTrue(os.path.exists(os.path.join(d, "trials.csv")))


if __name__ == "__main__":
    unittest.main()
