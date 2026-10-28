import * as React from 'react'
import type { z } from 'zod'

export const useLocalStorageState = <T>(
  key: string,
  defaultState: T | undefined,
  schema: z.ZodType<T>,
): [T | undefined, (newState: T | undefined) => void] => {
  const [state, setState] = React.useState<T | undefined>(() => {
    if (typeof window === 'undefined') return defaultState
    try {
      const stored = localStorage.getItem(key)
      if (!stored) return defaultState
      const parsed = schema.safeParse(JSON.parse(stored))
      if (parsed.success) return parsed.data
      localStorage.removeItem(key)
      return defaultState
    } catch (e) {
      console.warn(`Error reading ${key} from localStorage:`, e)
      return defaultState
    }
  })

  const setLocalStorageState = React.useCallback(
    (newState: T | undefined) => {
      const changed = state !== newState
      if (!changed) return
      setState(newState as T)
      try {
        if (newState === undefined) localStorage.removeItem(key)
        else localStorage.setItem(key, JSON.stringify(newState))
      } catch (e) {
        console.warn(`Error writing ${key} to localStorage:`, e)
      }
    },
    [state, key],
  )

  return [state, setLocalStorageState]
}
