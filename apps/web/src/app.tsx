import { Route, Routes } from 'react-router'

import { SiteHeader } from '@/components/layout/site-header'
import { BuilderPage } from '@/pages/builder'
import { HomePage } from '@/pages/home'
import { ProjectPage } from '@/pages/project'

export function App() {
  return (
    <div className="min-h-svh bg-background text-foreground">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl px-6 py-12">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/project/*" element={<ProjectPage />} />
          <Route path="/builder/:address" element={<BuilderPage />} />
        </Routes>
      </main>
    </div>
  )
}
