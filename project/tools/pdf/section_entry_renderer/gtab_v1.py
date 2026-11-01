"""
Render six-string guitar tablature.
"""

from typing import Any

from . import register_section_entry_renderer
from .common import render_tabs


@register_section_entry_renderer("gtab-v1")
def render_gtab_v1_section_entry(
    data: str,
    _strumms: list[list[str]],
    styles: dict[str, Any],
    _chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
) -> None:
    _ = (_strumms, _chords_map)
    render_tabs(data, styles, story, theme, "guitar")
