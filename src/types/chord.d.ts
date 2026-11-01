/**
 * --------------------------------------------------------------------------- *
 *                     Copyright (c) by BookOfFrets 2025                      *
 * --------------------------------------------------------------------------- *
 * @license https://github.com/TheAncientOwl/book-of-frets-x/blob/main/LICENSE
 *
 * @file chord.d.ts
 * @author Alexandru Delegeanu
 * @version 1.0
 * @description Chords types for json mapping.
 */

import type { TGuitarString, TUkuleleString } from '#types/common';

export type TChordInstrument = 'guitar' | 'ukulele';
export type TChordString = TGuitarString | TUkuleleString;
export type TFret = Partial<Record<TChordString, number>>;

export type TChord = {
  name: string;
  startFret?: number;
  frets: TFret[];
};

export type TChordsIndex = Record<string, TChord>;
