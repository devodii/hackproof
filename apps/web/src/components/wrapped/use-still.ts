import { createContext, useContext } from 'react'

export const StillContext = createContext(false)

export function useStill() {
  return useContext(StillContext)
}
