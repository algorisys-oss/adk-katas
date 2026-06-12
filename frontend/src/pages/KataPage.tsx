import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { Eye, EyeOff, RotateCcw } from "lucide-react"
import { api, type KataDetail } from "@/lib/api"
import { useKataStore } from "@/store/useKataStore"
import { Markdown } from "@/components/Markdown"
import { CodeEditor } from "@/components/CodeEditor"
import { CheckPanel } from "@/components/CheckPanel"
import { ChatPanel } from "@/components/ChatPanel"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function KataPage() {
  const { slug = "" } = useParams()
  const [kata, setKata] = useState<KataDetail | null>(null)
  const [showSolution, setShowSolution] = useState(false)
  const { setCode, codeBySlug, resetCode } = useKataStore()

  useEffect(() => {
    setKata(null)
    setShowSolution(false)
    api.getKata(slug).then(setKata).catch(() => setKata(null))
  }, [slug])

  if (!kata) {
    return <div className="p-8 text-sm text-muted-foreground">Loading kata…</div>
  }

  const code = codeBySlug[slug] ?? kata.starter_code

  return (
    <div className="grid h-full grid-cols-2 overflow-hidden">
      {/* Left: concept + task */}
      <div className="flex flex-col overflow-hidden border-r">
        <div className="flex items-center gap-2 border-b px-5 py-3">
          <Badge variant="secondary" className="font-mono">{kata.id}</Badge>
          <h2 className="font-semibold">{kata.title}</h2>
        </div>
        <div className="flex-1 overflow-auto px-5 py-4">
          <Markdown>{kata.concept_md}</Markdown>
          <div className="mt-5 rounded-lg border bg-accent/30 p-4">
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Your task
            </div>
            <Markdown>{kata.task_md}</Markdown>
          </div>

          <div className="mt-5">
            <Button variant="outline" size="sm" onClick={() => setShowSolution((v) => !v)}>
              {showSolution ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              {showSolution ? "Hide" : "Reveal"} solution
            </Button>
            {showSolution && (
              <pre className="mt-3 overflow-auto rounded-md bg-zinc-900 p-3 text-xs text-zinc-100">
                {kata.solution_code}
              </pre>
            )}
          </div>
        </div>
      </div>

      {/* Right: editor + checks/chat */}
      <div className="flex flex-col overflow-hidden">
        <div className="flex items-center justify-between border-b px-4 py-2">
          <span className="text-sm font-medium">Editor</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => resetCode(slug)}
            title="Reset to starter code"
          >
            <RotateCcw className="size-4" /> Reset
          </Button>
        </div>

        <div className="h-[45%] min-h-0 border-b">
          <CodeEditor value={code} onChange={(v) => setCode(slug, v)} />
        </div>

        <div className="min-h-0 flex-1">
          <Tabs defaultValue="checks" className="flex h-full flex-col gap-0">
            <TabsList className="m-2 w-fit">
              <TabsTrigger value="checks">Checks</TabsTrigger>
              <TabsTrigger value="chat">Live chat</TabsTrigger>
            </TabsList>
            <TabsContent value="checks" className="min-h-0 flex-1">
              <CheckPanel slug={slug} code={code} />
            </TabsContent>
            <TabsContent value="chat" className="min-h-0 flex-1">
              <ChatPanel kata={kata} code={code} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
