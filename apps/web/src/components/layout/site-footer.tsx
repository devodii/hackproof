import { useTranslation } from 'react-i18next'

import { LanguageToggle } from '@/components/layout/language-toggle'
import { REPO_URL } from '@/lib/config'

export function SiteFooter() {
  const { t } = useTranslation()

  return (
    <footer className="border-t">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-6 py-6 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <p>{t('footer.disclaimer')}</p>
        <div className="flex items-center gap-4">
          <LanguageToggle />
          <a href={REPO_URL} target="_blank" rel="noreferrer" className="hover:text-foreground">
            {t('footer.github')}
          </a>
        </div>
      </div>
    </footer>
  )
}
