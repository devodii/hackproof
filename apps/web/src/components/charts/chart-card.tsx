import type { ReactNode } from 'react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface ChartCardProps {
  title: string
  description: string
  headers: [string, string]
  rows: [string, number][]
  children: ReactNode
}

export function ChartCard({ title, description, headers, rows, children }: ChartCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {children}
        {rows.length > 0 && (
          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground">Table view</summary>
            <Table className="mt-2">
              <TableHeader>
                <TableRow>
                  <TableHead>{headers[0]}</TableHead>
                  <TableHead className="text-right">{headers[1]}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map(([label, value]) => (
                  <TableRow key={label}>
                    <TableCell>{label}</TableCell>
                    <TableCell className="text-right tabular-nums">{value}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </details>
        )}
      </CardContent>
    </Card>
  )
}
