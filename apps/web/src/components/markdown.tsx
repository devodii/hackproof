import type { ComponentProps } from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const components: Components = {
  h1: (props) => <h1 className="mb-6 text-4xl font-semibold tracking-tight" {...props} />,
  h2: (props) => <h2 className="mt-10 mb-3 text-2xl font-semibold tracking-tight" {...props} />,
  p: (props) => <p className="my-3 leading-7 text-muted-foreground" {...props} />,
  ul: (props) => <ul className="my-3 ml-6 list-disc space-y-2 text-muted-foreground" {...props} />,
  a: (props) => <a className="underline underline-offset-4" {...props} />,
  strong: (props) => <strong className="font-medium text-foreground" {...props} />,
  code: (props) => <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm" {...props} />,
  pre: (props) => (
    <pre
      className="my-4 overflow-x-auto rounded-lg border bg-muted p-4 font-mono text-sm"
      {...props}
    />
  ),
  table: (props) => (
    <div className="my-4 overflow-x-auto rounded-lg border">
      <Table {...(props as ComponentProps<typeof Table>)} />
    </div>
  ),
  thead: (props) => <TableHeader {...(props as ComponentProps<typeof TableHeader>)} />,
  tbody: (props) => <TableBody {...(props as ComponentProps<typeof TableBody>)} />,
  tr: (props) => <TableRow {...(props as ComponentProps<typeof TableRow>)} />,
  th: (props) => <TableHead {...(props as ComponentProps<typeof TableHead>)} />,
  td: (props) => <TableCell {...(props as ComponentProps<typeof TableCell>)} />,
}

export function Markdown({ children }: { children: string }) {
  return <ReactMarkdown components={components}>{children}</ReactMarkdown>
}
