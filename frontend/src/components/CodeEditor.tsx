import Editor from "@monaco-editor/react"

export function CodeEditor({
  value,
  onChange,
  height = "100%",
}: {
  value: string
  onChange: (value: string) => void
  height?: string | number
}) {
  return (
    <Editor
      height={height}
      defaultLanguage="python"
      theme="vs-dark"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      options={{
        fontSize: 13,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        lineNumbers: "on",
        tabSize: 4,
        automaticLayout: true,
        padding: { top: 12, bottom: 12 },
        renderLineHighlight: "line",
      }}
    />
  )
}
