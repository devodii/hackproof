const EXPERT = 'https://stellar.expert/explorer/testnet'
const GITHUB = 'https://github.com'

export const expertUrl = {
  contract: (id: string) => `${EXPERT}/contract/${id}`,
  account: (address: string) => `${EXPERT}/account/${address}`,
  tx: (hash: string) => `${EXPERT}/tx/${hash}`,
  ledger: (sequence: number) => `${EXPERT}/ledger/${sequence}`,
  asset: (asset: string) => `${EXPERT}/asset/${asset.replace(':', '-')}`,
}

export const githubUrl = {
  repo: (fullName: string) => `${GITHUB}/${fullName}`,
  profile: (login: string) => `${GITHUB}/${login}`,
  file: (fullName: string, path: string) => `${GITHUB}/${fullName}/blob/HEAD/${path}`,
  commits: (fullName: string, window: { start: string; end: string }) =>
    `${GITHUB}/${fullName}/commits/HEAD?since=${encodeURIComponent(window.start)}&until=${encodeURIComponent(window.end)}`,
}
