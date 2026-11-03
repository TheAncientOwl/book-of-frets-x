"""
Generate polished, theme-aware PDFs from BookOfFretsX song configuration files.
"""

import argparse
import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from section_entry_renderer import SectionEntryRenderer


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_THEMES_PATH = PROJECT_ROOT / "public" / "themes" / "index.json"
THEME_COLOR_KEYS = {
    "page",
    "surface",
    "surfaceRaised",
    "surfaceHover",
    "text",
    "muted",
    "subtle",
    "accent",
    "accentText",
    "accentStrong",
    "highlight",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def load_theme_catalog(path: Path) -> dict[str, Any]:
    catalog = load_json(path)
    themes = catalog.get("themes")
    if not isinstance(themes, list) or not themes:
        raise ValueError(f"Theme catalog {path} must contain a non-empty themes array")
    for theme in themes:
        validate_theme(theme)
    if not any(theme["id"] == catalog.get("defaultTheme") for theme in themes):
        raise ValueError("The theme catalog's defaultTheme does not match a theme id")
    return catalog


def validate_theme(theme: Any) -> None:
    if not isinstance(theme, dict) or not isinstance(theme.get("id"), str):
        raise ValueError("Theme catalog contains an invalid theme entry")
    palette = theme.get("colors")
    if not isinstance(palette, dict) or not THEME_COLOR_KEYS.issubset(palette):
        raise ValueError(f"Theme {theme['id']!r} is missing required PDF colors")
    if theme.get("colorScheme") not in {"dark", "light"}:
        raise ValueError(f"Theme {theme['id']!r} has an unsupported color scheme")
    for key in THEME_COLOR_KEYS:
        try:
            colors.HexColor(palette[key])
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Theme {theme['id']!r} has an invalid {key} color"
            ) from error


def make_styles(theme: dict[str, Any]) -> dict[str, ParagraphStyle]:
    palette = theme["colors"]
    sample = getSampleStyleSheet()
    normal = ParagraphStyle(
        "SongBody",
        parent=sample["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(palette["text"]),
        spaceAfter=0,
    )
    return {
        "Normal": normal,
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            textColor=colors.HexColor(palette["text"]),
            alignment=TA_LEFT,
        ),
        "CoverArtists": ParagraphStyle(
            "CoverArtists",
            parent=normal,
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor(palette["accentText"]),
            alignment=TA_LEFT,
        ),
        "Metadata": ParagraphStyle(
            "Metadata",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor(palette["muted"]),
            alignment=TA_LEFT,
        ),
        "Notes": ParagraphStyle(
            "Notes",
            parent=normal,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(palette["muted"]),
            alignment=TA_LEFT,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor(palette["accentText"]),
            alignment=TA_CENTER,
        ),
        "SectionRepeat": ParagraphStyle(
            "SectionRepeat",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(palette["accentText"]),
            alignment=TA_LEFT,
        ),
        "ChordLine": ParagraphStyle(
            "ChordLine",
            parent=normal,
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            alignment=TA_CENTER,
        ),
        "StrumLine": ParagraphStyle(
            "StrumLine",
            parent=normal,
            fontName="Courier",
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
        ),
        "Repeat": ParagraphStyle(
            "Repeat",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
    }


def render_section(
    section: dict[str, Any],
    song: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    chords_map: dict[str, Any],
    story: list[Any],
    theme: dict[str, Any],
    available_width: float,
) -> None:
    palette = theme["colors"]
    times = section.get("times", 1)
    repeat = (
        f' <font color="{palette["accent"]}">×{times}</font>' if times > 1 else ""
    )
    title = Paragraph(f'{escape(section["name"])}{repeat}', styles["SectionTitle"])
    heading = Table([[title]], colWidths=[available_width])
    heading.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(palette["surfaceRaised"])),
                ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(palette["accent"])),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    section_story: list[Any] = [heading, Spacer(1, 5)]

    for entry in section["entries"]:
        renderer_name = entry["renderer"]
        renderer = SectionEntryRenderer.get_renderer(renderer_name)
        if renderer is None:
            raise ValueError(f"Unsupported section renderer {renderer_name!r}")
        renderer(
            entry["data"],
            song.get("strumms", []),
            styles,
            chords_map,
            section_story,
            theme,
        )
    section_story.append(Spacer(1, 12))
    story.append(KeepTogether(section_story))


def cover_image_for(config_path: Path) -> Path | None:
    for filename in ("cover.webp", "cover-192x192.webp", "cover-128x128.webp"):
        candidate = config_path.parent / filename
        if candidate.is_file():
            return candidate
    return None


def render_cover(
    song: dict[str, Any],
    config_path: Path,
    styles: dict[str, ParagraphStyle],
    story: list[Any],
    theme: dict[str, Any],
    available_width: float,
) -> None:
    palette = theme["colors"]
    instrument = song.get("instrument", "guitar")
    metadata = f"{escape(instrument.upper())}  |  CAPO {song.get('capo', 0)}"
    text_rows: list[list[Any]] = [
        [Paragraph(escape(song["title"]), styles["CoverTitle"])],
        [Paragraph(escape(", ".join(song["artists"])), styles["CoverArtists"])],
        [Paragraph(metadata, styles["Metadata"])],
    ]
    notes = song.get("notes", [])
    if notes:
        note_text = "<br/>".join(escape(note) for note in notes)
        text_rows.append([Paragraph(note_text, styles["Notes"])])

    text_table = Table(text_rows, colWidths=[available_width - 72])
    text_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    image_path = cover_image_for(config_path)
    if image_path is not None:
        cover_content: list[Any] = [Image(str(image_path), width=52, height=52), text_table]
        widths = [62, available_width - 62]
    else:
        cover_content = [text_table]
        widths = [available_width]

    cover = Table([cover_content], colWidths=widths, hAlign="LEFT")
    cover.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(palette["surface"])),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(palette["accentStrong"])),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([cover, Spacer(1, 7)])


def render_song_pdf(
    config_path: Path,
    out_path: Path,
    chords_map: dict[str, Any],
    theme: dict[str, Any],
) -> None:
    validate_theme(theme)
    song = load_json(config_path)
    styles = make_styles(theme)
    page_width, page_height = A4
    margin = 12 * mm
    column_gap = 8 * mm
    available_width = page_width - 2 * margin
    column_width = (available_width - column_gap) / 2
    top_margin = 8 * mm
    bottom_margin = 18 * mm
    header_height = 31 * mm

    document = BaseDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        title=song["title"],
        author=", ".join(song["artists"]),
        subject=f"Song sheet in the {theme['name']} theme",
    )

    def make_column_frames(top: float) -> list[Frame]:
        frame_height = page_height - top - bottom_margin
        left_x = margin
        right_x = margin + column_width + column_gap
        return [
            Frame(
                left_x,
                bottom_margin,
                column_width,
                frame_height,
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
                id="left-column",
            ),
            Frame(
                right_x,
                bottom_margin,
                column_width,
                frame_height,
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
                id="right-column",
            ),
        ]

    story: list[Any] = []
    render_cover(song, config_path, styles, story, theme, available_width)
    header_frame = Frame(
        margin,
        page_height - top_margin - header_height,
        available_width,
        header_height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="song-header",
    )
    first_page_frames = [
        header_frame,
        *make_column_frames(top_margin + header_height),
    ]

    sections = song["sections"]
    ordered_sections: list[dict[str, Any]] = []
    for section_id in song["order"]:
        if section_id not in sections:
            raise ValueError(f"Song order refers to missing section {section_id!r}")
        ordered_sections.append(sections[section_id])

    story.append(NextPageTemplate("SongColumns"))
    for section in ordered_sections:
        render_section(
            section,
            song,
            styles,
            chords_map,
            story,
            theme,
            column_width,
        )

    page_color = colors.HexColor(theme["colors"]["page"])
    accent_color = colors.HexColor(theme["colors"]["accent"])
    muted_color = colors.HexColor(theme["colors"]["subtle"])

    def draw_page(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setFillColor(page_color)
        canvas.rect(0, 0, page_width, A4[1], fill=1, stroke=0)
        canvas.setFillColor(accent_color)
        canvas.rect(0, A4[1] - 4, page_width, 4, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor(theme["colors"]["surfaceRaised"]))
        canvas.setLineWidth(0.6)
        canvas.line(margin, 12 * mm, page_width - margin, 12 * mm)
        canvas.setFillColor(muted_color)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(margin, 7.5 * mm, song["title"])
        canvas.drawRightString(page_width - margin, 7.5 * mm, str(doc.page))
        canvas.restoreState()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    document.addPageTemplates(
        [
            PageTemplate("SongFirstPage", first_page_frames, onPage=draw_page),
            PageTemplate(
                "SongColumns",
                make_column_frames(top_margin),
                onPage=draw_page,
            ),
        ]
    )
    document.build(story)


def load_chords_map(path: Path) -> dict[str, Any]:
    data = load_json(path)
    index = data.get("index", data)
    if not isinstance(index, dict):
        raise ValueError(f"Chord index {path} must contain an object")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render song config JSON to theme-aware PDF."
    )
    parser.add_argument("config_path", type=Path, help="Song config.json path")
    theme_selection = parser.add_mutually_exclusive_group()
    theme_selection.add_argument(
        "--theme",
        help="Theme id from public/themes/index.json (defaults to the catalog default)",
    )
    theme_selection.add_argument(
        "--all-themes",
        action="store_true",
        help="Generate one PDF for every theme in the theme catalog",
    )
    parser.add_argument(
        "--themes-index",
        type=Path,
        default=DEFAULT_THEMES_PATH,
        help=f"Theme catalog JSON (default: {DEFAULT_THEMES_PATH})",
    )
    parser.add_argument(
        "--chords",
        type=Path,
        help="Optional chord index JSON; otherwise selected by song instrument",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PDF path for a single-theme render",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for generated PDFs (defaults to the song's pdf directory)",
    )
    args = parser.parse_args()

    if args.output and args.all_themes:
        parser.error("--output cannot be combined with --all-themes; use --output-dir")

    config_path = args.config_path.resolve()
    song = load_json(config_path)
    catalog = load_theme_catalog(args.themes_index.resolve())
    themes = catalog["themes"]
    if args.all_themes:
        selected_themes = themes
    else:
        theme_id = args.theme or catalog["defaultTheme"]
        selected_theme = next((theme for theme in themes if theme["id"] == theme_id), None)
        if selected_theme is None:
            available = ", ".join(theme["id"] for theme in themes)
            parser.error(f"Unknown theme {theme_id!r}. Available themes: {available}")
        selected_themes = [selected_theme]

    if args.chords:
        chords_map = load_chords_map(args.chords.resolve())
    else:
        instrument = song.get("instrument", "guitar")
        chord_index_path = PROJECT_ROOT / "public" / "chords" / "index.json"
        if instrument == "ukulele":
            chord_index_path = (
                PROJECT_ROOT / "public" / "chords" / "ukulele" / "index.json"
            )
        chords_map = load_chords_map(chord_index_path)

    output_dir = args.output_dir.resolve() if args.output_dir else config_path.parent / "pdf"
    for theme in selected_themes:
        output_path = (
            args.output.resolve()
            if args.output
            else output_dir / f"{config_path.parent.name}.{theme['id']}.pdf"
        )
        render_song_pdf(config_path, output_path, chords_map, theme)
        print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
