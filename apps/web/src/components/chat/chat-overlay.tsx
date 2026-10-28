import { HistoryIcon, PlusIcon, XIcon } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect } from 'react'

import { ChatHistory } from '@/components/chat/chat-history'
import { ChatThread } from '@/components/chat/chat-thread'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'

const EASE = [0.22, 1, 0.36, 1] as const

export function ChatOverlay() {
  const { view, activeId, startChat, openHistory, close } = useChatPanel()
  const open = view !== 'closed'

  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => event.key === 'Escape' && close()
    const root = document.documentElement
    const overflow = root.style.overflow
    root.style.overflow = 'hidden'
    document.addEventListener('keydown', onKeyDown)
    return () => {
      root.style.overflow = overflow
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open, close])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Ask the data"
          className="fixed inset-0 z-50 flex flex-col bg-background/80"
          initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
          animate={{ opacity: 1, backdropFilter: 'blur(28px)' }}
          exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
          transition={{ duration: 0.35, ease: EASE }}
        >
          <motion.div
            className="flex min-h-0 flex-1 flex-col"
            initial={{ opacity: 0, y: 36, scale: 0.985 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.99, transition: { duration: 0.22, ease: EASE } }}
            transition={{ type: 'spring', stiffness: 240, damping: 28 }}
          >
            <header className="mx-auto flex w-full max-w-3xl items-center justify-between px-4 pt-[max(0.75rem,env(safe-area-inset-top))] pb-3">
              <h2 className="text-3xl leading-none">
                {view === 'history' ? 'History' : 'Ask the data'}
              </h2>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Chat history"
                  aria-pressed={view === 'history'}
                  onClick={openHistory}
                >
                  <HistoryIcon />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="New chat"
                  onClick={() => startChat()}
                >
                  <PlusIcon />
                </Button>
                <Button variant="ghost" size="icon" aria-label="Close chat" onClick={close}>
                  <XIcon />
                </Button>
              </div>
            </header>
            {view === 'history' ? <ChatHistory /> : <ChatThread key={activeId} />}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
