## Generate all song pages

A helper script can create Astro pages for every entry in `public/songs/index.json`.

```bash
/usr/bin/python3 project/tools/song/astro/generate_all_song_pages.py
```

Use `--dry-run` to preview the pages without writing files:

```bash
/usr/bin/python3 project/tools/song/astro/generate_all_song_pages.py --dry-run
```

The script writes one `.astro` page per song into `src/pages/songs/`, using the existing `src/pages/songs/i-wanna-be-yours-easy.astro` boilerplate pattern.
