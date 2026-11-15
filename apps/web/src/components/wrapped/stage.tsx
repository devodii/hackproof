import { type ReactNode, createContext, useContext, useLayoutEffect, useRef, useState } from 'react'

export const STAGE_WIDTH = 1600
export const STAGE_HEIGHT = 900

const StillContext = createContext(false)

export function useStill() {
  return useContext(StillContext)
}

function fitScale() {
  return Math.min(window.innerWidth / STAGE_WIDTH, window.innerHeight / STAGE_HEIGHT)
}

export function Stage({ still, children }: { still: boolean; children: ReactNode }) {
  const [scale, setScale] = useState(fitScale)
  const frame = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const resize = () => setScale(fitScale())
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  return (
    <StillContext value={still}>
      <div
        ref={frame}
        className="dark fixed inset-0 grid place-items-center overflow-hidden bg-[#070707]"
      >
        <div
          className="relative shrink-0 overflow-hidden bg-background text-foreground"
          style={{
            width: STAGE_WIDTH,
            height: STAGE_HEIGHT,
            transform: `scale(${scale})`,
          }}
        >
          {children}
        </div>
      </div>
    </StillContext>
  )
}
