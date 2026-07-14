/**
 * --------------------------------------------------------------------------- *
 *                     Copyright (c) by BookOfFretsX 2026                      *
 * --------------------------------------------------------------------------- *
 * @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
 *
 * @file song.d.ts
 * @author Alexandru Delegeanu
 * @version 1.0
 * @description Song types for json mapping.
 */

export interface ISongsIndexEntry {
  title: string;
  artists: string[];
  directory: string;
  chordIDs: string[];
  type: string[];
  index?: number;
}
