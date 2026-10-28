import { ArrowUpIcon, SquareIcon } from 'lucide-react'
import { type KeyboardEvent, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'

interface PromptBoxProps {
  onSubmit: (text: string) => void
  placeholder: string
  disabled?: boolean
  busy?: boolean
  onStop?: () => void
  autoFocus?: boolean
  className?: string
}

export function PromptBox({
  onSubmit,
  placeholder,
  disabled = false,
  busy = false,
  onStop,
  autoFocus = false,
  className,
}: PromptBoxProps) {
  const [value, setValue] = useState('')
  const text = value.trim()

  function submit() {
    if (!text || disabled || busy) return
    onSubmit(text)
    setValue('')
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        submit()
      }}
      className={cn(
        'flex items-end gap-2 rounded-3xl border bg-card p-2 pl-4 transition-shadow focus-within:ring-3 focus-within:ring-ring/30',
        className,
      )}
    >
      <Textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
        rows={1}
        aria-label={placeholder}
        className="max-h-32 min-h-0 flex-1 resize-none border-0 bg-transparent px-0 py-1.5 text-base shadow-none focus-visible:ring-0 dark:bg-transparent"
      />
      {busy ? (
        <Button
          type="button"
          size="icon"
          className="rounded-full"
          onClick={onStop}
          aria-label="Stop generating"
        >
          <SquareIcon className="fill-current" />
        </Button>
      ) : (
        <Button
          type="submit"
          size="icon"
          className="rounded-full"
          disabled={!text || disabled}
          aria-label="Send message"
        >
          <ArrowUpIcon />
        </Button>
      )}
    </form>
  )
}
