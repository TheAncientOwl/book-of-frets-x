"""
Render four-string ukulele tablature.
"""

from typing import Any

from . import register_section_entry_renderer
from .common import render_tabs


@register_section_entry_renderer("ukulele-tabs-v1")
def render_ukulele_tabs_v1_section_entry(
    data: str,
    _strumms: list[list[str]],
    styles: dict[str, Any],
    _chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
    _render_context: dict[str, Any] | None = None,
) -> None:
    _ = (_strumms, _chords_map, _render_context)
    render_tabs(data, styles, story, theme, "ukulele")
