import { isToolUIPart, type ChatStatus, type UIMessage } from 'ai'
import { useEffect, useRef } from 'react'

import { ChatMarkdown } from '@/components/chat/chat-markdown'
import { ToolCall } from '@/components/chat/tool-call'
import { Spinner } from '@/components/spinner'

function isWaiting(messages: UIMessage[], status: ChatStatus) {
  if (status === 'submitted') return true
  if (status !== 'streaming') return false
  const last = messages.at(-1)
  return last?.role === 'assistant' && last.parts.every((part) => part.type === 'step-start')
}

function Message({ message }: { message: UIMessage }) {
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
              <ChatMarkdown>{part.text}</ChatMarkdown>
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
  const container = useRef<HTMLDivElement>(null)
  const pinned = useRef(true)

  useEffect(() => {
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
        {messages.map((message) => (
          <Message key={message.id} message={message} />
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
