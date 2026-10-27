import { Link } from 'react-router'

import { REPO_URL } from '@/lib/config'

export function SiteFooter() {
  return (
    <footer className="border-t">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-6 py-6 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <p>Independent project, not affiliated with SDF or Guava.</p>
        <nav className="flex gap-4">
          <Link to="/methodology" className="hover:text-foreground">
            Methodology
          </Link>
          <a href={REPO_URL} target="_blank" rel="noreferrer" className="hover:text-foreground">
            Source
          </a>
        </nav>
      </div>
    </footer>
  )
}
