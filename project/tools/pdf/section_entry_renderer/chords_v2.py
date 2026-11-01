"""
Render chords-v2 rows.
"""

from typing import Any

from . import register_section_entry_renderer
from .common import render_chords_v2_lines


@register_section_entry_renderer("chords-v2")
def render_chords_v2_section_entry(
    data: list[str],
    strumms: list[list[str]],
    styles: dict[str, Any],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
) -> None:
    render_chords_v2_lines(data, strumms, styles, chords_map, story, theme)
