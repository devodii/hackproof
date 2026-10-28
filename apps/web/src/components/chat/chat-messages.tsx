import { isToolUIPart, type ChatStatus, type UIMessage } from 'ai'
import * as React from 'react'
import { Link } from 'react-router'
import { type Components, Streamdown } from 'streamdown'

import { ToolCall } from '@/components/chat/tool-call'
import { useChatPanel } from '@/components/chat/use-chat-panel'
import { Spinner } from '@/components/spinner'

function ChatLink({
  href,
  children,
}: {
  href?: unknown
  children?: React.ReactNode
  node?: unknown
}) {
  const { close } = useChatPanel()
  const to = typeof href === 'string' ? href : ''
  const className = 'font-medium underline underline-offset-4 wrap-break-word'

  if (to.startsWith('/')) {
    return (
      <Link to={to} onClick={close} className={className}>
        {children}
      </Link>
    )
  }
  return (
    <a href={to} target="_blank" rel="noreferrer" className={className}>
      {children}
    </a>
  )
}

const components: Components = { a: ChatLink }

function isWaiting(messages: UIMessage[], status: ChatStatus) {
  if (status === 'submitted') return true
  if (status !== 'streaming') return false
  const last = messages.at(-1)
  return last?.role === 'assistant' && last.parts.every((part) => part.type === 'step-start')
}

function Message({ message, streaming }: { message: UIMessage; streaming: boolean }) {
  if (message.role === 'user') {
    const text = message.parts.map((part) => (part.type === 'text' ? part.text : '')).join('')
    return (
      <div className="ml-auto max-w-[85%] rounded-3xl rounded-br-md bg-primary px-4 py-2 text-sm whitespace-pre-wrap text-primary-foreground">
        {text}
      </div>
    )
  }

  return (
    <div className="flex flex-col items-start gap-2 text-sm md:text-base">
      {message.parts.map((part, index) => {
        if (isToolUIPart(part)) return <ToolCall key={part.toolCallId} part={part} />
        if (part.type === 'text' && part.text) {
          return (
            <div key={index} className="w-full min-w-0">
              <Streamdown
                components={components}
                isAnimating={streaming}
                linkSafety={{ enabled: false }}
                controls={{ table: false, code: true }}
                className="[&>*:first-child]:mt-0 [&>*:last-child]:mb-0"
              >
                {part.text}
              </Streamdown>
            </div>
          )
        }
        return null
      })}
    </div>
  )
}

interface ChatMessagesProps {
  messages: UIMessage[]
  status: ChatStatus
}

export function ChatMessages({ messages, status }: ChatMessagesProps) {
  const container = React.useRef<HTMLDivElement>(null)
  const pinned = React.useRef(true)

  React.useEffect(() => {
    const element = container.current
    if (element && pinned.current) element.scrollTop = element.scrollHeight
  }, [messages, status])

  return (
    <div
      ref={container}
      onScroll={(event) => {
        const { scrollTop, scrollHeight, clientHeight } = event.currentTarget
        pinned.current = scrollHeight - scrollTop - clientHeight < 96
      }}
      className="min-h-0 flex-1 overflow-y-auto overscroll-contain"
    >
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6">
        {messages.map((message, index) => (
          <Message
            key={message.id}
            message={message}
            streaming={status === 'streaming' && index === messages.length - 1}
          />
        ))}
        {isWaiting(messages, status) && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
            <Spinner size={20} />
            Thinking…
          </div>
        )}
      </div>
    </div>
  )
}
