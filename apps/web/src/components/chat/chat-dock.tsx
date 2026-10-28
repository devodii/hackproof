import { HistoryIcon } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'

import { PromptBox } from '@/components/chat/prompt-box'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'

export function ChatDock() {
  const { view, sessions, startChat, openHistory } = useChatPanel()

  return (
    <AnimatePresence>
      {view === 'closed' && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 16 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className="pointer-events-none fixed inset-x-0 bottom-0 z-40 flex justify-center px-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
        >
          <div className="pointer-events-auto flex w-full max-w-xl items-end gap-2">
            <PromptBox
              className="flex-1 shadow-lg"
              placeholder="Ask anything about HackMeridian"
              onSubmit={startChat}
            />
            {sessions.length > 0 && (
              <Button
                variant="outline"
                size="icon-lg"
                className="size-12 shrink-0 rounded-full bg-card shadow-lg"
                aria-label="Chat history"
                onClick={openHistory}
              >
                <HistoryIcon />
              </Button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
