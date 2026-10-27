import methodology from '../../../../docs/METHODOLOGY.md?raw'

import { Markdown } from '@/components/markdown'

export function MethodologyPage() {
  return (
    <article className="mx-auto max-w-3xl">
      <Markdown>{methodology}</Markdown>
    </article>
  )
}
