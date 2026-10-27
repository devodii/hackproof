import type { ReactNode } from 'react'

import odii from '@/assets/odii.jpg'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { AUTHOR_LINKS } from '@/lib/config'

function Outbound({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-foreground underline underline-offset-4"
    >
      {children}
    </a>
  )
}

export function About() {
  return (
    <section className="border-t">
      <div className="mx-auto flex w-full max-w-6xl flex-col items-start gap-6 px-6 py-16 sm:flex-row sm:items-center">
        <Avatar className="size-28 shrink-0">
          <AvatarImage src={odii} alt="Odii" />
          <AvatarFallback>O</AvatarFallback>
        </Avatar>
        <p className="max-w-2xl text-lg leading-relaxed text-muted-foreground">
          Hey curious, I'm Odii. A super talented builder passionate about Stellar, I've worked on
          projects such as <Outbound href={AUTHOR_LINKS.sorokit}>sorokit</Outbound>,{' '}
          <Outbound href={AUTHOR_LINKS.stellarTools}>StellarTools</Outbound> and many more, feel
          free to follow me on <Outbound href={AUTHOR_LINKS.x}>X</Outbound> &amp;{' '}
          <Outbound href={AUTHOR_LINKS.linkedin}>LinkedIn</Outbound>.
        </p>
      </div>
    </section>
  )
}
