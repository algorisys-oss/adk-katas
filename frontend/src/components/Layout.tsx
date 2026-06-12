import { useEffect } from "react"
import { NavLink, Outlet } from "react-router-dom"
import { CheckCircle2, Circle, Sparkles, KeyRound, KeyboardOff } from "lucide-react"
import { useKataStore } from "@/store/useKataStore"
import { ThemeToggle } from "@/components/ThemeToggle"
import { cn } from "@/lib/utils"

export function Layout() {
  const { katas, statusBySlug, health, loaded, init } = useKataStore()

  useEffect(() => {
    if (!loaded) init()
  }, [loaded, init])

  const done = Object.values(statusBySlug).filter((s) => s === "passed").length

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="flex w-72 shrink-0 flex-col border-r bg-card">
        <div className="flex items-center justify-between gap-2 border-b px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2">
            <Sparkles className="size-5 text-primary" />
            <div>
              <div className="font-semibold leading-tight">ADK Katas</div>
              <div className="text-xs text-muted-foreground">
                {done}/{katas.length || 9} complete
              </div>
            </div>
          </NavLink>
          <ThemeToggle />
        </div>

        <nav className="flex-1 overflow-auto p-2">
          {katas.map((k) => {
            const passed = statusBySlug[k.slug] === "passed"
            return (
              <NavLink
                key={k.slug}
                to={`/kata/${k.slug}`}
                className={({ isActive }) =>
                  cn(
                    "flex items-start gap-2 rounded-md px-3 py-2 text-sm",
                    isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/50"
                  )
                }
              >
                {passed ? (
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[var(--success)]" />
                ) : (
                  <Circle className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                )}
                <span>
                  <span className="font-mono text-xs text-muted-foreground">{k.id}</span>{" "}
                  {k.title}
                </span>
              </NavLink>
            )
          })}
          {katas.length === 0 && (
            <p className="p-3 text-xs text-muted-foreground">
              Loading katas… is the backend running on :8001?
            </p>
          )}
        </nav>

        <div className="border-t p-3 text-xs text-muted-foreground">
          {health ? (
            <div className="flex items-center gap-2">
              {health.has_api_key ? (
                <KeyRound className="size-3.5 text-[var(--success)]" />
              ) : (
                <KeyboardOff className="size-3.5" />
              )}
              <span>
                ADK {health.adk_version} · {health.has_api_key ? "API key set" : "no API key"}
              </span>
            </div>
          ) : (
            <span>backend offline</span>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
