# 🎸 BookOfFrets-X

BookOfFrets is a web-based application designed to help guitar enthusiasts learn and explore songs through an interactive fretboard interface. It features a comprehensive collection of songs with detailed fret information, chords, a chord list, a song list, and customizable themes.

#### 🌐 Check out the live application at [book-of-frets.com](https://book-of-frets.com).

## 🕰️ History

- Initially, `book-of-frets` was made in `React` [@here](https://github.com/TheAncientOwl/book-of-frets).
- After some time I discovered [Astro](https://astro.build/) and thought it will be a better fit for the static content my website has.
- And here we are at `book-of-frets-x` which was initially a port of the `React` version, then updated continuously since then.

## ✨ Features

- **🎵 Songs with Frets:** Visualize songs with precise fret positions to help you learn finger placements.
- **🎼 Chords:** Access a rich library of chords with clear diagrams.
- **📖 Chord List:** Browse and search through a curated list of chords.
- **📂 Song List:** Easily navigate through a growing collection of songs.
- **🎨 Themes:** Choose a theme from the app menu. Your selected palette is saved on this device.
- **📺 Video Resources:** Learn how to play songs with helpful video tutorials.

## 🛠️ Main Feature

BookOfFrets is easily configurable via JSON files, allowing users and contributors to add new songs, chords, and themes without modifying the core code. This extensibility makes it simple to expand the app's content and tailor it to your preferences.

### Customize themes

Choose themes from the dedicated Themes page, linked in the app menu. Edit [`public/themes/index.json`](./public/themes/index.json) to change the available palettes or add a new theme. Add each theme to the `themes` array with a unique, lowercase `id`, a display `name`, `colorScheme: "dark"`, a `logo` path to its SVG in `public/themes/logos/`, a `mainColor` swatch, and the complete `colors` palette. Name the logo `public/themes/logos/<theme-id>.svg`. The selected logo is used in the app menu and as the browser favicon. `defaultTheme` selects the palette used when there is no saved selection. The selected theme is saved in the browser and falls back to the default if its id is no longer available.

The palettes include Banananana, Bright Sky, Bubble Gum, Catpuccin, Cherry, Hazbin, Lavander, Nature, Peach, and Pop N'Lock (the default).

The JSON file is validated by [`themes-index.schema.json`](./project/schemas/themes-index.schema.json). Palette keys map to the app's shared CSS variables (`page`, `surface`, `surfaceRaised`, `surfaceHover`, `text`, `muted`, `subtle`, `accent`, `accentText`, `accentStrong`, `highlight`, `onAccent`, `overlay`, and `scrollbar`).

## 🎶 Motivation

As a guitar learner, I found myself frustrated with the tedious process of writing chords and songs by hand. I wanted a prettier, more extensible solution that could grow with my learning journey. BookOfFrets was born out of this desire to create an intuitive and visually appealing tool that makes learning guitar more enjoyable and accessible.

## 🤝 Contribution

Contributions are welcome and encouraged! If you have new songs, chords, or themes to share, please submit a pull request. There are plenty of songs to showcase theme/chord/song configuration! Help us make BookOfFrets better for everyone.

## 📜 License

This project is licensed under the [MIT License](https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE).
