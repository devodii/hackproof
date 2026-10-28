import { createContext, useContext } from 'react'

import type { Session } from '@/components/chat/session'

export type PanelView = 'closed' | 'thread' | 'history'

export interface ChatPanel {
  sessions: Session[]
  view: PanelView
  activeId: string
  pendingPrompt: string | null
  startChat: (prompt?: string) => void
  openHistory: () => void
  openSession: (id: string) => void
  close: () => void
  deleteSession: (id: string) => void
  saveSession: (session: Session) => void
  takePrompt: () => string | null
}

export const ChatPanelContext = createContext<ChatPanel | null>(null)

export function useChatPanel() {
  const panel = useContext(ChatPanelContext)
  if (!panel) throw new Error('useChatPanel must be used inside ChatProvider')
  return panel
}
