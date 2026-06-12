import { useState } from "react"
import { Loader2, Send, Wrench, ArrowRightLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { api, type KataDetail } from "@/lib/api"
import { useKataStore } from "@/store/useKataStore"

interface Turn {
  role: "user" | "agent" | "system"
  text: string
  tools?: string[]
  transfers?: string[]
  state?: Record<string, unknown>
}

export function ChatPanel({ kata, code }: { kata: KataDetail; code: string }) {
  const [turns, setTurns] = useState<Turn[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const hasKey = useKataStore((s) => s.health?.has_api_key)

  if (!kata.chattable) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        This kata has no chat agent — the goal is to make the <strong>checks</strong> pass. 🎯
      </div>
    )
  }

  async function send(prompt: string) {
    if (!prompt.trim() || busy) return
    setInput("")
    setTurns((t) => [...t, { role: "user", text: prompt }])
    setBusy(true)
    try {
      const res = await api.chat(kata.slug, code, prompt)
      if (res.ok) {
        setTurns((t) => [
          ...t,
          {
            role: "agent",
            text: res.text || "(no text response)",
            tools: res.tool_calls,
            transfers: res.transfers,
            state: res.state,
          },
        ])
      } else if (res.needs_key) {
        setTurns((t) => [...t, { role: "system", text: "⚠️ No GOOGLE_API_KEY on the backend. Add it to the .env and restart the server." }])
      } else {
        const msg = (res.error || "").includes("RESOURCE_EXHAUSTED")
          ? "⏳ Gemini free-tier quota hit (429). Wait a minute and try again."
          : `❌ ${res.error}`
        setTurns((t) => [...t, { role: "system", text: msg }])
      }
    } catch (e) {
      setTurns((t) => [...t, { role: "system", text: `❌ ${e}` }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b p-3 text-sm">
        <span className="font-medium">Live chat</span>
        <Badge variant="secondary" className="font-mono text-xs">{kata.chat_symbol}</Badge>
        {hasKey === false && (
          <span className="ml-auto text-xs text-muted-foreground">no API key — runs will be skipped</span>
        )}
      </div>

      <div className="flex-1 space-y-3 overflow-auto p-3">
        {turns.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Run your agent live. Each send starts a fresh single-turn session.
            </p>
            <div className="flex flex-wrap gap-2">
              {kata.sample_prompts.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="rounded-full border px-3 py-1 text-xs hover:bg-accent"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {turns.map((t, i) => (
          <div key={i} className={t.role === "user" ? "text-right" : ""}>
            <div
              className={
                "inline-block max-w-[85%] rounded-lg px-3 py-2 text-sm " +
                (t.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : t.role === "system"
                    ? "bg-muted text-muted-foreground"
                    : "bg-secondary text-secondary-foreground")
              }
            >
              <div className="whitespace-pre-wrap text-left">{t.text}</div>
              {(t.tools?.length || t.transfers?.length) ? (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {t.transfers?.map((x, j) => (
                    <Badge key={`x${j}`} variant="outline" className="gap-1 text-xs">
                      <ArrowRightLeft className="size-3" /> {x}
                    </Badge>
                  ))}
                  {t.tools?.map((x, j) => (
                    <Badge key={`t${j}`} variant="outline" className="gap-1 text-xs">
                      <Wrench className="size-3" /> {x}
                    </Badge>
                  ))}
                </div>
              ) : null}
              {t.state && Object.keys(t.state).length > 0 && (
                <pre className="mt-2 rounded bg-background/40 p-1.5 text-[11px]">
                  state: {JSON.stringify(t.state)}
                </pre>
              )}
            </div>
          </div>
        ))}
        {busy && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" /> running agent…
          </div>
        )}
      </div>

      <form
        className="flex gap-2 border-t p-3"
        onSubmit={(e) => {
          e.preventDefault()
          send(input)
        }}
      >
        <input
          className="flex-1 rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
          placeholder="Message the agent…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <Button type="submit" size="sm" disabled={busy || !input.trim()}>
          <Send className="size-4" />
        </Button>
      </form>
    </div>
  )
}
