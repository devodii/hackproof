import { MoonIcon, SunIcon } from 'lucide-react'
import { useTheme } from 'next-themes'
import * as React from 'react'
import { Link } from 'react-router'

import { HackathonSwitcher } from '@/components/hackathon/hackathon-switcher'
import { IntegrationsMenu } from '@/components/layout/integrations-menu'
import { Button } from '@/components/ui/button'
import { HackathonContext } from '@/hooks/use-hackathon'

export function SiteHeader() {
  const { resolvedTheme, setTheme } = useTheme()
  const hackathon = React.useContext(HackathonContext)

  return (
    <header className="sticky top-0 z-30 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-1.5">
          <Link to="/" translate="no" className="font-heading text-2xl leading-none">
            HackProof
          </Link>
          {hackathon && (
            <>
              <span className="text-muted-foreground/60">/</span>
              <HackathonSwitcher />
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hackathon?.indexed && <IntegrationsMenu />}
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
