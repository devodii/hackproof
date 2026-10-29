import { type ReactNode, useEffect, useRef } from 'react'

import { Spinner } from '@/components/spinner'

interface ScrollBoxProps {
  hasMore: boolean
  loading: boolean
  onMore: () => void
  children: ReactNode
}

export function ScrollBox({ hasMore, loading, onMore, children }: ScrollBoxProps) {
  const box = useRef<HTMLDivElement>(null)
  const end = useRef<HTMLDivElement>(null)
  const more = useRef(onMore)
  more.current = onMore

  useEffect(() => {
    if (!hasMore || loading || !end.current) return
    const watcher = new IntersectionObserver(([entry]) => entry.isIntersecting && more.current(), {
      root: box.current,
      rootMargin: '200px',
    })
    watcher.observe(end.current)
    return () => watcher.disconnect()
  }, [hasMore, loading])

  return (
    <div ref={box} className="max-h-[70svh] overflow-y-auto overscroll-contain pr-1">
      {children}
      <div ref={end} className="flex h-10 items-center justify-center">
        {loading && <Spinner />}
      </div>
    </div>
  )
}
