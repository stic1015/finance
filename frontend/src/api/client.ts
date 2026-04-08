const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Envelope<T> = { data: T }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  const payload = (await response.json()) as Envelope<T>
  return payload.data
}

export function apiGet<T>(path: string) {
  return request<T>(path)
}

export function apiPost<T>(path: string, body: unknown) {
  return request<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function getWsBaseUrl() {
  return import.meta.env.VITE_WS_BASE_URL ?? API_BASE_URL.replace(/^http/, 'ws')
}
