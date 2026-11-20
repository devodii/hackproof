import { LANGUAGES, SOURCE_LANGUAGE } from '@/lib/languages'

const COOKIE = 'googtrans'
const CONTAINER = 'google_translate_element'
const CALLBACK = 'googleTranslateReady'
const SCRIPT = `https://translate.google.com/translate_a/element.js?cb=${CALLBACK}`

interface TranslateElementOptions {
  pageLanguage: string
  includedLanguages: string
  autoDisplay: boolean
}

declare global {
  interface Window {
    [CALLBACK]?: () => void
    google?: {
      translate: { TranslateElement: new (options: TranslateElementOptions, id: string) => void }
    }
  }
}

let loading: Promise<void> | null = null

export function rememberLanguage(code: string) {
  document.cookie =
    code === SOURCE_LANGUAGE
      ? `${COOKIE}=; path=/; max-age=0`
      : `${COOKIE}=/${SOURCE_LANGUAGE}/${code}; path=/; max-age=31536000`
}

function keepReactAndGoogleApart() {
  const { removeChild, insertBefore } = Node.prototype
  Node.prototype.removeChild = function <T extends Node>(this: Node, child: T): T {
    return child.parentNode === this ? (removeChild.call(this, child) as T) : child
  }
  Node.prototype.insertBefore = function <T extends Node>(
    this: Node,
    node: T,
    reference: Node | null,
  ): T {
    return reference && reference.parentNode !== this
      ? (insertBefore.call(this, node, null) as T)
      : (insertBefore.call(this, node, reference) as T)
  }
}

export function loadTranslator(): Promise<void> {
  loading ??= new Promise((resolve) => {
    keepReactAndGoogleApart()
    window[CALLBACK] = () => {
      new window.google!.translate.TranslateElement(
        {
          pageLanguage: SOURCE_LANGUAGE,
          includedLanguages: LANGUAGES.map((language) => language.code).join(','),
          autoDisplay: false,
        },
        CONTAINER,
      )
      resolve()
    }
    const script = document.createElement('script')
    script.src = SCRIPT
    script.async = true
    document.head.append(script)
  })
  return loading
}

function restoreOriginal(): boolean {
  const frame = document.querySelector<HTMLIFrameElement>('iframe.skiptranslate')
  const restore = frame?.contentDocument?.querySelector<HTMLElement>('[id$="restore"]')
  if (!restore) return false
  restore.click()
  return true
}

export function translateTo(code: string): boolean {
  if (code === SOURCE_LANGUAGE) return restoreOriginal()
  const combo = document.querySelector<HTMLSelectElement>('select.goog-te-combo')
  if (!combo) return false
  combo.value = code
  combo.dispatchEvent(new Event('change'))
  return true
}

export const TRANSLATOR_CONTAINER = CONTAINER
