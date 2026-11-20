import { CrownIcon, ExternalLinkIcon, MoonIcon, SparklesIcon, SunIcon } from 'lucide-react'
import { useTheme } from 'next-themes'
import * as React from 'react'
import { Link as RouterLink } from 'react-router'

import { Link } from '@/components/hackathon/hackathon-link'
import { IntegrationsMenu } from '@/components/layout/integrations-menu'
import { Button } from '@/components/ui/button'
import { HackathonContext } from '@/hooks/use-hackathon'
import { REPO_URL } from '@/lib/config'

const NAV = 'inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground'

function HackathonLinks() {
  return (
    <>
      <Link to="/?award=first&award=runner-up" className={NAV}>
        <CrownIcon className="size-3.5" /> Winners
      </Link>
      <Link to="/wrapped" className={NAV}>
        <SparklesIcon className="size-3.5" /> Wrapped
      </Link>
      <IntegrationsMenu />
    </>
  )
}

export function SiteHeader() {
  const { resolvedTheme, setTheme } = useTheme()
  const hackathon = React.useContext(HackathonContext)

  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex min-w-0 items-baseline gap-2">
          <RouterLink to="/" translate="no" className="font-heading text-2xl leading-none">
            HackProof
          </RouterLink>
          {hackathon && (
            <Link
              to="/"
              translate="no"
              className="hidden truncate text-sm text-muted-foreground hover:text-foreground sm:inline"
            >
              / {hackathon.name}
            </Link>
          )}
        </div>
        <div className="flex items-center gap-3">
          {hackathon && <HackathonLinks />}
          <a href={REPO_URL} target="_blank" rel="noreferrer" className={NAV}>
            Open Source <ExternalLinkIcon className="size-3.5" />
          </a>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Toggle theme"
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
