import { cn } from '@/lib/utils'
import onDark from '@/assets/hackmeridian-light.png'
import onLight from '@/assets/hackmeridian-dark.png'
import { EVENT_NAME } from '@/lib/config'

export function EventLogo({ className }: { className?: string }) {
  return (
    <>
      <img src={onLight} alt={EVENT_NAME} className={cn('dark:hidden', className)} />
      <img src={onDark} alt={EVENT_NAME} className={cn('hidden dark:block', className)} />
    </>
  )
}
