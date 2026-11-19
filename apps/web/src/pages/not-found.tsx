import { Link } from 'react-router'

import lost from '@/assets/lost.gif'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-background px-6 text-center text-foreground">
      <img src={lost} alt="" className="w-72 rounded-2xl" />
      <div className="flex flex-col gap-2">
        <h1 className="text-6xl leading-none">404</h1>
        <p className="text-muted-foreground">There is nothing here.</p>
      </div>
      <Button render={<Link to="/" />}>Back home</Button>
    </div>
  )
}
