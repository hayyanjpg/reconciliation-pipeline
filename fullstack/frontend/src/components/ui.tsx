import type { ReactNode } from "react";
import { cn } from "../utils";

const STATUS_STYLES: Record<string, string> = {
  PASS: "bg-brand-50 text-brand-800 ring-brand-200",
  FAIL: "bg-rose-50 text-rose-700 ring-rose-200",
  ERROR: "bg-amber-50 text-amber-800 ring-amber-200",
  ok: "bg-brand-50 text-brand-800 ring-brand-200",
  warning: "bg-amber-50 text-amber-800 ring-amber-200",
  error: "bg-rose-50 text-rose-700 ring-rose-200",
  critical: "bg-rose-50 text-rose-700 ring-rose-200",
  info: "bg-sky-50 text-sky-700 ring-sky-200",
  queued: "bg-slate-100 text-slate-600 ring-slate-200",
  running: "bg-brand-50 text-brand-800 ring-brand-200",
  succeeded: "bg-brand-50 text-brand-800 ring-brand-200",
  failed: "bg-rose-50 text-rose-700 ring-rose-200",
};

export function StatusBadge({
  value,
  label,
}: {
  value: string;
  label?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 ring-inset",
        STATUS_STYLES[value] ??
          "bg-slate-100 text-slate-600 ring-slate-200",
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label ?? value}
    </span>
  );
}

const TONES = {
  brand: { bar: "bg-brand-600", text: "text-brand-700" },
  emerald: { bar: "bg-emerald-600", text: "text-emerald-700" },
  rose: { bar: "bg-rose-500", text: "text-rose-700" },
  amber: { bar: "bg-amber-500", text: "text-amber-700" },
  sky: { bar: "bg-sky-600", text: "text-sky-700" },
} as const;

export type Tone = keyof typeof TONES;

export function KpiCard({
  label,
  value,
  sub,
  tone = "brand",
}: {
  label: string;
  value: string;
  sub: string;
  tone?: Tone;
}) {
  return (
    <div className="relative min-w-0 overflow-hidden rounded-xl border border-line bg-white p-4 shadow-card">
      <div className={cn("absolute inset-x-0 top-0 h-1", TONES[tone].bar)} />
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        {label}
      </p>
      <p className="mt-2 break-words font-mono text-xl font-semibold tracking-tight text-ink sm:text-2xl">
        {value}
      </p>
      <p className={cn("mt-1 text-xs", TONES[tone].text)}>{sub}</p>
    </div>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  sub,
  right,
}: {
  eyebrow?: string;
  title: string;
  sub?: string;
  right?: ReactNode;
}) {
  return (
    <div className="mb-4 flex min-w-0 flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">
            {eyebrow}
          </p>
        )}
        <h2 className="mt-1 text-xl font-semibold tracking-tight text-ink">
          {title}
        </h2>
        {sub && <p className="mt-1 break-words text-sm text-muted">{sub}</p>}
      </div>
      {right}
    </div>
  );
}

export function DataTable({
  rows,
  empty = "Tidak ada data.",
  maxHeight = "380px",
}: {
  rows: Record<string, string | number>[];
  empty?: string;
  maxHeight?: string;
}) {
  if (!rows.length) {
    return (
      <div className="rounded-lg border border-dashed border-line bg-white p-6 text-center text-sm text-muted">
        {empty}
      </div>
    );
  }

  const columns = Object.keys(rows[0]);

  return (
    <div
      className="max-w-full overflow-auto rounded-lg border border-line bg-white"
      style={{ maxHeight }}
    >
      <table className="min-w-full border-collapse text-left text-xs">
        <thead className="sticky top-0 z-10 bg-surface-muted">
          <tr>
            {columns.map((column) => (
              <th
                key={column}
                className="whitespace-nowrap border-b border-line px-3 py-2.5 font-semibold uppercase tracking-wide text-muted"
              >
                {column.replace(/_/g, " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line/70">
          {rows.map((row, index) => (
            <tr key={index} className="hover:bg-surface-muted">
              {columns.map((column) => (
                <td
                  key={column}
                  className="whitespace-nowrap px-3 py-2 text-ink-soft"
                >
                  {String(row[column] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-line border-t-brand-700",
        className,
      )}
    />
  );
}

export function EmptyState({
  icon,
  title,
  sub,
}: {
  icon: ReactNode;
  title: string;
  sub: string;
}) {
  return (
    <div className="rounded-xl border border-dashed border-line bg-white p-8 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
        {icon}
      </div>
      <p className="mt-3 font-semibold text-ink">{title}</p>
      <p className="mt-1 text-sm text-muted">{sub}</p>
    </div>
  );
}
