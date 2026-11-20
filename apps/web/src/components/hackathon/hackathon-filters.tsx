import { SearchIcon, XIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  DEFAULT_FILTERS,
  SORTS,
  STATUS_FILTERS,
  type HackathonFilters,
  type Sort,
  type StatusFilter,
} from '@/lib/hackathons'

interface Props {
  filters: HackathonFilters
  years: string[]
  onChange: (next: HackathonFilters) => void
}

export function HackathonFilterBar({ filters, years, onChange }: Props) {
  const dirty = JSON.stringify(filters) !== JSON.stringify(DEFAULT_FILTERS)
  const set = (patch: Partial<HackathonFilters>) => onChange({ ...filters, ...patch })

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={filters.q}
            onChange={(event) => set({ q: event.target.value })}
            placeholder="Search by name, city or topic"
            aria-label="Search hackathons"
            className="pl-8"
          />
        </div>
        <Tabs
          value={filters.status}
          onValueChange={(value) => set({ status: value as StatusFilter })}
        >
          <TabsList>
            {STATUS_FILTERS.map((item) => (
              <TabsTrigger key={item.value} value={item.value}>
                {item.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>
      <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
        {years.length > 1 && (
          <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Year">
            {years.map((year) => (
              <Button
                key={year}
                size="sm"
                variant={filters.year === year ? 'default' : 'outline'}
                className="rounded-full"
                onClick={() => set({ year: filters.year === year ? '' : year })}
              >
                {year}
              </Button>
            ))}
          </div>
        )}
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={filters.indexedOnly}
            onCheckedChange={(checked) => set({ indexedOnly: checked === true })}
          />
          With indexed projects only
        </label>
        <div className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
          Sort
          <Select value={filters.sort} onValueChange={(value) => set({ sort: value as Sort })}>
            <SelectTrigger aria-label="Sort hackathons">
              <SelectValue>{SORTS.find((item) => item.value === filters.sort)?.label}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {SORTS.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {dirty && (
          <Button size="sm" variant="ghost" onClick={() => onChange(DEFAULT_FILTERS)}>
            <XIcon /> Clear
          </Button>
        )}
      </div>
    </div>
  )
}
