import type { UIMessage } from 'ai'
import { z } from 'zod'

const messageSchema = z.looseObject({
  id: z.string(),
  role: z.enum(['user', 'assistant', 'system']),
  parts: z.array(z.looseObject({ type: z.string() })),
}) as unknown as z.ZodType<UIMessage>

export const sessionSchema = z.object({
  id: z.string(),
  title: z.string(),
  updatedAt: z.number(),
  messages: z.array(messageSchema),
})

export const sessionsSchema = z.array(sessionSchema)

export type Session = z.infer<typeof sessionSchema>

export function messageText(message: UIMessage) {
  return message.parts
    .map((part) => (part.type === 'text' ? part.text : ''))
    .join('')
    .trim()
}

export function sessionTitle(messages: UIMessage[]) {
  const first = messages.find((message) => message.role === 'user')
  const text = first ? messageText(first) : ''
  return text.length > 56 ? `${text.slice(0, 56).trimEnd()}…` : text || 'New chat'
}
