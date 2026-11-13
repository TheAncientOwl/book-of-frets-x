"""
Render chords-v4 bars, line repeats, and strumming patterns.
"""

from html import escape
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from . import register_section_entry_renderer
from .common import queue_strumming_patterns


@register_section_entry_renderer("chords-v4")
def render_chords_v4_section_entry(
    data: dict[str, Any],
    strumms: list[list[str]],
    styles: dict[str, Any],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
    render_context: dict[str, Any] | None = None,
) -> None:
    pattern_index = data["pattern"]
    if pattern_index < 0 or pattern_index >= len(strumms):
        raise ValueError(f"Strumming pattern index {pattern_index} is out of range")

    lines = data["lines"]
    if len(data["times"]) > len(lines):
        raise ValueError("chords-v4 times cannot contain more entries than lines")

    align = data.get("align", "center")
    if align not in {"center", "left"}:
        raise ValueError(f"Unsupported chords-v4 alignment {align!r}")

    show_badges = data.get("badge", True)
    if not isinstance(show_badges, bool):
        raise ValueError("chords-v4 badge must be a boolean")

    palette = theme["colors"]
    chord_style = styles["ChordLine"]
    if align == "left":
        chord_style = ParagraphStyle(
            "ChordLineLeft",
            parent=chord_style,
            alignment=TA_LEFT,
        )

    max_bars = max((len(line) for line in lines), default=0)
    if max_bars:
        rows: list[list[Any]] = []
        for line_index, bars in enumerate(lines):
            row: list[Any] = []
            for bar in bars:
                chords: list[str] = []
                for chord_id in bar:
                    label = escape(str(chords_map.get(chord_id, {}).get("name", chord_id)))
                    if show_badges:
                        chords.append(
                            f'<font backColor="{palette["surfaceHover"]}" '
                            f'color="{palette["accentText"]}"><b> {label} </b></font>'
                        )
                    else:
                        chords.append(f"<b>{label}</b>")
                row.append(Paragraph(" ".join(chords), chord_style))

            row.extend([""] * (max_bars - len(bars)))
            repeat = data["times"][line_index] if line_index < len(data["times"]) else 1
            row.append(
                Paragraph(
                    f'<font color="{palette["accent"]}"><b>×{repeat}</b></font>'
                    if repeat > 1
                    else "",
                    styles["Repeat"],
                )
            )
            rows.append(row)

        table = Table(rows, hAlign="CENTER")
        table_style = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBEFORE", (0, 0), (0, -1), 1, colors.HexColor(palette["accentText"])),
        ]
        table_style.extend(
            (
                "LINEAFTER",
                (column, row_index),
                (column, row_index),
                1,
                colors.HexColor(palette["accentText"]),
            )
            for row_index, bars in enumerate(lines)
            for column in range(len(bars))
        )
        if align == "left":
            table_style.append(("ALIGN", (0, 0), (-2, -1), "LEFT"))
        else:
            table_style.append(("ALIGN", (0, 0), (-2, -1), "CENTER"))
        table_style.append(("ALIGN", (-1, 0), (-1, -1), "LEFT"))
        table.setStyle(TableStyle(table_style))
        story.append(table)

    queue_strumming_patterns(
        [tuple(strumms[pattern_index])],
        render_context,
    )
