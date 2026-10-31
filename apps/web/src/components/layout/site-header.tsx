import { CrownIcon, ExternalLinkIcon, MoonIcon, SunIcon } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'

import { Button } from '@/components/ui/button'
import { REPO_URL } from '@/lib/config'

export function SiteHeader() {
  const { resolvedTheme, setTheme } = useTheme()
  const { t } = useTranslation()

  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="font-heading text-2xl leading-none">
          HackProof
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/?award=first&award=runner-up"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <CrownIcon className="size-3.5" /> {t('nav.winners')}
          </Link>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            {t('nav.openSource')} <ExternalLinkIcon className="size-3.5" />
          </a>
          <Button
            variant="ghost"
            size="icon"
            aria-label={t('nav.toggleTheme')}
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
          >
            <SunIcon className="hidden dark:block" />
            <MoonIcon className="dark:hidden" />
          </Button>
        </div>
      </div>
    </header>
  )
}
