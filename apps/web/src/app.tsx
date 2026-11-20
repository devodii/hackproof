import { Outlet, Route, Routes, useLocation } from 'react-router'

import { ChatDock } from '@/components/chat/chat-dock'
import { ChatOverlay } from '@/components/chat/chat-overlay'
import { ChatProvider } from '@/components/chat/chat-provider'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { HackathonScope } from '@/components/hackathon/hackathon-scope'
import { LegacyRedirect } from '@/components/hackathon/legacy-redirect'
import { Frame } from '@/components/layout/frame'
import { LanguageProvider } from '@/components/layout/language-provider'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'
import { FILTER_KEYS } from '@/lib/hackathons'
import { BuilderPage } from '@/pages/builder'
import { HackathonsPage } from '@/pages/hackathons'
import { HomePage } from '@/pages/home'
import { IntegrationPage } from '@/pages/integration'
import { NotFoundPage } from '@/pages/not-found'
import { ContributorsPage } from '@/pages/contributors'
import { PersonPage } from '@/pages/person'
import { ProjectPage } from '@/pages/project'
import { WrappedPage } from '@/pages/wrapped'

function Shell() {
  const { view } = useChatPanel()

  return (
    <>
      <div
        inert={view !== 'closed'}
        className="flex min-h-svh flex-col bg-background pb-24 text-foreground"
      >
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-12">
          <Outlet />
        </main>
        <SiteFooter />
        <ChatDock />
      </div>
      <ChatOverlay />
    </>
  )
}

function Landing() {
  const { search } = useLocation()
  const legacy = [...new URLSearchParams(search).keys()].some((key) => !FILTER_KEYS.includes(key))
  if (legacy) return <LegacyRedirect />

  return (
    <Frame>
      <HackathonsPage />
    </Frame>
  )
}

const LEGACY_PATHS = [
  '/wrapped',
  '/project/*',
  '/builder/:address',
  '/integration/:slug',
  '/contributors',
  '/contributor/:login',
]

export function App() {
  return (
    <LanguageProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/hackathon/:id" element={<HackathonScope />}>
          <Route path="wrapped" element={<WrappedPage />} />
          <Route
            element={
              <ChatProvider>
                <Shell />
              </ChatProvider>
            }
          >
            <Route index element={<HomePage />} />
            <Route path="project/*" element={<ProjectPage />} />
            <Route path="builder/:address" element={<BuilderPage />} />
            <Route path="integration/:slug" element={<IntegrationPage />} />
            <Route path="contributors" element={<ContributorsPage />} />
            <Route path="contributor/:login" element={<PersonPage />} />
          </Route>
        </Route>
        {LEGACY_PATHS.map((path) => (
          <Route key={path} path={path} element={<LegacyRedirect />} />
        ))}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </LanguageProvider>
  )
}
