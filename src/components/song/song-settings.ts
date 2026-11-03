export const SONG_SETTINGS_STORAGE_KEY = 'book-of-frets-song-settings';

export const DEFAULT_SONG_SETTINGS = {
  songChordsList: true,
  chordFingers: true,
  songNotes: true,
  sectionTimes: true,
  chordTimes: true,
  chordTimesOne: true,
  strummingPattern: true,
};

export const SONG_SETTING_DEFINITIONS = [
  { key: 'songChordsList', label: 'Song Chords List' },
  { key: 'chordFingers', label: 'Chords Fingers' },
  { key: 'songNotes', label: 'Song Notes' },
  { key: 'sectionTimes', label: 'Section Times' },
  { key: 'chordTimes', label: 'Chord Times' },
  { key: 'chordTimesOne', label: 'Chord Times 1' },
  { key: 'strummingPattern', label: 'Strumming Pattern' },
] as const satisfies readonly { key: keyof typeof DEFAULT_SONG_SETTINGS; label: string }[];

export type SongSettingKey = keyof typeof DEFAULT_SONG_SETTINGS;
export type SongSettings = Record<SongSettingKey, boolean>;

export const isSongSettingKey = (value: string): value is SongSettingKey =>
  Object.hasOwn(DEFAULT_SONG_SETTINGS, value);

export function readSongSettings(): SongSettings {
  const stored = window.localStorage.getItem(SONG_SETTINGS_STORAGE_KEY);
  if (stored === null) return { ...DEFAULT_SONG_SETTINGS };

  let parsed: unknown;
  try {
    parsed = JSON.parse(stored);
  } catch (error) {
    console.error('Failed to parse saved song settings; using defaults.', error);
    return { ...DEFAULT_SONG_SETTINGS };
  }

  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    console.error('Saved song settings are invalid; using defaults.');
    return { ...DEFAULT_SONG_SETTINGS };
  }

  const savedSettings = parsed as Record<string, unknown>;
  const settings: SongSettings = { ...DEFAULT_SONG_SETTINGS };

  for (const definition of SONG_SETTING_DEFINITIONS) {
    const value = savedSettings[definition.key];
    if (typeof value === 'boolean') {
      settings[definition.key] = value;
    } else if (value !== undefined) {
      console.error(`Invalid saved value for song setting "${definition.key}".`);
    }
  }

  return settings;
}

export function writeSongSettings(settings: SongSettings): void {
  window.localStorage.setItem(SONG_SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}

export function applySongSettings(root: ParentNode, settings: SongSettings): void {
  root.querySelectorAll<HTMLElement>('[data-song-setting], [data-song-setting-one]').forEach(element => {
    const settingKey = element.dataset.songSetting;
    const oneSettingKey = element.dataset.songSettingOne;
    const visible =
      (!settingKey || !isSongSettingKey(settingKey) || settings[settingKey]) &&
      (!oneSettingKey || !isSongSettingKey(oneSettingKey) || settings[oneSettingKey]);

    element.hidden = !visible;
    if (visible) element.style.removeProperty('display');
    else element.style.setProperty('display', 'none');
  });
}
