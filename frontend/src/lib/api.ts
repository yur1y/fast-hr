import axios from 'axios'
import { QueryClient } from '@tanstack/react-query'

export const api = axios.create({
  baseURL: '/',
})

export const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

typeof document !== 'undefined' &&
  api.interceptors.request.use((config) => {
    const params = new URLSearchParams(window.location.search)
    const provider = params.get('llm_provider') || params.get('LLM_PROVIDER')
    if (provider) {
      config.headers = config.headers ?? {}
      config.headers['X-LLM-Provider'] = provider
    }
    return config
  })
