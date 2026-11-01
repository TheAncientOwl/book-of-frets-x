# !/bin/bash
# -----------------------------------------------------------------------------
#                     Copyright (c) by BookOfFretsX 2026
# -----------------------------------------------------------------------------
# @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
#
# @file render_pdf_themes.sh
# @author Alexandru Delegeanu
# @version 1.1
# @description Runs @see make_pdf.py for a song with all themes
#

set -euo pipefail

if [ -z "$1" ]; then
    echo "Usage: $0 <song-config.json>"
    exit 1
fi

config_path="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

python3 project/tools/pdf/render.py "$config_path" --all-themes
