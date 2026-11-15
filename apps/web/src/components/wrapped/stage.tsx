import { type ReactNode, useLayoutEffect, useState } from 'react'

import { StillContext } from '@/components/wrapped/use-still'

export const STAGE_WIDTH = 1600
export const STAGE_HEIGHT = 900

function fitScale() {
  return Math.min(window.innerWidth / STAGE_WIDTH, window.innerHeight / STAGE_HEIGHT)
}

export function Stage({ still, children }: { still: boolean; children: ReactNode }) {
  const [scale, setScale] = useState(fitScale)

  useLayoutEffect(() => {
    const resize = () => setScale(fitScale())
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  return (
    <StillContext value={still}>
      <div className="dark fixed inset-0 grid place-items-center overflow-hidden bg-poster">
        <div
          className="relative shrink-0 overflow-hidden bg-background text-foreground"
          style={{ width: STAGE_WIDTH, height: STAGE_HEIGHT, transform: `scale(${scale})` }}
        >
          {children}
        </div>
      </div>
    </StillContext>
  )
}
