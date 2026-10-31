import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { useLocalStorageState } from '@/hooks/use-local-storage-state'

const LangSchema = z.enum(['en', 'pt'])
type Language = z.infer<typeof LangSchema>

export function LanguageToggle() {
  const { i18n, t } = useTranslation()
  const [lang, setLang] = useLocalStorageState<Language>('hackproof-language', 'en', LangSchema)

  useEffect(() => {
    if (lang && i18n.language !== lang) {
      void i18n.changeLanguage(lang)
    }
  }, [lang, i18n])

  const toggleLanguage = () => {
    const next: Language = lang === 'pt' ? 'en' : 'pt'
    setLang(next)
    void i18n.changeLanguage(next)
  }

  const current = lang === 'pt' ? 'pt' : 'en'

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground">{t('footer.language')}:</span>
      <Button
        variant="outline"
        size="sm"
        className="h-7 px-2 text-xs font-medium"
        onClick={toggleLanguage}
        title={current === 'pt' ? 'Mudar para Inglês' : 'Mudar para Português'}
      >
        {current === 'pt' ? '🇵🇹 PT-PT' : '🇬🇧 EN'}
      </Button>
    </div>
  )
}
