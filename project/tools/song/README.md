# Song Create Tool

Helper script used to generate a new song directory along with its required assets and configuration.

This tool:

- Creates a song directory under `public/songs/`
- Moves a provided cover image into the directory
- Converts the cover image to **WebP**
- Resizes the cover image to the required dimensions
- Generates the song configuration boilerplate

---

## Usage

```bash
./project/tools/song/create/run.sh <dir-name> <cover-image-src-path>
```

## Ukulele songs

Set `"instrument": "ukulele"` in a song's `config.json` to resolve its `chordIDs`
and chord diagrams from `public/chords/ukulele/index.json`. Songs without an
`instrument` setting continue to use guitar chords.

For four-string tabs, add a section entry with renderer `"ukulele-tabs-v1"`.
Tab data uses the `G`, `C`, `E`, and `A` string labels, for example:

```json
{ "renderer": "ukulele-tabs-v1", "data": "G0+C0+E0+A3 [C] - A3" }
```
