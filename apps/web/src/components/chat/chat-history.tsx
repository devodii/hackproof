import { MessageSquareIcon, Trash2Icon } from 'lucide-react'

import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Button } from '@/components/ui/button'

const relative = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

function ago(timestamp: number) {
  const minutes = Math.round((timestamp - Date.now()) / 60_000)
  if (Math.abs(minutes) < 60) return relative.format(minutes, 'minute')
  const hours = Math.round(minutes / 60)
  if (Math.abs(hours) < 24) return relative.format(hours, 'hour')
  return relative.format(Math.round(hours / 24), 'day')
}

export function ChatHistory() {
  const { sessions, openSession, deleteSession, startChat } = useChatPanel()

  if (sessions.length === 0) {
    return (
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <MessageSquareIcon className="size-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">No conversations yet.</p>
        <Button variant="outline" onClick={() => startChat()}>
          Start one
        </Button>
      </div>
    )
  }

  return (
    <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
      <ul className="mx-auto flex w-full max-w-3xl flex-col gap-1 p-2">
        {sessions.map((session) => (
          <li key={session.id} className="group flex items-center gap-1">
            <button
              type="button"
              onClick={() => openSession(session.id)}
              className="flex min-w-0 flex-1 flex-col gap-0.5 rounded-xl px-3 py-2.5 text-left hover:bg-muted focus-visible:bg-muted focus-visible:outline-none"
            >
              <span className="truncate text-sm font-medium">{session.title}</span>
              <span className="text-xs text-muted-foreground">{ago(session.updatedAt)}</span>
            </button>
            <Button
              variant="ghost"
              size="icon-sm"
              className="shrink-0 text-muted-foreground sm:opacity-0 sm:group-hover:opacity-100 sm:focus-visible:opacity-100"
              aria-label={`Delete ${session.title}`}
              onClick={() => deleteSession(session.id)}
            >
              <Trash2Icon />
            </Button>
          </li>
        ))}
      </ul>
    </div>
  )
}
