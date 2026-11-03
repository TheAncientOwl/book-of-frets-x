"""
Render chords-v3 repeated groups using the chords-v2 line grammar.
"""

from typing import Any

from reportlab.platypus import Paragraph, Spacer

from . import register_section_entry_renderer
from .common import render_chords_v2_lines


@register_section_entry_renderer("chords-v3")
def render_chords_v3_section_entry(
    data: dict[str, Any],
    strumms: list[list[str]],
    styles: dict[str, Any],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
    render_context: dict[str, Any] | None = None,
) -> None:
    times = data["times"]
    for line_group in data["items"]:
        if times > 1:
            story.append(
                Paragraph(
                    f'<font color="{theme["colors"]["accent"]}"><b>×{times}</b></font>',
                    styles["Repeat"],
                )
            )
        render_chords_v2_lines(
            line_group, strumms, styles, chords_map, story, theme, render_context
        )
        story.append(Spacer(1, 3))
