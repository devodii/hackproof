import posthog from 'posthog-js'

const key = import.meta.env.VITE_POSTHOG_KEY

if (key) {
  posthog.init(key, {
    api_host: import.meta.env.VITE_POSTHOG_HOST ?? 'https://us.i.posthog.com',
    defaults: '2025-05-24',
    person_profiles: 'identified_only',
  })
}

export { posthog }
