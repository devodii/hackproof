import * as React from 'react'

import { SOURCE_LANGUAGE } from '@/lib/languages'

export interface LanguageState {
  code: string
  select: (code: string) => void
}

export const LanguageContext = React.createContext<LanguageState>({
  code: SOURCE_LANGUAGE,
  select: () => {},
})

export const useLanguage = () => React.useContext(LanguageContext)
