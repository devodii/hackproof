import { type ReactNode, useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { sessionsSchema, type Session } from '@/components/chat/session'
import { type ChatPanel, ChatPanelContext, type PanelView } from '@/components/chat/use-chat-panel'
import { useLocalStorageState } from '@/hooks/use-local-storage-state'

const MAX_SESSIONS = 30

export function ChatProvider({ children }: { children: ReactNode }) {
  const [stored, setStored] = useLocalStorageState('hackproof.chat.sessions', [], sessionsSchema)
  const sessions = useMemo(() => stored ?? [], [stored])
  const latest = useRef(sessions)
  useEffect(() => {
    latest.current = sessions
  }, [sessions])

  const [view, setView] = useState<PanelView>('closed')
  const [activeId, setActiveId] = useState<string>(() => crypto.randomUUID())
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null)
  const prompt = useRef<string | null>(null)

  const startChat = useCallback((text?: string) => {
    prompt.current = text ?? null
    setPendingPrompt(prompt.current)
    setActiveId(crypto.randomUUID())
    setView('thread')
  }, [])

  const openSession = useCallback((id: string) => {
    prompt.current = null
    setPendingPrompt(null)
    setActiveId(id)
    setView('thread')
  }, [])

  const saveSession = useCallback(
    (session: Session) => {
      const others = latest.current.filter((item) => item.id !== session.id)
      setStored([session, ...others].slice(0, MAX_SESSIONS))
    },
    [setStored],
  )

  const deleteSession = useCallback(
    (id: string) => setStored(latest.current.filter((item) => item.id !== id)),
    [setStored],
  )

  const takePrompt = useCallback(() => {
    const text = prompt.current
    prompt.current = null
    return text
  }, [])

  const value = useMemo<ChatPanel>(
    () => ({
      sessions,
      view,
      activeId,
      pendingPrompt,
      startChat,
      openHistory: () => setView('history'),
      openSession,
      close: () => setView('closed'),
      deleteSession,
      saveSession,
      takePrompt,
    }),
    [
      sessions,
      view,
      activeId,
      pendingPrompt,
      startChat,
      openSession,
      deleteSession,
      saveSession,
      takePrompt,
    ],
  )

  return <ChatPanelContext.Provider value={value}>{children}</ChatPanelContext.Provider>
}
