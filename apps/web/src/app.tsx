import { Route, Routes } from 'react-router'

import { About } from '@/components/layout/about'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'
import { BuilderPage } from '@/pages/builder'
import { HomePage } from '@/pages/home'
import { MethodologyPage } from '@/pages/methodology'
import { ProjectPage } from '@/pages/project'
import { SummaryPage } from '@/pages/summary'

export function App() {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-12">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/project/*" element={<ProjectPage />} />
          <Route path="/builder/:address" element={<BuilderPage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/methodology" element={<MethodologyPage />} />
        </Routes>
      </main>
      <About />
      <SiteFooter />
    </div>
  )
}
