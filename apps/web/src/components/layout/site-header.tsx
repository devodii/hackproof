import { MoonIcon, SunIcon } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Link } from 'react-router'

import { Button } from '@/components/ui/button'

export function SiteHeader() {
  const { resolvedTheme, setTheme } = useTheme()

  return (
    <header className="border-b">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-6">
        <nav className="flex items-center gap-6">
          <Link to="/" className="font-heading text-2xl leading-none">
            hackproof
          </Link>
          <Link to="/summary" className="text-sm text-muted-foreground hover:text-foreground">
            Summary
          </Link>
          <Link to="/methodology" className="text-sm text-muted-foreground hover:text-foreground">
            Methodology
          </Link>
        </nav>
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
    </header>
  )
}
