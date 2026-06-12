// Thin client for the FastAPI backend (proxied at /api in dev via vite.config.ts).

export interface KataMeta {
  id: string
  slug: string
  title: string
  blurb: string
}

export interface KataDetail extends KataMeta {
  concept_md: string
  task_md: string
  starter_code: string
  solution_code: string
  sample_prompts: string[]
  chat_symbol: string
  chattable: boolean
  needs_key_for_chat: boolean
}

export interface CheckResult {
  label: string
  passed: boolean
  detail: string
}

export interface CheckResponse {
  ok: boolean
  error: string | null
  results: CheckResult[]
}

export interface ChatResponse {
  ok: boolean
  error?: string
  needs_key?: boolean
  text?: string
  tool_calls?: string[]
  tool_args?: Record<string, unknown>[]
  transfers?: string[]
  author_path?: string[]
  state?: Record<string, unknown>
}

export interface Health {
  ok: boolean
  has_api_key: boolean
  adk_version: string
  kata_count: number
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const api = {
  health: () => fetch("/api/health").then(json<Health>),
  listKatas: () => fetch("/api/katas").then(json<KataMeta[]>),
  getKata: (slug: string) => fetch(`/api/katas/${slug}`).then(json<KataDetail>),
  check: (slug: string, code: string) =>
    fetch(`/api/katas/${slug}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    }).then(json<CheckResponse>),
  chat: (slug: string, code: string, prompt: string) =>
    fetch(`/api/katas/${slug}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, prompt }),
    }).then(json<ChatResponse>),
}
