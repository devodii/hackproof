import { ChevronDownIcon } from 'lucide-react'
import { type ReactNode, useEffect, useRef, useState } from 'react'

import { Spinner } from '@/components/spinner'
import { Button } from '@/components/ui/button'

interface ScrollBoxProps {
  hasMore: boolean
  loading: boolean
  onMore: () => void
  children: ReactNode
}

const EDGE = 8
const SWIPE = 24
const JUMP_MS = 900
const PAGE_FRACTION = 0.8

export function ScrollBox({ hasMore, loading, onMore, children }: ScrollBoxProps) {
  const box = useRef<HTMLDivElement>(null)
  const end = useRef<HTMLDivElement>(null)
  const more = useRef(onMore)
  more.current = onMore
  const [below, setBelow] = useState(false)

  useEffect(() => {
    if (!hasMore || loading || !end.current) return
    const watcher = new IntersectionObserver(([entry]) => entry.isIntersecting && more.current(), {
      root: box.current,
      rootMargin: '200px',
    })
    watcher.observe(end.current)
    return () => watcher.disconnect()
  }, [hasMore, loading])

  const measure = () => {
    const el = box.current
    if (el) setBelow(el.scrollHeight - el.scrollTop - el.clientHeight > EDGE)
  }

  useEffect(measure)

  const touchY = useRef(0)
  const lockedUntil = useRef(0)

  const release = (direction: 1 | -1) => {
    const el = box.current
    if (!el || el.scrollHeight <= el.clientHeight + EDGE || Date.now() < lockedUntil.current) return
    const atEnd = !hasMore && el.scrollHeight - el.scrollTop - el.clientHeight <= EDGE
    const atStart = el.scrollTop <= EDGE
    if (direction > 0 ? !atEnd : !atStart) return
    lockedUntil.current = Date.now() + JUMP_MS
    document.getElementById(direction > 0 ? 'about' : 'overview')?.scrollIntoView({
      behavior: 'smooth',
    })
  }

  return (
    <div className="relative">
      <div
        ref={box}
        onScroll={measure}
        onWheel={(event) => event.deltaY !== 0 && release(event.deltaY > 0 ? 1 : -1)}
        onTouchStart={(event) => {
          touchY.current = event.touches[0].clientY
        }}
        onTouchMove={(event) => {
          const moved = touchY.current - event.touches[0].clientY
          if (Math.abs(moved) > SWIPE) release(moved > 0 ? 1 : -1)
        }}
        className="max-h-[70svh] overflow-y-auto p-1.5 pr-3"
      >
        {children}
        <div ref={end} className="flex h-10 items-center justify-center">
          {loading && <Spinner />}
        </div>
      </div>
      {(below || hasMore) && (
        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex h-16 items-end justify-center bg-linear-to-t from-background to-transparent pb-1">
          <Button
            type="button"
            variant="outline"
            size="icon"
            aria-label="Show more"
            className="pointer-events-auto size-11 rounded-full bg-background"
            onClick={() =>
              box.current?.scrollBy({
                top: box.current.clientHeight * PAGE_FRACTION,
                behavior: 'smooth',
              })
            }
          >
            <ChevronDownIcon className="size-5 animate-bounce text-muted-foreground" />
          </Button>
        </div>
      )}
    </div>
  )
}
