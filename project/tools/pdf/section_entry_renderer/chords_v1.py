"""
Render the legacy chords-v1 line format.
"""

from html import escape
from typing import Any

from reportlab.platypus import Paragraph, Spacer

from . import register_section_entry_renderer
from .common import chord_sequence_markup


@register_section_entry_renderer("chords-v1")
def render_chords_v1_section_entry(
    data: list[dict[str, Any]],
    strumms: list[list[str]],
    styles: dict[str, Any],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
) -> None:
    accent = theme["colors"]["accent"]
    for repeated_block in data:
        times = repeated_block.get("times", 1)
        if times > 1:
            story.append(
                Paragraph(f'<font color="{accent}"><b>×{times}</b></font>', styles["Repeat"])
            )

        for chunk in repeated_block.get("items", []):
            for line_group in chunk:
                for line in line_group:
                    tokens = line.split()
                    if not tokens:
                        continue

                    pattern_index = int(tokens[0])
                    if pattern_index < 0 or pattern_index >= len(strumms):
                        raise ValueError(
                            f"Strumming pattern index {pattern_index} is out of range"
                        )

                    chord_markup = chord_sequence_markup(
                        tokens[1:], chords_map, accent
                    )
                    story.append(Paragraph(chord_markup, styles["ChordLine"]))
                    pattern = escape("   ".join(strumms[pattern_index]))
                    story.append(
                        Paragraph(
                            f'<font color="{theme["colors"]["subtle"]}">'
                            f"{pattern}</font>",
                            styles["StrumLine"],
                        )
                    )
                    story.append(Spacer(1, 5))
