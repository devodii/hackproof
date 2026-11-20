export function Backdrop() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -top-60 -left-40 size-glow rounded-full bg-glow-secondary blur-glow" />
      <div className="absolute -right-48 -bottom-72 size-glow-lg rounded-full bg-glow-primary blur-glow-lg" />
      <div className="poster-dots absolute inset-0" />
    </div>
  )
}
