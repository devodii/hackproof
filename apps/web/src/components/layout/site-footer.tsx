import { LanguageMenu } from '@/components/layout/language-menu'
import { REPO_URL } from '@/lib/config'

export function SiteFooter() {
  return (
    <footer id="site-footer" className="border-t">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-6 py-6 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <p>Independent project, not affiliated with SDF or Guava.</p>
        <div className="flex items-center gap-4">
          <LanguageMenu />
          <a href={REPO_URL} target="_blank" rel="noreferrer" className="hover:text-foreground">
            GitHub
          </a>
        </div>
      </div>
    </footer>
  )
}
