import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import en from './locales/en.json'
import pt from './locales/pt.json'

const savedLanguage = typeof window !== 'undefined' ? localStorage.getItem('hackproof-language') : null
const initialLanguage = savedLanguage ? JSON.parse(savedLanguage) : 'en'

void i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      pt: { translation: pt },
      'pt-PT': { translation: pt },
    },
    lng: initialLanguage === 'pt' ? 'pt' : 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
