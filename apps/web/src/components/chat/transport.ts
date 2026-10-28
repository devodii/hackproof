import { DefaultChatTransport } from 'ai'
import { z } from 'zod'

import { currentPage } from '@/components/chat/page'
import { API_URL } from '@/lib/config'

const rateLimitBody = z.object({
  window: z.enum(['minute', 'hour']),
  limit: z.number(),
  retryAfter: z.number(),
})

export class RateLimitError extends Error {
  readonly window: 'minute' | 'hour'
  readonly limit: number
  readonly retryAfter: number

  constructor(body: z.infer<typeof rateLimitBody>) {
    super('rate_limited')
    this.window = body.window
    this.limit = body.limit
    this.retryAfter = body.retryAfter
  }
}

export class UnavailableError extends Error {
  constructor() {
    super('chat_unavailable')
  }
}

export const transport = new DefaultChatTransport({
  api: `${API_URL}/api/chat`,
  fetch: async (input, init) => {
    const response = await fetch(input, init)
    if (response.status === 429)
      throw new RateLimitError(rateLimitBody.parse(await response.json()))
    if (response.status === 503) throw new UnavailableError()
    return response
  },
  prepareSendMessagesRequest: ({ messages }) => ({
    body: {
      page: currentPage(),
      messages: messages.map((message) => ({
        role: message.role,
        parts: message.parts.filter((part) => part.type === 'text'),
      })),
    },
  }),
})
