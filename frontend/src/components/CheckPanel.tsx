import { useState } from "react"
import { CheckCircle2, XCircle, Loader2, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { api, type CheckResult } from "@/lib/api"
import { useKataStore } from "@/store/useKataStore"
import { cn } from "@/lib/utils"

export function CheckPanel({ slug, code }: { slug: string; code: string }) {
  const [results, setResults] = useState<CheckResult[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)
  const markStatus = useKataStore((s) => s.markStatus)

  async function run() {
    setRunning(true)
    setError(null)
    try {
      const res = await api.check(slug, code)
      setResults(res.results)
      setError(res.error)
      if (res.ok) markStatus(slug, "passed")
    } catch (e) {
      setError(String(e))
      setResults(null)
    } finally {
      setRunning(false)
    }
  }

  const passed = results?.filter((r) => r.passed).length ?? 0
  const total = results?.length ?? 0
  const allGreen = total > 0 && passed === total

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b p-3">
        <div className="text-sm font-medium">
          Checks{" "}
          {results && (
            <span className={cn("ml-1", allGreen ? "text-[var(--success)]" : "text-muted-foreground")}>
              {passed}/{total}
            </span>
          )}
        </div>
        <Button size="sm" onClick={run} disabled={running}>
          {running ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
          Run checks
        </Button>
      </div>

      <div className="flex-1 overflow-auto p-3">
        {!results && !error && (
          <p className="text-sm text-muted-foreground">
            Fill in the editor, then run the checks. They grade your code offline — no API key needed.
          </p>
        )}

        {error && (
          <pre className="whitespace-pre-wrap rounded-md bg-destructive/10 p-3 text-xs text-destructive">
            {error}
          </pre>
        )}

        {results && (
          <ul className="space-y-1.5">
            {results.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                {r.passed ? (
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[var(--success)]" />
                ) : (
                  <XCircle className="mt-0.5 size-4 shrink-0 text-destructive" />
                )}
                <span className={cn(r.passed ? "" : "text-foreground")}>
                  {r.label}
                  {!r.passed && r.detail && (
                    <span className="block text-xs text-muted-foreground">{r.detail}</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}

        {allGreen && (
          <div className="mt-4 rounded-md bg-[var(--success)]/10 p-3 text-sm font-medium text-[var(--success)]">
            🎉 Kata complete — all checks passed!
          </div>
        )}
      </div>
    </div>
  )
}
