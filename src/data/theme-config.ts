import { readFileSync } from 'node:fs';
import path from 'node:path';

export interface ThemeColors {
  page: string;
  surface: string;
  surfaceRaised: string;
  surfaceHover: string;
  text: string;
  muted: string;
  subtle: string;
  accent: string;
  accentText: string;
  accentStrong: string;
  highlight: string;
  onAccent: string;
  overlay: string;
  scrollbar: string;
  black: string;
  success: string;
  successStrong: string;
  successSurface: string;
  successSurfaceRaised: string;
  error: string;
  errorStrong: string;
  errorSurface: string;
  info: string;
}

export interface AppTheme {
  id: string;
  name: string;
  colorScheme: 'dark';
  logo: string;
  mainColor: string;
  colors: ThemeColors;
}

export interface ThemeConfig {
  defaultTheme: string;
  themes: AppTheme[];
}

const themeConfigPath = path.resolve(process.cwd(), 'public/themes/index.json');

const themeConfig = JSON.parse(readFileSync(themeConfigPath, 'utf8')) as ThemeConfig;

export default themeConfig;
