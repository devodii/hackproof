import { ChevronDownIcon } from 'lucide-react'
import { type ReactNode, useEffect, useRef, useState } from 'react'

import { Spinner } from '@/components/spinner'

interface ScrollBoxProps {
  hasMore: boolean
  loading: boolean
  onMore: () => void
  children: ReactNode
}

const EDGE = 8
const SWIPE = 24

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

  const release = () => {
    const el = box.current
    if (!el || hasMore || el.scrollHeight - el.scrollTop - el.clientHeight > EDGE) return
    document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="relative">
      <div
        ref={box}
        onScroll={measure}
        onWheel={(event) => event.deltaY > 0 && release()}
        onTouchStart={(event) => {
          touchY.current = event.touches[0].clientY
        }}
        onTouchMove={(event) => touchY.current - event.touches[0].clientY > SWIPE && release()}
        className="max-h-[70svh] overflow-y-auto p-1.5 pr-3"
      >
        {children}
        <div ref={end} className="flex h-10 items-center justify-center">
          {loading && <Spinner />}
        </div>
      </div>
      {(below || hasMore) && (
        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex h-14 items-end justify-center bg-gradient-to-t from-background to-transparent pb-1">
          <ChevronDownIcon className="size-5 animate-bounce text-muted-foreground" />
        </div>
      )}
    </div>
  )
}
