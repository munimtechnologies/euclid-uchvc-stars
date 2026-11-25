# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Offline tests for euclid-uchvc-stars (stdlib only, no network)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uchvc as U  # noqa: E402
import io_euclid as E  # noqa: E402
import job  # noqa: E402


class Coords(unittest.TestCase):
    def test_hms_dms(self):
        self.assertAlmostEqual(U.hms_to_deg("122154.7"), 15 * (12 + 21 / 60 + 54.7 / 3600), 9)
        self.assertAlmostEqual(U.dms_to_deg("+132810"), 13 + 28 / 60 + 10 / 3600, 9)
        self.assertAlmostEqual(U.dms_to_deg("-385923"), -(38 + 59 / 60 + 23 / 3600), 9)
        ra, dec = U.sexa_to_deg("10:21:45.1", "+18:05:17")
        self.assertAlmostEqual(ra, 155.43792, 4)
        self.assertAlmostEqual(dec, 18.08806, 4)
        ra, dec = U.sexa_to_deg("01:51:06.3", "-44:26:41")
        self.assertAlmostEqual(dec, -44.44472, 4)

    def test_galactic_poles(self):
        l, b = U.eq_to_gal(192.85948, 27.12825)
        self.assertAlmostEqual(b, 90.0, 2)
        l, b = U.eq_to_gal(266.40500, -28.93617)
        self.assertLess(U.ang_diff_deg(l, 0.0), 0.01)
        self.assertLess(abs(b), 0.01)

    def test_parse_name(self):
        self.assertEqual(U.parse_hvc_name("HVC274.68+74.70-123"), (274.68, 74.70, -123.0))
        self.assertEqual(U.parse_hvc_name("HVC111.65-30.53-124"), (111.65, -30.53, -124.0))
        self.assertEqual(U.parse_hvc_name("HVC5.58+52.07+163"), (5.58, 52.07, 163.0))

    def test_g0_on_catalogue(self):
        t = job.load_targets()
        self.assertEqual(len(t), 59)
        bad = job.gate_g0(t)
        self.assertLessEqual(len(bad), 5, bad)

    def test_sep_and_offsets(self):
        self.assertAlmostEqual(U.sep_arcmin(10.0, 0.0, 10.0, 1.0), 60.0, 6)
        x, y = U.offset_xy_arcmin(10.0, 60.0, 10.1, 60.0)
        self.assertAlmostEqual(x, 0.1 * 0.5 * 60.0, 6)
        x, y = U.offset_xy_arcmin(359.95, 0.0, 0.05, 0.0)
        self.assertAlmostEqual(x, 6.0, 6)


class Photometry(unittest.TestCase):
    def test_ab(self):
        self.assertAlmostEqual(U.flux_to_ab(1.0), 23.9, 9)
        self.assertIsNone(U.flux_to_ab(0.0))
        self.assertIsNone(U.flux_to_ab(None))

    def test_keep(self):
        self.assertTrue(U.keep_source(25.0, None, None))
        self.assertFalse(U.keep_source(27.0, None, None))
        f21 = 10 ** ((23.9 - 21.0) / 2.5)
        f20 = 10 ** ((23.9 - 20.0) / 2.5)
        self.assertTrue(U.keep_source(22.0, f21, None))      # colour 1.0
        self.assertFalse(U.keep_source(22.0, f20, None))     # colour 2.0
        self.assertTrue(U.keep_source(22.0, f20, 100.0))     # HE not detected (S/N < 3)

    def test_windows(self):
        self.assertTrue(U.in_window(22.0, 0))
        self.assertFalse(U.in_window(22.0, 1))
        self.assertTrue(U.in_window(23.0, 1))
        self.assertFalse(U.in_window(23.0, 0))


class Poisson(unittest.TestCase):
    def test_values(self):
        self.assertEqual(U.poisson_sf(0, 3.0), 1.0)
        self.assertAlmostEqual(U.poisson_sf(1, 2.0), 1 - math.exp(-2.0), 9)
        self.assertAlmostEqual(U.poisson_sf(5, 1.0), 0.0036598, 6)
        self.assertAlmostEqual(U.poisson_cdf(0, 2.0), math.exp(-2.0), 12)
        self.assertEqual(U.poisson_sf(3, 0.0), 0.0)

    def test_upper_limit(self):
        self.assertAlmostEqual(U.excess_upper95(0, 0.0), -math.log(0.05), 3)
        self.assertEqual(U.excess_upper95(0, 5.0), 0.0)
        self.assertGreater(U.excess_upper95(20, 5.0), 15.0)


def grid(extra=0, ie=22.0):
    pts = [(float(i), float(j), ie) for i in range(-20, 21) for j in range(-20, 21)]
    pts += [(0.0, 0.0, ie)] * extra
    return pts


class Statistic(unittest.TestCase):
    def test_coverage(self):
        pts = [(x, y) for x, y, _ in grid()]
        f_in, f_an = U.coverage_fractions(pts, 4.0, 8.0, 20.0)
        self.assertEqual((f_in, f_an), (1.0, 1.0))
        half = [(x, y) for x, y in pts if x >= 0]
        f_in, f_an = U.coverage_fractions(half, 4.0, 8.0, 20.0)
        self.assertAlmostEqual(f_in, 0.5, 9)

    def test_counts(self):
        c = U.circle_counts([(0.0, 0.0, 22.0)] * 10 + [(5.0, 0.0, 22.0)], 0.0, 0.0, 2.0)
        self.assertEqual(c, [10, 0, 0, 0])

    def test_detection_and_null(self):
        for extra, want in ((40, "CANDIDATE"), (0, "NO_COUNTERPART")):
            pts = grid(extra)
            dens, ann = U.annulus_density(pts, 1.0)
            self.assertAlmostEqual(dens[0], 1.0, 1)
            tr = U.trials_at(pts, 0.0, 0.0, dens)
            self.assertEqual(len(tr), U.n_trials())
            nulls = [U.min_p(U.trials_at(pts, cx, cy, dens)) for cx, cy in U.null_centres(7)]
            self.assertEqual(U.classify_target(U.min_p(tr), nulls, 1e-4), want)
        self.assertEqual(U.classify_control(1e-9, [0.5, 0.2]), "DETECTED")
        self.assertEqual(U.classify_control(1e-9, [1e-10]), "MISSED")
        self.assertEqual(U.classify_target(1e-9, [1e-10], 1e-4), "EXCESS_NOT_UNIQUE")

    def test_null_centres(self):
        a, b = U.null_centres(11), U.null_centres(11)
        self.assertEqual(a, b)
        self.assertEqual(len(a), U.N_NULL)
        for x, y in a:
            r = math.hypot(x, y)
            self.assertTrue(12.0 - 1e-9 <= r <= 16.0 + 1e-9)

    def test_overall(self):
        self.assertEqual(U.overall(False, 3, 1, [], []), "SCHEMA_MISMATCH")
        self.assertEqual(U.overall(True, 0, 1, ["DETECTED"], []), "NO_COVERAGE")
        self.assertEqual(U.overall(True, 3, 1, ["MISSED"], ["CANDIDATE"]), "CONTROL_FAILED")
        self.assertEqual(U.overall(True, 3, 2, ["MISSED", "DETECTED"], ["NO_COUNTERPART"]),
                         "NO_COUNTERPART")
        self.assertEqual(U.overall(True, 3, 0, [], ["CANDIDATE", "NO_COUNTERPART"]),
                         "CANDIDATES_UNCALIBRATED")


class IO(unittest.TestCase):
    def test_map_and_queries(self):
        cols = ["object_id", "right_ascension", "declination", "flux_vis_psf", "flux_h_templfit",
                "fluxerr_h_templfit", "point_like_flag", "point_like_prob", "spurious_flag"]
        m, ok = E.map_columns(cols)
        self.assertTrue(ok)
        self.assertEqual(m["ra"], "right_ascension")
        q = E.cone_query(m, 155.4, 18.1, 1 / 3, 26.5)
        self.assertIn("point_like_flag = 1", q)
        self.assertIn("spurious_flag = 0", q)
        self.assertIn("flux_vis_psf > 0.0912", q)
        m2, ok2 = E.map_columns(["right_ascension", "declination", "flux_vis_psf"])
        self.assertFalse(ok2)
        self.assertIn("COUNT(*)", E.count_query(m, 1.0, 2.0, 0.1))
        self.assertIsNone(E.fnum("nan"))
        self.assertIsNone(E.fnum(""))
        self.assertEqual(E.fnum("1.5"), 1.5)


if __name__ == "__main__":
    unittest.main()
