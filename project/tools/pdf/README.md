# Song PDF generator

`render.py` creates a styled PDF directly from a song's `config.json`. It reads
the current palette definitions in `public/themes/index.json`, automatically
uses the guitar or ukulele chord index from the song's `instrument`, and renders
all supported section types: `chords-v1`, `chords-v2`, `chords-v3`, `gtab-v1`,
and `ukulele-tabs-v1`. Sections are centered and flow in order down the first
column, then the second column, continuing on additional pages as needed.
Repeated strumming patterns are shown only once per section.

Render using a theme:

```bash
python3 project/tools/pdf/render.py public/songs/fur-elise/config.json --theme graphite
```

By default, the theme catalog's `defaultTheme` is used. PDFs are written to the
song's `pdf/` directory as `<song-directory>.<theme-id>.pdf`, which is the
filename used by the song page's PDF button. Render every theme with
`--all-themes`, or choose a destination with `--output` / `--output-dir`:

```bash
python3 project/tools/pdf/render.py public/songs/fur-elise/config.json --all-themes
python3 project/tools/pdf/render.py public/songs/fur-elise/config.json --theme sea-glass --output /tmp/fur-elise.pdf
```

Optional `--chords` and `--themes-index` arguments can point to alternate chord
indexes or theme catalogs. `./project/tools/booky.sh --render-pdf-themes
<song-config.json>` generates all theme variants for one song; `--render-pdf-all`
does so for every song config.

The PDF button opens the pre-rendered PDF matching the currently active theme.
For a static deployment, run the theme-generation command after changing a
song config or adding a theme.
