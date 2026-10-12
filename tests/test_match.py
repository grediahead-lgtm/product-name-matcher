import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from name_matcher.__main__ import main  # noqa: E402
from name_matcher.match import match_lists, score, tokens  # noqa: E402


class ScoreTests(unittest.TestCase):
    def test_word_order_case_and_punctuation(self):
        self.assertGreaterEqual(score("Лежак Comfort сірий 40x30", "Сірий лежак Comfort, 40 х 30 см"), 0.9)

    def test_different_size_is_penalised(self):
        same = score("Лежак Comfort 40x30", "Лежак Comfort 40x30")
        diff = score("Лежак Comfort 40x30", "Лежак Comfort 50x40")
        self.assertLess(diff, 0.8)  # never an automatic match
        self.assertLess(diff, same)

    def test_apostrophes_and_ukrainian_letters(self):
        self.assertGreaterEqual(score("м'яч іграшка", "мяч игрушка"), 0.5)
        self.assertGreaterEqual(score("Сірий м’який лежак", "сірий мякий лежак"), 0.9)

    def test_empty_names(self):
        self.assertEqual(score("", "x"), 0.0)
        self.assertEqual(tokens("для та")[0], [])


class MatchTests(unittest.TestCase):
    A = ["Лежак Comfort сірий 40x30", "Миска сталева 500 мл", "Іграшка м'яч"]
    B = ["Сірий лежак Comfort, 40 х 30 см", "Миска сталева 700 мл", "Поводок рулетка 5 м"]

    def test_statuses(self):
        rows, only_b = match_lists(self.A, self.B)
        self.assertEqual(rows[0]["status"], "match")
        self.assertEqual(rows[2]["status"], "no_match")
        self.assertEqual(rows[2]["b"], "")
        self.assertEqual(only_b, ["Поводок рулетка 5 м"])

    def test_similar_but_not_equal_goes_to_review_not_match(self):
        rows, _ = match_lists(["Миска сталева 500 мл"], ["Миска сталева 700 мл"])
        self.assertIn(rows[0]["status"], ("review", "match"))
        self.assertLess(rows[0]["score"], 1.0)

    def test_one_to_one(self):
        rows, _ = match_lists(["Лежак Comfort", "Лежак Comfort"], ["Лежак Comfort"])
        self.assertEqual(sorted(r["status"] for r in rows), ["match", "no_match"])

    def test_deterministic(self):
        self.assertEqual(match_lists(self.A, self.B), match_lists(self.A, self.B))


class CliTests(unittest.TestCase):
    def test_cli_on_examples(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "m.csv")
            self.assertEqual(main([os.path.join(ROOT, "examples", "shop.csv"), os.path.join(ROOT, "examples", "supplier.csv"), "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["status"], "match")

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            main([os.path.join(ROOT, "examples", "shop.csv"), os.path.join(ROOT, "examples", "supplier.csv"), "--col-a", "nope"])


if __name__ == "__main__":
    unittest.main()
