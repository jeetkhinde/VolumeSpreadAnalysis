/**
 * Two editions of the same book, served side by side.
 *
 *   /            English  (unchanged URLs — the original edition stays put)
 *   /pa/         Punjabi
 *
 * Everything language-dependent goes through here: URLs, UI strings and the
 * <html lang> value. Pages pass `lang` down explicitly rather than sniffing the
 * URL, so a page can never disagree with the content it is rendering.
 */
import ui from '../data/i18n/ui.json';

export const LANGS = ['en', 'pa'] as const;
export type Lang = (typeof LANGS)[number];
export const DEFAULT_LANG: Lang = 'en';

export const LANG_META: Record<Lang, {
  /** the language's name in its own script — what the switcher shows */
  native: string;
  /** the language's name in English, for aria-labels and hreflang tables */
  english: string;
  /** BCP-47 tag for <html lang> and hreflang */
  tag: string;
  /** URL prefix, '' for the default language */
  prefix: string;
}> = {
  en: { native: 'English', english: 'English', tag: 'en', prefix: '' },
  pa: { native: 'ਪੰਜਾਬੀ', english: 'Punjabi', tag: 'pa', prefix: '/pa' },
};

const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** The other language — with two of them, "switch" means "the other one". */
export const otherLang = (lang: Lang): Lang => (lang === 'en' ? 'pa' : 'en');

/**
 * A path inside one edition. `p` is the language-independent part and always
 * starts with '/': href('pa', '/read/testing-supply/') -> '/pa/read/testing-supply/'
 */
export const href = (lang: Lang, p = '/') => `${BASE}${LANG_META[lang].prefix}${p}`;

/** UI string lookup with {name} interpolation, falling back to English. */
export function t(lang: Lang, key: string, vars?: Record<string, string | number>): string {
  const table = ui as Record<string, Record<string, string>>;
  const s = table[lang]?.[key] ?? table[DEFAULT_LANG][key] ?? key;
  return vars
    ? s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m))
    : s;
}

/** "p. 34" / "pp. 34–35", in the reader's language. */
export const pageLabel = (lang: Lang, a: number, b: number) =>
  a === b ? t(lang, 'pageOne', { a }) : t(lang, 'pageRange', { a, b });

/** Numbers read better localised, but chapter/page numbers must stay clickable
 *  against the printed book, so only large word counts get grouped. */
export const num = (lang: Lang, n: number) => n.toLocaleString(lang === 'pa' ? 'pa-IN' : 'en-GB');

/** Page <title>: "<what> · Master the Markets" in both editions. */
export const pageTitle = (lang: Lang, what: string) => `${what} · ${t(lang, 'bookTitle')}`;
