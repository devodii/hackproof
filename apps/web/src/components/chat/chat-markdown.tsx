import { Link } from 'react-router'
import ReactMarkdown, { type Components } from 'react-markdown'

import { useChatPanel } from '@/components/chat/use-chat-panel'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

function ChatLink({ href = '', children }: { href?: string; children?: React.ReactNode }) {
  const { close } = useChatPanel()
  const className = 'font-medium underline underline-offset-4 break-words'

  if (href.startsWith('/')) {
    return (
      <Link to={href} onClick={close} className={className}>
        {children}
      </Link>
    )
  }
  return (
    <a href={href} target="_blank" rel="noreferrer" className={className}>
      {children}
    </a>
  )
}

const components: Components = {
  p: (props) => <p className="my-2 leading-6 first:mt-0 last:mb-0" {...props} />,
  ul: (props) => <ul className="my-2 ml-5 list-disc space-y-1" {...props} />,
  ol: (props) => <ol className="my-2 ml-5 list-decimal space-y-1" {...props} />,
  h1: (props) => <h3 className="mt-4 mb-1 text-xl" {...props} />,
  h2: (props) => <h3 className="mt-4 mb-1 text-xl" {...props} />,
  h3: (props) => <h3 className="mt-3 mb-1 text-lg" {...props} />,
  a: ChatLink,
  strong: (props) => <strong className="font-semibold" {...props} />,
  code: (props) => (
    <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]" {...props} />
  ),
  pre: (props) => (
    <pre
      className="my-2 overflow-x-auto rounded-lg border bg-muted p-3 font-mono text-xs"
      {...props}
    />
  ),
  table: (props) => (
    <div className="my-2 overflow-x-auto rounded-lg border">
      <Table {...(props as React.ComponentProps<typeof Table>)} />
    </div>
  ),
  thead: (props) => <TableHeader {...(props as React.ComponentProps<typeof TableHeader>)} />,
  tbody: (props) => <TableBody {...(props as React.ComponentProps<typeof TableBody>)} />,
  tr: (props) => <TableRow {...(props as React.ComponentProps<typeof TableRow>)} />,
  th: (props) => <TableHead {...(props as React.ComponentProps<typeof TableHead>)} />,
  td: (props) => <TableCell {...(props as React.ComponentProps<typeof TableCell>)} />,
}

export function ChatMarkdown({ children }: { children: string }) {
  return <ReactMarkdown components={components}>{children}</ReactMarkdown>
}
