import { ArrowLeftIcon } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router'

import { Button } from '@/components/ui/button'

export function BackButton() {
  const location = useLocation()
  const navigate = useNavigate()

  if (location.key !== 'default') {
    return (
      <Button variant="ghost" size="sm" className="-ml-2.5" onClick={() => navigate(-1)}>
        <ArrowLeftIcon /> Back
      </Button>
    )
  }
  return (
    <Button variant="ghost" size="sm" className="-ml-2.5" render={<Link to="/" />}>
      <ArrowLeftIcon /> All projects
    </Button>
  )
}
