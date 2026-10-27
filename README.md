# hackproof

HackMeridian submissions rebuilt from Stellar testnet: every contract deployed, wasm uploaded and failed transaction in the hack window, linked back to the repos that produced them.

## Layout

- `apps/web`: React, Vite and shadcn/ui
- `apps/api`: FastAPI, managed with uv

## Development

```sh
pnpm install
pnpm dev:api
pnpm dev:web
```
