export function Bar({ value, max }: { value: number; max: number }) {
  const width = max > 0 ? Math.round((value / max) * 100) : 0

  return (
    <div className="h-1.5 w-full rounded-full bg-secondary">
      <div className="h-full rounded-full bg-primary" style={{ width: `${width}%` }} />
    </div>
  )
}
