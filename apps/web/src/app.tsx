import { Route, Routes } from 'react-router'

import { ChatDock } from '@/components/chat/chat-dock'
import { ChatOverlay } from '@/components/chat/chat-overlay'
import { ChatProvider } from '@/components/chat/chat-provider'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'
import { BuilderPage } from '@/pages/builder'
import { HomePage } from '@/pages/home'
import { IntegrationPage } from '@/pages/integration'
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
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/project/*" element={<ProjectPage />} />
            <Route path="/builder/:address" element={<BuilderPage />} />
            <Route path="/integration/:slug" element={<IntegrationPage />} />
            <Route path="/contributors" element={<ContributorsPage />} />
            <Route path="/contributor/:login" element={<PersonPage />} />
          </Routes>
        </main>
        <SiteFooter />
        <ChatDock />
      </div>
      <ChatOverlay />
    </>
  )
}

export function App() {
  return (
    <Routes>
      <Route path="/wrapped" element={<WrappedPage />} />
      <Route
        path="*"
        element={
          <ChatProvider>
            <Shell />
          </ChatProvider>
        }
      />
    </Routes>
  )
}
