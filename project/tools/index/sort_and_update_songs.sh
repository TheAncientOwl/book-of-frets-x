# !/bin/bash
# -----------------------------------------------------------------------------
#                     Copyright (c) by BookOfFretsX 2026
# -----------------------------------------------------------------------------
# @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
#
# @file run.sh
# @author Alexandru Delegeanu
# @version 1.0
# @description Runs @see sort.py
#

python3 ./project/tools/index/_sort_and_update_songs.py public/songs/index.json index.html
