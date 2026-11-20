import { Link } from 'react-router'

import stellarDark from '@/assets/stellar.gif'
import stellarLight from '@/assets/stellar-light.gif'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-background px-6 text-center text-foreground">
      <img src={stellarLight} alt="" className="w-72 rounded-2xl dark:hidden" />
      <img src={stellarDark} alt="" className="hidden w-72 rounded-2xl dark:block" />
      <div className="flex flex-col gap-2">
        <h1 className="text-6xl leading-none">404</h1>
        <p className="text-muted-foreground">There is nothing here.</p>
      </div>
      <Button render={<Link to="/" />}>Back home</Button>
    </div>
  )
}
