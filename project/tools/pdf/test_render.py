import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from render import DEFAULT_THEMES_PATH, load_theme_catalog, render_song_pdf


class SongPdfRendererTests(unittest.TestCase):
    def test_all_renderer_types_render_with_selected_theme(self) -> None:
        catalog = load_theme_catalog(DEFAULT_THEMES_PATH)
        song = {
            "title": "PDF Renderer Test",
            "artists": ["Test Artist"],
            "instrument": "guitar",
            "capo": 2,
            "notes": ["Test note"],
            "strumms": [["D", "U"], ["D", "-", "U"]],
            "sections": {
                "v1": {
                    "name": "Chords V1",
                    "times": 2,
                    "entries": [
                        {
                            "renderer": "chords-v1",
                            "data": [
                                {
                                    "times": 2,
                                    "items": [[["0 C 2 G 1"]]],
                                }
                            ],
                        }
                    ],
                },
                "v2": {
                    "name": "Chords V2",
                    "times": 1,
                    "entries": [
                        {
                            "renderer": "chords-v2",
                            "data": ["x2 C 2 | 0 G 1", "> 0"],
                        }
                    ],
                },
                "v3": {
                    "name": "Chords V3",
                    "times": 1,
                    "entries": [
                        {
                            "renderer": "chords-v3",
                            "data": {
                                "times": 2,
                                "items": [["x1 C 1 G 2", "> 1"]],
                            },
                        }
                    ],
                },
                "guitar": {
                    "name": "Guitar Tabs",
                    "times": 1,
                    "entries": [
                        {
                            "renderer": "gtab-v1",
                            "data": "[C] - e0 B1 G0 D2 A3 E0 |",
                        }
                    ],
                },
                "ukulele": {
                    "name": "Ukulele Tabs",
                    "times": 1,
                    "entries": [
                        {
                            "renderer": "ukulele-tabs-v1",
                            "data": "[C] - A3 E0 C0 G0 |",
                        }
                    ],
                },
            },
            "order": ["v1", "v2", "v3", "guitar", "ukulele"],
        }
        chords_map = {
            "C": {"name": "C"},
            "G": {"name": "G"},
        }

        for theme_id in ("graphite", "rosewater"):
            theme = next(theme for theme in catalog["themes"] if theme["id"] == theme_id)
            with tempfile.TemporaryDirectory() as temporary_directory:
                config_path = Path(temporary_directory) / "config.json"
                output_path = Path(temporary_directory) / f"song.{theme_id}.pdf"
                config_path.write_text(json.dumps(song), encoding="utf-8")
                render_song_pdf(config_path, output_path, chords_map, theme)

                reader = PdfReader(output_path)
                self.assertGreaterEqual(len(reader.pages), 1)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)

                for expected_text in (
                    "PDF Renderer Test",
                    "Chords V1",
                    "Chords V2",
                    "Chords V3",
                    "Guitar Tabs",
                    "Ukulele Tabs",
                    "CAPO 2",
                ):
                    self.assertIn(expected_text, text)
                self.assertEqual(
                    reader.metadata.subject if reader.metadata else None,
                    f"Song sheet in the {theme['name']} theme",
                )


if __name__ == "__main__":
    unittest.main()
