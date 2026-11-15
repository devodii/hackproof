import onDark from '@/assets/hackmeridian-light.png'
import onLight from '@/assets/hackmeridian-dark.png'
import { EVENT_NAME, EVENT_URL } from '@/lib/config'
import { cn } from '@/lib/utils'

export function EventLogo({ className }: { className?: string }) {
  return (
    <a
      href={EVENT_URL}
      target="_blank"
      rel="noreferrer"
      aria-label={EVENT_NAME}
      className="shrink-0"
    >
      <img src={onLight} alt="" className={cn('dark:hidden', className)} />
      <img src={onDark} alt="" className={cn('hidden dark:block', className)} />
    </a>
  )
}
