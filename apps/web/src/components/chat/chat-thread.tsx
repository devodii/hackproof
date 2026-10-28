import { useChat } from '@ai-sdk/react'
import { useCallback, useEffect, useRef } from 'react'

import { ChatError } from '@/components/chat/chat-error'
import { ChatMessages } from '@/components/chat/chat-messages'
import { PromptBox } from '@/components/chat/prompt-box'
import { sessionTitle } from '@/components/chat/session'
import { SUGGESTIONS } from '@/components/chat/suggestions'
import { RateLimitError, transport } from '@/components/chat/transport'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'

function EmptyThread({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto flex min-h-full w-full max-w-3xl flex-col justify-center gap-6 px-4 py-6">
        <div className="flex flex-col gap-2">
          <h2 className="text-4xl leading-none sm:text-5xl">What do you want to know?</h2>
          <p className="text-sm text-muted-foreground">
            Projects, contracts, wasm uploads and builders from the 27 hour window. Answers come
            from live queries, not guesses.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <Button
              key={suggestion}
              variant="outline"
              className="h-auto justify-start rounded-2xl px-4 py-2.5 text-left whitespace-normal"
              onClick={() => onPick(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}

export function ChatThread() {
  const { activeId, sessions, saveSession, takePrompt } = useChatPanel()
  const { messages, sendMessage, regenerate, status, stop, error } = useChat({
    id: activeId,
    messages: sessions.find((session) => session.id === activeId)?.messages,
    transport,
  })

  const latest = useRef(messages)
  useEffect(() => {
    latest.current = messages
  }, [messages])

  const persist = useCallback(() => {
    if (latest.current.length === 0) return
    saveSession({
      id: activeId,
      title: sessionTitle(latest.current),
      updatedAt: Date.now(),
      messages: latest.current,
    })
  }, [activeId, saveSession])

  const persistOnExit = useRef(persist)
  useEffect(() => {
    persistOnExit.current = persist
  }, [persist])

  useEffect(() => {
    const timer = setTimeout(() => {
      const prompt = takePrompt()
      if (prompt) sendMessage({ text: prompt })
    }, 0)
    return () => clearTimeout(timer)
  }, [sendMessage, takePrompt])

  useEffect(() => {
    if (status === 'ready' || status === 'error') persist()
  }, [status, persist])

  useEffect(() => () => persistOnExit.current(), [])

  const busy = status === 'submitted' || status === 'streaming'

  return (
    <>
      {messages.length === 0 ? (
        <EmptyThread onPick={(text) => sendMessage({ text })} />
      ) : (
        <ChatMessages messages={messages} status={status} />
      )}
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-3 px-3 pt-2 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        {error && <ChatError error={error} onRetry={() => regenerate()} />}
        <PromptBox
          autoFocus
          busy={busy}
          onStop={stop}
          disabled={error instanceof RateLimitError}
          placeholder="Ask a follow up"
          onSubmit={(text) => sendMessage({ text })}
        />
      </div>
    </>
  )
}
