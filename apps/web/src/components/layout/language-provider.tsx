import * as React from 'react'
import { z } from 'zod'

import { LanguageContext } from '@/hooks/use-language'
import { useLocalStorageState } from '@/hooks/use-local-storage-state'
import {
  loadTranslator,
  rememberLanguage,
  TRANSLATOR_CONTAINER,
  translateTo,
} from '@/lib/google-translate'
import { LANGUAGE_CODES, LANGUAGE_STORAGE_KEY, SOURCE_LANGUAGE } from '@/lib/languages'

const schema = z.enum(LANGUAGE_CODES as [string, ...string[]])

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [stored, setStored] = useLocalStorageState(LANGUAGE_STORAGE_KEY, SOURCE_LANGUAGE, schema)
  const code = stored ?? SOURCE_LANGUAGE

  React.useEffect(() => {
    rememberLanguage(code)
    if (code !== SOURCE_LANGUAGE) void loadTranslator()
  }, [])

  const select = React.useCallback(
    (next: string) => {
      setStored(next)
      rememberLanguage(next)
      if (next === SOURCE_LANGUAGE && !translateTo(next)) window.location.reload()
      else void loadTranslator().then(() => translateTo(next))
    },
    [setStored],
  )

  return (
    <LanguageContext value={{ code, select }}>
      <div id={TRANSLATOR_CONTAINER} aria-hidden className="sr-only" />
      {children}
    </LanguageContext>
  )
}
