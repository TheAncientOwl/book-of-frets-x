"""
Shared PDF building blocks for song section renderers.
"""

from html import escape
from typing import Any

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Preformatted, Spacer, Table, TableStyle


def chord_label(chord_id: str, chords_map: dict[str, Any]) -> str:
    chord = chords_map.get(chord_id, {})
    return str(chord.get("name", chord_id))


def chord_sequence_markup(tokens: list[str], chords_map: dict[str, Any], accent: str) -> str:
    parts: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if index + 1 >= len(tokens):
            raise ValueError(f"Incomplete chord/count pair near {token!r}")

        count = tokens[index + 1]
        if token in {"|", "/", "!", "?"}:
            if token == "/":
                parts.append("<br/>")
            elif token in {"|", "!"}:
                parts.append(f'<font color="{accent}">  |  </font>')
            else:
                parts.append(" ")
            index += 2
            continue

        label = chord_label(token, chords_map)
        if token == "-":
            parts.append('<font color="#888888">-</font>')
        elif count not in {"0", "1"}:
            parts.append(f"<b>{escape(label)}</b><super>{escape(count)}</super>")
        else:
            parts.append(f"<b>{escape(label)}</b>")
        index += 2

    return " ".join(parts)


def render_chords_v2_lines(
    data: list[str],
    strumms: list[list[str]],
    styles: dict[str, ParagraphStyle],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
) -> None:
    accent = theme["colors"]["accent"]
    for line in data:
        tokens = line.split()
        if not tokens:
            continue

        if tokens[0] == ">":
            pattern_ids = tokens[1:]
            patterns: list[str] = []
            for pattern_id in pattern_ids:
                index = int(pattern_id)
                if index < 0 or index >= len(strumms):
                    raise ValueError(f"Strumming pattern index {index} is out of range")
                patterns.append(" ".join(strumms[index]))
            paragraph = Paragraph(
                f'<font color="{accent}"><b>STRUM</b></font>  '
                f'<font name="Courier">{escape("    |    ".join(patterns))}</font>',
                styles["StrumLine"],
            )
            story.append(paragraph)
            story.append(Spacer(1, 4))
            continue

        if not tokens[0].startswith("x") or not tokens[0][1:].isdigit():
            raise ValueError(f"Unsupported chords-v2 line: {line!r}")

        repeat = int(tokens[0][1:])
        chord_markup = chord_sequence_markup(tokens[1:], chords_map, accent)
        repeat_markup = (
            f'<font color="{accent}"><b>×{repeat}</b></font>  ' if repeat > 1 else ""
        )
        story.append(
            Paragraph(f"{repeat_markup}{chord_markup}", styles["ChordLine"])
        )
    story.append(Spacer(1, 5))


STRING_ORDERS = {
    "guitar": ("e", "B", "G", "D", "A", "E"),
    "ukulele": ("A", "E", "C", "G"),
}
TAB_CHUNK_WIDTH = 76


def parse_tab_data(data: str, string_order: tuple[str, ...]) -> tuple[dict[str, str], list[tuple[int, str]]]:
    tracks = {name: ["|"] for name in string_order}
    chord_marks: list[tuple[int, str]] = []
    offset = 1

    for token in data.split():
        if token in {"-", "|"}:
            for track in tracks.values():
                track.append(token)
            offset += len(token)
            continue

        if token.startswith("[") and token.endswith("]"):
            chord_marks.append((offset, token[1:-1]))
            continue

        entries: dict[str, str] = {}
        for part in token.split("+"):
            string_name = next(
                (name for name in string_order if part.startswith(name)), None
            )
            if string_name is None:
                raise ValueError(f"Invalid tab token {part!r} for {string_order!r}")
            fret = part[len(string_name) :]
            fret = fret.replace("▲", "^").replace("▼", "v")
            valid_fret_characters = set("0123456789-Xx/\\^~hpbv")
            if not fret or any(character not in valid_fret_characters for character in fret):
                raise ValueError(f"Invalid fret value in tab token {part!r}")
            entries[string_name] = fret

        width = max(len(fret) for fret in entries.values())
        for string_name, track in tracks.items():
            fret = entries.get(string_name)
            track.append(fret.ljust(width, "-") if fret else "-" * width)
        offset += width

    for track in tracks.values():
        track.append("|")
    return {name: "".join(track) for name, track in tracks.items()}, chord_marks


def render_tabs(
    data: str,
    styles: dict[str, ParagraphStyle],
    story: list[Any],
    theme: dict[str, Any],
    instrument: str,
) -> None:
    string_order = STRING_ORDERS[instrument]
    tracks, chord_marks = parse_tab_data(data, string_order)
    total_width = max(map(len, tracks.values()), default=0)
    start = 0
    while start < total_width:
        end = min(start + TAB_CHUNK_WIDTH, total_width)
        if end < total_width:
            measure_end = tracks[string_order[0]].rfind("|", start + 32, end)
            if measure_end > start:
                end = measure_end + 1

        header = [" "] * (end - start)
        for offset, chord_name in chord_marks:
            local_offset = offset - start
            if 0 <= local_offset < len(header):
                for position, character in enumerate(chord_name):
                    if local_offset + position < len(header):
                        header[local_offset + position] = character

        lines = ["    " + "".join(header)]
        lines.extend(
            f"{name:>2} | {tracks[name][start:end]}" for name in string_order
        )
        tab_block = Preformatted(
            "\n".join(lines),
            ParagraphStyle(
                "TabBlock",
                parent=styles["Normal"],
                fontName="Courier",
                fontSize=8,
                leading=12,
                textColor=colors.HexColor(theme["colors"]["accentText"]),
            ),
        )
        table = Table([[tab_block]], hAlign="CENTER")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(theme["colors"]["surfaceRaised"])),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(theme["colors"]["accentStrong"])),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 8))
        start = end
