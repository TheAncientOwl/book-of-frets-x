#!/usr/bin/env python3
"""
---------------------------------------------------------------------------
                    Copyright (c) by BookOfFretsX 2025
---------------------------------------------------------------------------
 @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE

 @file generate_all_song_pages.py
 @author Alexandru Delegeanu
 @version 1.0
 @description Generate Astro song pages in src/pages/songs from public/songs/index.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
INDEX_PATH = ROOT / "public" / "songs" / "index.json"
OUTPUT_DIR = ROOT / "src" / "pages" / "songs"

TEMPLATE = """---
/**
 * --------------------------------------------------------------------------- *
 *                     Copyright (c) by BookOfFretsX 2026                      *
 * --------------------------------------------------------------------------- *
 * @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
 *
 * @file {filename}
 * @author Alexandru Delegeanu
 * @version 1.0
 * @description {description}
 */

import '#styles/global.css';

import SongLayout from '#layouts/SongLayout.astro';
import Song from '#components/song/Song.astro';

import type {{ TSong }} from '#types/song';
import configData from '#public/songs/{directory}/config.json';
const config = configData as TSong;
---

<SongLayout directory='{directory}'>
  <Song directory='{directory}' {{...config}} />
</SongLayout>
"""


def build_page_content(directory: str, title: str) -> str:
    filename = f"{directory}.astro"
    description = f"{title} song page."
    return TEMPLATE.format(filename=filename, description=description, directory=directory)


def load_index(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.exists():
        raise FileNotFoundError(f"Song index not found: {index_path}")

    with index_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or "index" not in data or not isinstance(data["index"], list):
        raise ValueError(f"Invalid index format in {index_path}")

    return data["index"]


def write_pages(entries: list[dict[str, object]], output_dir: Path, dry_run: bool = False) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []

    for entry in entries:
        directory = entry.get("directory")
        title = entry.get("title")

        if not isinstance(directory, str) or not directory.strip():
            print(f"Skipping invalid song entry with missing directory: {entry}")
            continue

        if not isinstance(title, str) or not title.strip():
            title = "Song"

        page_path = output_dir / f"{directory}.astro"
        content = build_page_content(directory=directory, title=title)

        if dry_run:
            print(f"Would create: {page_path}")
            created.append(page_path)
            continue

        current_text = page_path.read_text("utf-8") if page_path.exists() else None
        if current_text != content:
            page_path.write_text(content, encoding="utf-8")
            print(f"Created/updated: {page_path}")
        else:
            print(f"Unchanged: {page_path}")

        created.append(page_path)

    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Astro song pages from public/songs/index.json")
    parser.add_argument("--dry-run", action="store_true", help="Show which pages would be created without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    entries = load_index(INDEX_PATH)
    write_pages(entries, OUTPUT_DIR, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
