export type Region = 'latam' | 'europe' | 'asia'

export interface Language {
  code: string
  name: string
  region: Region
}

export const SOURCE_LANGUAGE = 'en'

export const REGION_LABEL: Record<Region, string> = {
  latam: 'Latin America',
  europe: 'Europe',
  asia: 'Asia',
}

export const LANGUAGES: Language[] = [
  { code: 'pt', name: 'Português (Brasil)', region: 'latam' },
  { code: 'es', name: 'Español', region: 'latam' },
  { code: 'pt-PT', name: 'Português (Portugal)', region: 'europe' },
  { code: 'fr', name: 'Français', region: 'europe' },
  { code: 'de', name: 'Deutsch', region: 'europe' },
  { code: 'it', name: 'Italiano', region: 'europe' },
  { code: 'tr', name: 'Türkçe', region: 'europe' },
  { code: 'zh-CN', name: '中文 (简体)', region: 'asia' },
  { code: 'ja', name: '日本語', region: 'asia' },
  { code: 'ko', name: '한국어', region: 'asia' },
  { code: 'hi', name: 'हिन्दी', region: 'asia' },
  { code: 'bn', name: 'বাংলা', region: 'asia' },
  { code: 'id', name: 'Bahasa Indonesia', region: 'asia' },
  { code: 'vi', name: 'Tiếng Việt', region: 'asia' },
  { code: 'th', name: 'ไทย', region: 'asia' },
  { code: 'tl', name: 'Filipino', region: 'asia' },
]

export const LANGUAGE_CODES = [SOURCE_LANGUAGE, ...LANGUAGES.map((language) => language.code)]

export function languageName(code: string) {
  return code === SOURCE_LANGUAGE
    ? 'English'
    : (LANGUAGES.find((language) => language.code === code)?.name ?? code)
}

export const LANGUAGE_STORAGE_KEY = 'language'

export function currentLanguage() {
  try {
    const stored: unknown = JSON.parse(localStorage.getItem(LANGUAGE_STORAGE_KEY) ?? 'null')
    return typeof stored === 'string' && LANGUAGE_CODES.includes(stored) ? stored : SOURCE_LANGUAGE
  } catch {
    return SOURCE_LANGUAGE
  }
}
