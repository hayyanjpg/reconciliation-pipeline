import { Activity, BookOpen } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-line/80 bg-canvas/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
        <a href="#top" className="flex min-w-0 items-center gap-3">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-700 font-mono text-xs font-semibold tracking-wider text-white">
            DQ
          </span>
          <span className="min-w-0 leading-tight">
            <span className="block truncate text-sm font-semibold text-ink">
              Data Quality Studio
            </span>
            <span className="hidden truncate text-xs text-muted sm:block">
              Upload, validasi, rekonsiliasi
            </span>
          </span>
        </a>

        <nav className="flex shrink-0 items-center gap-1 text-sm">
          <a
            href="#workspace"
            className="hidden rounded-lg px-3 py-2 text-muted transition hover:bg-white hover:text-ink sm:block"
          >
            Upload
          </a>
          <a
            href="#results"
            className="hidden rounded-lg px-3 py-2 text-muted transition hover:bg-white hover:text-ink sm:block"
          >
            Hasil
          </a>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            aria-label="Dokumentasi API"
            className="flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-muted transition hover:bg-white hover:text-ink sm:px-3"
          >
            <BookOpen className="h-4 w-4" />
            <span className="hidden sm:inline">API Docs</span>
          </a>
          <span className="ml-1 hidden items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-800 md:flex">
            <Activity className="h-3 w-3" />
            API aktif
          </span>
        </nav>
      </div>
    </header>
  );
}
