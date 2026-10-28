import { Route, Routes } from 'react-router'

import { ChatDock } from '@/components/chat/chat-dock'
import { ChatOverlay } from '@/components/chat/chat-overlay'
import { ChatProvider } from '@/components/chat/chat-provider'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { About } from '@/components/layout/about'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'
import { BuilderPage } from '@/pages/builder'
import { HomePage } from '@/pages/home'
import { MethodologyPage } from '@/pages/methodology'
import { ProjectPage } from '@/pages/project'
import { SummaryPage } from '@/pages/summary'

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
            <Route path="/summary" element={<SummaryPage />} />
            <Route path="/methodology" element={<MethodologyPage />} />
          </Routes>
        </main>
        <About />
        <SiteFooter />
        <ChatDock />
      </div>
      <ChatOverlay />
    </>
  )
}

export function App() {
  return (
    <ChatProvider>
      <Shell />
    </ChatProvider>
  )
}
