import { Link } from "react-router-dom"
import { ArrowRight, CheckCircle2, Circle, Sparkles } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useKataStore } from "@/store/useKataStore"

export function HomePage() {
  const { katas, statusBySlug, health } = useKataStore()
  const firstTodo = katas.find((k) => statusBySlug[k.slug] !== "passed") ?? katas[0]

  return (
    <div className="h-full overflow-auto">
      <div className="mx-auto max-w-4xl px-8 py-10">
        <div className="flex items-center gap-2 text-primary">
          <Sparkles className="size-6" />
          <h1 className="text-2xl font-bold">ADK Katas</h1>
        </div>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Learn Google's <strong>Agent Development Kit</strong> (ADK {health?.adk_version ?? "2"}) by
          doing. Each kata teaches one concept: read it, fill in the code, run the offline checks, and
          chat with your agent live. Your progress is saved in this browser.
        </p>

        {firstTodo && (
          <Button asChild className="mt-5">
            <Link to={`/kata/${firstTodo.slug}`}>
              Start kata {firstTodo.id}: {firstTodo.title} <ArrowRight className="size-4" />
            </Link>
          </Button>
        )}

        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          {katas.map((k) => {
            const passed = statusBySlug[k.slug] === "passed"
            return (
              <Link key={k.slug} to={`/kata/${k.slug}`}>
                <Card className="h-full transition-colors hover:border-primary/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      {passed ? (
                        <CheckCircle2 className="size-4 text-[var(--success)]" />
                      ) : (
                        <Circle className="size-4 text-muted-foreground" />
                      )}
                      <span className="font-mono text-xs text-muted-foreground">{k.id}</span>
                      {k.title}
                    </CardTitle>
                    <CardDescription>{k.blurb}</CardDescription>
                  </CardHeader>
                </Card>
              </Link>
            )
          })}
        </div>

        {katas.length === 0 && (
          <Card className="mt-8">
            <CardContent className="py-6 text-sm text-muted-foreground">
              No katas loaded. Make sure the backend is running:
              <pre className="mt-2 rounded bg-muted p-2 text-xs">uv run uvicorn server:app --port 8001</pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
