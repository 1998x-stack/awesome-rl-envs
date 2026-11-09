"""Game list parser regression - does NOT contact third-party URLs."""
import json
from pathlib import Path
import unittest
from scripts.export_game_links import ROOT, SOURCE, OUTPUT, extract


class GameSectionTests(unittest.TestCase):
    def test_exact_section_preserves_original_elevent_references(self):
        doc = extract(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(len(doc["projects"]), 11)
        self.assertEqual(doc["projects"][0]["name"], "Coin-Run")
        self.assertEqual(doc["projects"][-1]["name"], "VizDoom")
        self.assertTrue(all(row["status"] == "not-verified" for row in doc["projects"]))
        self.assertEqual(doc, json.loads(OUTPUT.read_text(encoding="utf-8")))

    def test_only_games_heading_and_https_urls_are_allowed(self):
        self.assertEqual(
            extract("## Robotics\n<a href='https://example.com/robot'>Robot</a>\n"
                    "## Games\n<a href='https://example.com/a'>Test</a>\n"
                    "## Multi-Agent\n<a href='https://example.com/b'>Other</a>")
            ["projects"][0]["name"], "Test"
        )
        with self.assertRaises(ValueError):
            extract("## Games\n<a href='http://example.org'>Bad</a>")
        with self.assertRaises(ValueError):
            extract("## Games\n<a href='https://example.org'>One</a>\n"
                    "<a href='https://example.org'>Duplicate</a>")
        with self.assertRaises(ValueError):
            extract("## Not-Games\n<a href='https://example.org'>Wrong</a>")


if __name__ == "__main__":
    unittest.main()
