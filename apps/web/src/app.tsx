import { Outlet, Route, Routes } from 'react-router'

import { ChatDock } from '@/components/chat/chat-dock'
import { ChatOverlay } from '@/components/chat/chat-overlay'
import { ChatProvider } from '@/components/chat/chat-provider'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { HackathonScope } from '@/components/hackathon/hackathon-scope'
import { Backdrop } from '@/components/wrapped/backdrop'
import { Frame } from '@/components/layout/frame'
import { LanguageProvider } from '@/components/layout/language-provider'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'
import { AccountPage } from '@/pages/account'
import { BuilderPage } from '@/pages/builder'
import { HackathonsPage } from '@/pages/hackathons'
import { HomePage } from '@/pages/home'
import { IntegrationPage } from '@/pages/integration'
import { NotFoundPage } from '@/pages/not-found'
import { ContributorsPage } from '@/pages/contributors'
import { ProjectPage } from '@/pages/project'
import { WrappedPage } from '@/pages/wrapped'

function Shell() {
  const { view } = useChatPanel()

  return (
    <>
      <div
        inert={view !== 'closed'}
        className="relative isolate flex min-h-svh flex-col overflow-x-clip bg-background pb-24 text-foreground"
      >
        <Backdrop />
        <SiteHeader />
        <main className="relative mx-auto w-full max-w-6xl flex-1 px-6 py-12">
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
  return (
    <Frame>
      <HackathonsPage />
    </Frame>
  )
}

export function App() {
  return (
    <LanguageProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/builder/:login"
          element={
            <Frame>
              <BuilderPage />
            </Frame>
          }
        />
        <Route
          path="/integration/:slug"
          element={
            <Frame>
              <IntegrationPage />
            </Frame>
          }
        />
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
            <Route path="account/:address" element={<AccountPage />} />
            <Route path="contributors" element={<ContributorsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </LanguageProvider>
  )
}
