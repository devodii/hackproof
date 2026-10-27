import type { StellarWalletsKit } from '@creit.tech/stellar-wallets-kit'

let kit: Promise<typeof StellarWalletsKit> | undefined

async function loadKit() {
  const [{ StellarWalletsKit }, { defaultModules }] = await Promise.all([
    import('@creit.tech/stellar-wallets-kit'),
    import('@creit.tech/stellar-wallets-kit/modules/utils'),
  ])
  StellarWalletsKit.init({ modules: defaultModules() })
  return StellarWalletsKit
}

const getKit = () => (kit ??= loadKit())

export async function connectWallet() {
  const { address } = await (await getKit()).authModal()
  return address
}

export async function signMessage(message: string, address: string) {
  const { signedMessage } = await (await getKit()).signMessage(message, { address })
  return signedMessage
}
