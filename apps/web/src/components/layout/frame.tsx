import type * as React from 'react'

import { Backdrop } from '@/components/wrapped/backdrop'
import { SiteFooter } from '@/components/layout/site-footer'
import { SiteHeader } from '@/components/layout/site-header'

export function Frame({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative isolate flex min-h-svh flex-col bg-background text-foreground">
      <Backdrop />
      <SiteHeader />
      <main className="relative mx-auto w-full max-w-6xl flex-1 px-6 py-12">{children}</main>
      <SiteFooter />
    </div>
  )
}
