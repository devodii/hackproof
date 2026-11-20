import { GlobeIcon } from 'lucide-react'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useLanguage } from '@/hooks/use-language'
import {
  LANGUAGES,
  languageName,
  REGION_LABEL,
  type Region,
  SOURCE_LANGUAGE,
} from '@/lib/languages'
import { cn } from '@/lib/utils'

const REGIONS = Object.keys(REGION_LABEL) as Region[]

export function LanguageMenu() {
  const { code, select } = useLanguage()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        translate="no"
        className="inline-flex items-center gap-1.5 outline-none hover:text-foreground"
      >
        <GlobeIcon className="size-3.5" /> {languageName(code)}
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" side="top" className="max-h-96 min-w-56 overflow-auto">
        <DropdownMenuItem translate="no" onClick={() => select(SOURCE_LANGUAGE)}>
          English
        </DropdownMenuItem>
        {REGIONS.map((region) => (
          <DropdownMenuGroup key={region}>
            <DropdownMenuSeparator />
            <DropdownMenuLabel>{REGION_LABEL[region]}</DropdownMenuLabel>
            {LANGUAGES.filter((language) => language.region === region).map((language) => (
              <DropdownMenuItem
                key={language.code}
                translate="no"
                className={cn(language.code === code && 'text-primary')}
                onClick={() => select(language.code)}
              >
                {language.name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuGroup>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
