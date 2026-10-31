import { AlertTriangle, CheckCircle2, ChevronDown, XCircle } from "lucide-react";
import type { ValidationResponse } from "../types";
import { DataTable, StatusBadge } from "./ui";

export function ValidationPanel({
  validation,
}: {
  validation: ValidationResponse;
}) {
  const results = Object.values(validation.files);
  const errors = results.reduce(
    (total, item) => total + item.errors.length,
    0,
  );
  const warnings = results.reduce(
    (total, item) => total + item.warnings.length,
    0,
  );

  return (
    <div className="min-w-0 rounded-xl border border-line bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          {validation.ok ? (
            <CheckCircle2 className="h-4 w-4 shrink-0 text-brand-700" />
          ) : (
            <XCircle className="h-4 w-4 shrink-0 text-rose-700" />
          )}
          <p className="text-sm font-semibold text-ink">
            {validation.ok
              ? "Validasi lolos - siap dijalankan"
              : "Validasi menemukan masalah"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="rounded-md bg-rose-50 px-2 py-0.5 font-semibold text-rose-700">
            {errors} error
          </span>
          <span className="rounded-md bg-amber-50 px-2 py-0.5 font-semibold text-amber-800">
            {warnings} peringatan
          </span>
        </div>
      </div>

      {validation.missing_files.length > 0 && (
        <p className="mt-2 break-words rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
          File belum diupload: {validation.missing_files.join(", ")}
        </p>
      )}

      <div className="mt-3 space-y-2">
        {results.map((item) => (
          <div
            key={item.filename}
            className="min-w-0 rounded-lg border border-line bg-surface-muted px-3 py-2.5"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex min-w-0 items-center gap-2">
                <StatusBadge value={item.status} />
                <span className="break-all font-mono text-xs text-ink-soft">
                  {item.filename}
                </span>
              </div>
              <span className="text-xs text-muted">
                {item.row_count} baris · {item.encoding ?? "-"} · pemisah{" "}
                {item.delimiter === "\t" ? "tab" : item.delimiter ?? "-"}
              </span>
            </div>

            {item.errors.map((error) => (
              <p
                key={error}
                className="mt-1.5 flex items-start gap-1.5 text-xs text-rose-700"
              >
                <XCircle className="mt-0.5 h-3 w-3 shrink-0" />
                {error}
              </p>
            ))}
            {item.warnings.map((warning) => (
              <p
                key={warning}
                className="mt-1.5 flex items-start gap-1.5 text-xs text-amber-800"
              >
                <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" />
                {warning}
              </p>
            ))}

            {item.preview.length > 0 && (
              <details className="group mt-2">
                <summary className="flex cursor-pointer list-none items-center gap-1 text-xs font-medium text-brand-700">
                  <ChevronDown className="h-3 w-3 transition group-open:rotate-180" />
                  Preview {item.preview.length} baris
                </summary>
                <div className="mt-2">
                  <DataTable rows={item.preview} maxHeight="180px" />
                </div>
              </details>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
