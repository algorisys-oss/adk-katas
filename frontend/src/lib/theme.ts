// Minimal light/dark theme: persisted to localStorage, defaults to system.

export type Theme = "light" | "dark"
const KEY = "adk-theme"

export function getTheme(): Theme {
  const t = localStorage.getItem(KEY)
  if (t === "light" || t === "dark") return t
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export function applyTheme(t: Theme): void {
  document.documentElement.classList.toggle("dark", t === "dark")
}

export function setTheme(t: Theme): void {
  localStorage.setItem(KEY, t)
  applyTheme(t)
}

export function toggleTheme(): Theme {
  const next: Theme = getTheme() === "dark" ? "light" : "dark"
  setTheme(next)
  return next
}
