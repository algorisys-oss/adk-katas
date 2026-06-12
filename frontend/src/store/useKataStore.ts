import { create } from "zustand"
import { persist } from "zustand/middleware"
import { api, type Health, type KataMeta } from "@/lib/api"

export type KataStatus = "todo" | "passed"

interface KataState {
  // server data
  katas: KataMeta[]
  health: Health | null
  loaded: boolean
  // per-kata learner state (persisted)
  codeBySlug: Record<string, string>
  statusBySlug: Record<string, KataStatus>
  // actions
  init: () => Promise<void>
  setCode: (slug: string, code: string) => void
  getCode: (slug: string, fallback: string) => string
  markStatus: (slug: string, status: KataStatus) => void
  resetCode: (slug: string) => void
}

export const useKataStore = create<KataState>()(
  persist(
    (set, get) => ({
      katas: [],
      health: null,
      loaded: false,
      codeBySlug: {},
      statusBySlug: {},

      init: async () => {
        const [katas, health] = await Promise.all([
          api.listKatas().catch(() => [] as KataMeta[]),
          api.health().catch(() => null),
        ])
        set({ katas, health, loaded: true })
      },

      setCode: (slug, code) =>
        set((s) => ({ codeBySlug: { ...s.codeBySlug, [slug]: code } })),

      getCode: (slug, fallback) => get().codeBySlug[slug] ?? fallback,

      markStatus: (slug, status) =>
        set((s) => ({ statusBySlug: { ...s.statusBySlug, [slug]: status } })),

      resetCode: (slug) =>
        set((s) => {
          const next = { ...s.codeBySlug }
          delete next[slug]
          return { codeBySlug: next }
        }),
    }),
    {
      name: "adk-katas",
      // Only persist the learner's work, not server data.
      partialize: (s) => ({
        codeBySlug: s.codeBySlug,
        statusBySlug: s.statusBySlug,
      }),
    }
  )
)
