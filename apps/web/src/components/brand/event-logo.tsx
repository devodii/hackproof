import { useHackathon } from '@/hooks/use-hackathon'
import { cn } from '@/lib/utils'

const logos = import.meta.glob<string>('@/assets/logos/*.png', {
  eager: true,
  import: 'default',
})

export function EventLogo({ className }: { className?: string }) {
  const { slug, name, website } = useHackathon()
  const onDark = logos[`/src/assets/logos/${slug}-light.png`]
  const onLight = logos[`/src/assets/logos/${slug}-dark.png`]
  if (!onDark || !onLight) return null

  return (
    <a
      href={website ?? undefined}
      target="_blank"
      rel="noreferrer"
      aria-label={name}
      className="shrink-0"
    >
      <img src={onLight} alt="" className={cn('dark:hidden', className)} />
      <img src={onDark} alt="" className={cn('hidden dark:block', className)} />
    </a>
  )
}
