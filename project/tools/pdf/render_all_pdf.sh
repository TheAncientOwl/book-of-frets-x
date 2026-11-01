# !/bin/bash
# -----------------------------------------------------------------------------
#                     Copyright (c) by BookOfFretsX 2026
# -----------------------------------------------------------------------------
# @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
#
# @file render_all_pdf.sh
# @author Alexandru Delegeanu
# @version 1.1
# @description Runs @see make_pdf.py for all songs with all themes
#

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

find public/songs -type f -name "config.json" -print0 |
    while IFS= read -r -d '' config; do
        echo ">> Rendering all theme PDFs for \"$config\""
        python3 project/tools/pdf/render.py "$config" --all-themes
    done
