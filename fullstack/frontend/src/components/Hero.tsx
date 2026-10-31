import { ArrowRight, Database, Play, ShieldCheck, UploadCloud } from "lucide-react";
import { Spinner } from "./ui";

export function Hero({
  onDemo,
  onUpload,
  demoLoading,
  demoAvailable,
}: {
  onDemo: () => void;
  onUpload: () => void;
  demoLoading: boolean;
  demoAvailable: boolean;
}) {
  return (
    <section
      id="top"
      className="relative overflow-hidden border-b border-line/80"
    >
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(28,37,35,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(28,37,35,0.04)_1px,transparent_1px)] [background-size:36px_36px] [mask-image:linear-gradient(to_bottom,black,transparent_92%)]" />

      <div className="relative mx-auto grid max-w-7xl gap-10 px-4 pb-14 pt-14 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:items-center lg:gap-14 lg:pt-20">
        <div className="min-w-0">
          <span className="inline-flex items-center gap-2 border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-800">
            <ShieldCheck className="h-3.5 w-3.5" />
            Full-stack Data Quality Assurance
          </span>

          <h1 className="mt-5 max-w-3xl text-[2.15rem] font-semibold leading-[1.08] tracking-tight text-ink sm:text-5xl lg:text-6xl">
            Temukan masalah data{" "}
            <span className="text-brand-700">
              sebelum klien menemukannya.
            </span>
          </h1>

          <p className="mt-5 max-w-xl text-base leading-relaxed text-muted">
            Upload order dan payment, validasi format otomatis, lalu jalankan 16
            SQL check dan rekonsiliasi multichannel. Hasil langsung dalam bentuk
            KPI, tabel temuan, dan laporan siap kirim.
          </p>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button
              type="button"
              onClick={onDemo}
              disabled={demoLoading || !demoAvailable}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-700 px-5 py-3 text-sm font-semibold text-white shadow-card transition hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              {demoLoading ? <Spinner /> : <Play className="h-4 w-4" />}
              Coba data demo
            </button>
            <button
              type="button"
              onClick={onUpload}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-line bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-line-strong hover:bg-surface-muted sm:w-auto"
            >
              <UploadCloud className="h-4 w-4" />
              Upload data sendiri
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-9 grid max-w-lg grid-cols-3 divide-x divide-line border-y border-line">
            {[
              ["16", "SQL checks"],
              ["3", "File CSV"],
              ["12,5%", "Pass rate demo"],
            ].map(([value, label], index) => (
              <div
                key={label}
                className={index === 0 ? "py-3 pr-3" : "px-3 py-3"}
              >
                <p className="font-mono text-lg font-semibold text-ink sm:text-xl">
                  {value}
                </p>
                <p className="mt-0.5 text-xs text-muted">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative min-w-0">
          <div className="rounded-2xl border border-line bg-white p-5 shadow-lift sm:p-6">
            <div className="flex items-start justify-between gap-3">
              <div className="flex min-w-0 items-center gap-2 text-sm font-semibold text-ink">
                <Database className="h-4 w-4 shrink-0 text-brand-700" />
                <span className="truncate">Quality snapshot</span>
              </div>
              <span className="shrink-0 border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-rose-700">
                Perlu tindakan
              </span>
            </div>

            <div className="mt-5 border border-line bg-surface-muted p-4">
              <div className="flex items-end justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">
                    Pass rate
                  </p>
                  <p className="mt-1 font-mono text-3xl font-semibold text-ink">
                    12,5%
                  </p>
                </div>
                <p className="text-right text-xs leading-5 text-muted">
                  2 lulus
                  <br />
                  14 gagal
                </p>
              </div>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-line">
                <div className="h-full w-[12.5%] rounded-full bg-rose-500" />
              </div>
            </div>

            <div className="mt-4 divide-y divide-line border-y border-line">
              {[
                ["Amount mismatch", "12", "text-rose-700"],
                ["Pembayaran yatim", "6", "text-amber-700"],
                ["Order belum dibayar", "18", "text-sky-700"],
                ["Nominal berisiko", "Rp 5.118.000", "text-rose-700"],
              ].map(([label, value, color]) => (
                <div
                  key={label}
                  className="flex items-center justify-between gap-4 py-2.5 text-xs"
                >
                  <span className="text-muted">{label}</span>
                  <span className={`shrink-0 font-mono font-semibold ${color}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>

            <p className="mt-4 text-xs leading-relaxed text-muted">
              Contoh keluaran pipeline pada dataset demo sintetis.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
