import { QueryClientProvider } from '@tanstack/react-query'
import { Analytics } from '@vercel/analytics/react'
import { ThemeProvider } from 'next-themes'
import { PostHogProvider } from 'posthog-js/react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'

import { TooltipProvider } from '@/components/ui/tooltip'

import { App } from './app'
import { posthog } from './lib/analytics'
import { createQueryClient } from './lib/query-client'
import './index.css'

const queryClient = createQueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PostHogProvider client={posthog}>
      <ThemeProvider attribute="class" defaultTheme="dark" disableTransitionOnChange>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
            <Analytics />
          </TooltipProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </PostHogProvider>
  </StrictMode>,
)
