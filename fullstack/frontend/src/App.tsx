import { lazy, Suspense, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Download,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  ApiError,
  createDemoRun,
  createRun,
  getMeta,
  getResults,
  getRun,
  templateUrl,
  validateFiles,
} from "./api";
import type {
  FileKey,
  Meta,
  ResultsResponse,
  Run,
  ValidationResponse,
} from "./types";
import { todayIso } from "./utils";
import { FormatGuide } from "./components/FormatGuide";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { RunProgress } from "./components/RunProgress";
import { Spinner } from "./components/ui";
import { UploadSlot } from "./components/UploadSlot";
import { ValidationPanel } from "./components/ValidationPanel";

const Results = lazy(() =>
  import("./components/Results").then((module) => ({ default: module.Results })),
);

const EMPTY_FILES: Record<FileKey, File | null> = {
  orders_web: null,
  orders_app: null,
  payments: null,
};

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Terjadi kesalahan yang tidak diketahui.";
}

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [files, setFiles] = useState(EMPTY_FILES);
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [asOf, setAsOf] = useState(todayIso());
  const [busy, setBusy] = useState<"validate" | "run" | "demo" | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getMeta()
      .then(setMeta)
      .catch((reason) => setMetaError(errorMessage(reason)));
  }, []);

  useEffect(() => {
    if (!run || (run.status !== "queued" && run.status !== "running")) {
      return;
    }
    let cancelled = false;

    const tick = async () => {
      try {
        const next = await getRun(run.id);
        if (cancelled) return;

        if (next.status === "succeeded") {
          const data = await getResults(run.id);
          if (cancelled) return;
          setRun(next);
          setResults(data);
          window.setTimeout(
            () =>
              resultsRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "start",
              }),
            150,
          );
          return;
        }

        setRun(next);
      } catch (reason) {
        if (!cancelled) setError(errorMessage(reason));
      }
    };

    tick();
    const timer = window.setInterval(tick, 1500);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [run?.id, run?.status]);

  const updateFile = (key: FileKey, file: File) => {
    setFiles((previous) => ({ ...previous, [key]: file }));
    setValidation(null);
    setError(null);
  };

  const clearFile = (key: FileKey) => {
    setFiles((previous) => ({ ...previous, [key]: null }));
    setValidation(null);
    setError(null);
  };

  const handleValidate = async () => {
    setBusy("validate");
    setError(null);
    try {
      setValidation(await validateFiles(files));
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(null);
    }
  };

  const handleRun = async () => {
    if (!validation?.ok) {
      setError("Validasi file terlebih dahulu sebelum menjalankan pipeline.");
      return;
    }
    setBusy("run");
    setError(null);
    setResults(null);
    try {
      const created = await createRun(asOf, files);
      setRun(await getRun(created.id));
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(null);
    }
  };

  const handleDemo = async () => {
    setBusy("demo");
    setError(null);
    setResults(null);
    try {
      const created = await createDemoRun(asOf);
      setRun(await getRun(created.id));
      window.setTimeout(
        () =>
          document
            .getElementById("workspace")
            ?.scrollIntoView({ behavior: "smooth", block: "start" }),
        100,
      );
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(null);
    }
  };

  const demoStarted = useRef(false);
  useEffect(() => {
    if (demoStarted.current) return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("demo") !== "1") return;
    demoStarted.current = true;
    void handleDemo();
    // handleDemo hanya dipanggil sekali saat halaman dibuka dengan ?demo=1
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const reset = () => {
    setRun(null);
    setResults(null);
    setValidation(null);
    setFiles(EMPTY_FILES);
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen overflow-x-clip">
      <Header />
      <Hero
        onDemo={handleDemo}
        onUpload={() =>
          document
            .getElementById("workspace")
            ?.scrollIntoView({ behavior: "smooth", block: "start" })
        }
        demoLoading={busy === "demo"}
        demoAvailable={meta?.demo_available ?? false}
      />

      <section
        id="workspace"
        className="mx-auto w-full min-w-0 max-w-7xl scroll-mt-20 px-4 pb-14 sm:px-6"
      >
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">
              Workspace
            </p>
            <h2 className="mt-1 text-xl font-semibold tracking-tight text-ink">
              Upload, validasi, jalankan
            </h2>
            <p className="mt-1 text-sm text-muted">
              Tiga file CSV. Template tersedia jika belum punya data.
            </p>
          </div>
          <a
            href={templateUrl("all.zip")}
            className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-ink-soft transition hover:bg-surface-muted"
          >
            <Download className="h-3.5 w-3.5" />
            Unduh semua template
          </a>
        </div>

        <div className="grid min-w-0 gap-4 lg:grid-cols-[1.55fr_0.9fr]">
          <div className="min-w-0 rounded-2xl border border-line bg-white p-4 shadow-card sm:p-5">
            <div className="flex items-start gap-2 rounded-lg border border-brand-200 bg-brand-50 px-3 py-2.5">
              <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-brand-700" />
              <p className="text-xs leading-relaxed text-brand-900">
                Data diproses di server, disimpan maksimal{" "}
                {meta?.limits.ttl_hours ?? 24} jam, lalu dihapus otomatis. Jangan
                upload data klien atau data sensitif ke demo publik.
              </p>
            </div>

            {metaError ? (
              <div className="mt-4 flex items-start gap-2 rounded-lg bg-rose-50 px-3 py-3 text-xs text-rose-700">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                <div>
                  <p>{metaError}</p>
                  <p className="mt-1 text-rose-600">
                    Pastikan backend berjalan di port 8000.
                  </p>
                </div>
              </div>
            ) : !meta ? (
              <div className="mt-4 flex items-center gap-2 rounded-lg border border-line bg-surface-muted px-3 py-6 text-xs text-muted">
                <Spinner />
                Memuat skema file...
              </div>
            ) : (
              <div className="mt-4 grid gap-3">
                {meta.schema.files.map((file) => (
                  <UploadSlot
                    key={file.key}
                    schema={file}
                    file={files[file.key]}
                    validation={validation?.files[file.filename]}
                    disabled={busy !== null || run?.status === "running"}
                    onFile={(selected) => updateFile(file.key, selected)}
                    onClear={() => clearFile(file.key)}
                  />
                ))}
              </div>
            )}

            <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_auto_auto] sm:items-end">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted">
                Tanggal as-of
                <input
                  type="date"
                  value={asOf}
                  onChange={(event) => setAsOf(event.target.value)}
                  className="mt-1 block w-full rounded-lg border border-line bg-white px-3 py-2.5 text-sm text-ink outline-none focus:border-brand-500"
                />
              </label>
              <button
                type="button"
                onClick={handleValidate}
                disabled={busy !== null || !meta}
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-line bg-surface-muted px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy === "validate" ? (
                  <Spinner />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Validasi
              </button>
              <button
                type="button"
                onClick={handleRun}
                disabled={
                  busy !== null ||
                  !validation?.ok ||
                  run?.status === "running"
                }
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-700 px-4 py-2.5 text-sm font-semibold text-white shadow-card transition hover:bg-brand-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy === "run" ? <Spinner /> : <Play className="h-4 w-4" />}
                Jalankan pipeline
              </button>
            </div>

            {validation && (
              <div className="mt-4">
                <ValidationPanel validation={validation} />
              </div>
            )}

            {error && (
              <p className="mt-3 flex items-start gap-2 break-words rounded-lg bg-rose-50 px-3 py-2.5 text-xs text-rose-700">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                {error}
              </p>
            )}
          </div>

          <aside className="h-fit min-w-0 lg:sticky lg:top-20">
            {meta ? (
              <FormatGuide meta={meta} />
            ) : (
              <div className="rounded-xl border border-line bg-white p-4 text-xs text-muted">
                <Sparkles className="mb-2 h-4 w-4 text-brand-700" />
                Panduan format akan muncul setelah backend terhubung.
              </div>
            )}
          </aside>
        </div>
      </section>

      {run && (
        <section className="mx-auto w-full min-w-0 max-w-7xl px-4 pb-8 sm:px-6">
          <RunProgress run={run} />
        </section>
      )}

      <div ref={resultsRef} className="scroll-mt-20">
        {results ? (
          <Suspense
            fallback={
              <div className="mx-auto flex max-w-7xl items-center justify-center gap-2 px-4 py-16 text-sm text-muted sm:px-6">
                <Spinner />
                Memuat hasil...
              </div>
            }
          >
            <Results results={results} onNewRun={reset} />
          </Suspense>
        ) : (
          !run && (
            <section className="mx-auto w-full max-w-7xl px-4 pb-16 sm:px-6">
              <div className="rounded-2xl border border-dashed border-line bg-white px-6 py-10 text-center">
                <p className="text-sm font-semibold text-ink">
                  Hasil akan muncul di sini
                </p>
                <p className="mx-auto mt-1 max-w-md text-xs leading-relaxed text-muted">
                  Klik "Coba data demo" untuk melihat contoh laporan lengkap,
                  atau upload tiga file CSV lalu jalankan pipeline.
                </p>
              </div>
            </section>
          )
        )}
      </div>

      <footer className="border-t border-line bg-white/60">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-6 text-xs text-muted sm:px-6">
          <p className="break-words">
            Data Quality Studio - FastAPI, React, Tailwind, SQLite/Postgres.
          </p>
          <p className="break-words">
            16 SQL checks · rekonsiliasi order vs payment · laporan harian
          </p>
        </div>
      </footer>
    </div>
  );
}
