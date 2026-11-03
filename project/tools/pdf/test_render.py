import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from reportlab.lib.enums import TA_CENTER
from pypdf import PdfReader

from render import (
    DEFAULT_THEMES_PATH,
    load_theme_catalog,
    make_styles,
    render_song_pdf,
)
from section_entry_renderer.chords_v1 import render_chords_v1_section_entry
from section_entry_renderer.chords_v2 import render_chords_v2_section_entry
from section_entry_renderer.common import render_queued_strumming_patterns


class SongPdfRendererTests(unittest.TestCase):
    def test_repeated_strumming_patterns_render_once_per_section(self) -> None:
        catalog = load_theme_catalog(DEFAULT_THEMES_PATH)
        theme = next(theme for theme in catalog["themes"] if theme["id"] == "graphite")
        styles = make_styles(theme)
        strumms = [["D", "U"]]
        chords_map = {"C": {"name": "C"}, "G": {"name": "G"}}
        render_context: dict[str, Any] = {
            "strum_patterns": set(),
            "pending_strum_patterns": [],
        }
        story: list[Any] = []

        render_chords_v1_section_entry(
            [{"times": 1, "items": [[["0 C 1", "0 G 1"]]]}],
            strumms,
            styles,
            chords_map,
            story,
            theme,
            render_context,
        )
        render_chords_v2_section_entry(
            ["x1 C 1", "> 0", "x1 G 1", "> 0"],
            strumms,
            styles,
            chords_map,
            story,
            theme,
            render_context,
        )

        self.assertFalse(any(getattr(item, "style", None) == styles["StrumLine"] for item in story))
        render_queued_strumming_patterns(render_context, styles, story, theme)

        chord_line_indexes = [
            index
            for index, item in enumerate(story)
            if getattr(item, "style", None) == styles["ChordLine"]
        ]
        strum_line_indexes = [
            index
            for index, item in enumerate(story)
            if getattr(item, "style", None) == styles["StrumLine"]
        ]
        self.assertLess(max(chord_line_indexes), min(strum_line_indexes))
        strum_lines = [story[index] for index in strum_line_indexes]
        self.assertEqual(len(strum_lines), 1)

    def test_section_content_styles_are_centered(self) -> None:
        theme = load_theme_catalog(DEFAULT_THEMES_PATH)["themes"][0]
        styles = make_styles(theme)
        self.assertLess(styles["CoverTitle"].fontSize, 21)
        self.assertEqual(styles["SectionTitle"].alignment, TA_CENTER)
        self.assertEqual(styles["ChordLine"].alignment, TA_CENTER)
        self.assertEqual(styles["StrumLine"].alignment, TA_CENTER)
        self.assertEqual(styles["Repeat"].alignment, TA_CENTER)

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
        for index in range(1, 11):
            section_id = f"overflow-{index}"
            song["sections"][section_id] = {
                "name": f"Overflow {index}",
                "times": 1,
                "entries": [
                    {
                        "renderer": "chords-v2",
                        "data": ["x1 C 1 G 1"] * 3,
                    }
                ],
            }
            song["order"].append(section_id)

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
                section_x_positions: dict[str, float] = {}
                expected_sections = {
                    "chords v1",
                    "chords v2",
                    "chords v3",
                    "guitar tabs",
                    "ukulele tabs",
                    *(f"overflow {index}" for index in range(1, 11)),
                }

                def collect_section_positions(
                    extracted_text: str,
                    current_matrix: list[float],
                    text_matrix: list[float],
                    _font_dict: Any,
                    _font_size: float,
                ) -> None:
                    section_name = extracted_text.strip().casefold()
                    matched_section = next(
                        (
                            name
                            for name in sorted(
                                expected_sections, key=len, reverse=True
                            )
                            if section_name.startswith(name)
                        ),
                        None,
                    )
                    if matched_section is not None:
                        section_x_positions[matched_section] = current_matrix[4]

                for page in reader.pages:
                    page.extract_text(visitor_text=collect_section_positions)

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
                self.assertNotIn("STRUM", text)
                self.assertLess(text.index("Chords V1"), text.index("Chords V2"))
                self.assertLess(text.index("Chords V2"), text.index("Chords V3"))
                self.assertEqual(
                    section_x_positions["chords v1"],
                    section_x_positions["chords v2"],
                )
                self.assertEqual(
                    section_x_positions["chords v2"],
                    section_x_positions["chords v3"],
                )
                self.assertEqual(
                    section_x_positions["guitar tabs"],
                    section_x_positions["chords v3"],
                )
                self.assertEqual(
                    section_x_positions["guitar tabs"],
                    section_x_positions["ukulele tabs"],
                )
                first_column_x = section_x_positions["chords v1"]
                self.assertTrue(
                    any(
                        x > first_column_x
                        for name, x in section_x_positions.items()
                        if name.startswith("overflow ")
                    ),
                    msg=repr(section_x_positions),
                )
                self.assertEqual(
                    reader.metadata.subject if reader.metadata else None,
                    f"Song sheet in the {theme['name']} theme",
                )


if __name__ == "__main__":
    unittest.main()
