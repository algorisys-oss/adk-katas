import { useState } from "react"
import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { getTheme, toggleTheme } from "@/lib/theme"

export function ThemeToggle() {
  const [theme, setThemeState] = useState(getTheme())
  return (
    <Button
      variant="ghost"
      size="icon"
      className="size-8 shrink-0"
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      onClick={() => setThemeState(toggleTheme())}
    >
      {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
