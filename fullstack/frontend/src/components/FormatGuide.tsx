import { ChevronDown, Download, Info } from "lucide-react";
import { templateUrl } from "../api";
import type { Meta } from "../types";

const FORMAT_LABELS: Record<string, string> = {
  amount: "Nominal",
  date: "Tanggal",
  status_order: "Status order",
  status_payment: "Status payment",
  channel: "Channel",
  encoding: "Encoding",
  delimiter: "Pemisah",
};

export function FormatGuide({ meta }: { meta: Meta }) {
  return (
    <div className="min-w-0 space-y-4">
      <div className="rounded-xl border border-brand-200 bg-brand-50 p-4">
        <div className="flex items-start gap-2">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-brand-700" />
          <div className="min-w-0">
            <p className="text-sm font-semibold text-ink">
              Isi boleh beda, format harus sama
            </p>
            <p className="mt-1 text-xs leading-relaxed text-muted">
              Jumlah baris, ID, nominal, dan tanggal bebas. Yang perlu sama
              hanya nama kolom dan tipe nilainya. Tidak punya file? Unduh
              template di bawah.
            </p>
          </div>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          <a
            href={templateUrl("all.zip")}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-700 px-3 py-2 text-xs font-semibold text-white transition hover:bg-brand-800"
          >
            <Download className="h-3.5 w-3.5" />
            Semua template (ZIP)
          </a>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-ink-soft transition hover:bg-surface-muted"
          >
            Dokumentasi API
          </a>
        </div>
      </div>

      <div className="space-y-2">
        {meta.schema.files.map((file) => (
          <details
            key={file.key}
            className="group rounded-xl border border-line bg-white"
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-4 py-3 transition hover:bg-surface-muted">
              <div className="min-w-0">
                <p className="text-sm font-semibold text-ink">{file.label}</p>
                <p className="break-all font-mono text-xs text-muted">
                  {file.filename}
                </p>
              </div>
              <ChevronDown className="h-4 w-4 shrink-0 text-muted transition group-open:rotate-180" />
            </summary>
            <div className="border-t border-line px-4 py-3">
              <div className="space-y-2">
                {file.fields.map((field) => (
                  <div
                    key={field.name}
                    className="flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="min-w-0">
                      <p className="break-all font-mono text-xs text-ink">
                        {field.name}
                      </p>
                      <p className="mt-0.5 text-xs text-muted">
                        {field.description}
                      </p>
                    </div>
                    <span
                      className={
                        field.required
                          ? "shrink-0 rounded-md bg-rose-50 px-2 py-0.5 text-xs font-semibold text-rose-700"
                          : field.recommended
                            ? "shrink-0 rounded-md bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-800"
                            : "shrink-0 rounded-md bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600"
                      }
                    >
                      {field.required
                        ? "wajib"
                        : field.recommended
                          ? "disarankan"
                          : "opsional"}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-3 rounded-lg border border-line bg-surface-muted p-2.5">
                <p className="text-xs uppercase tracking-wider text-muted">
                  Contoh baris
                </p>
                <p className="mt-1 break-all font-mono text-xs text-brand-800">
                  {Object.values(file.example).join(",")}
                </p>
              </div>
            </div>
          </details>
        ))}
      </div>

      <div className="rounded-xl border border-line bg-white p-4">
        <p className="text-sm font-semibold text-ink">Format nilai</p>
        <div className="mt-3 space-y-3">
          {Object.entries(meta.schema.accepted_formats).map(
            ([key, values]) => (
              <div key={key}>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                  {FORMAT_LABELS[key] ?? key}
                </p>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {values.map((value) => (
                    <span
                      key={value}
                      className="rounded border border-line bg-surface-muted px-1.5 py-0.5 font-mono text-xs text-ink-soft"
                    >
                      {value}
                    </span>
                  ))}
                </div>
              </div>
            ),
          )}
        </div>
      </div>
    </div>
  );
}
