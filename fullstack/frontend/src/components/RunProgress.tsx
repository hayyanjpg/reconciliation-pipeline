import { AlertTriangle, Clock3 } from "lucide-react";
import type { Run } from "../types";
import { formatDateTime } from "../utils";
import { Spinner, StatusBadge } from "./ui";

const STEPS = [
  { key: "queued", label: "Antrean" },
  { key: "running", label: "Pipeline" },
  { key: "succeeded", label: "Selesai" },
];

export function RunProgress({ run }: { run: Run }) {
  const activeIndex = STEPS.findIndex((step) => step.key === run.status);
  const progress =
    run.status === "queued"
      ? 12
      : run.status === "running"
        ? 55
        : run.status === "succeeded"
          ? 100
          : 100;

  return (
    <div className="min-w-0 rounded-xl border border-line bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          {run.status === "queued" || run.status === "running" ? (
            <Spinner />
          ) : run.status === "succeeded" ? (
            <span className="h-2.5 w-2.5 rounded-full bg-brand-600" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-rose-700" />
          )}
          <p className="text-sm font-semibold text-ink">
            {run.status === "queued"
              ? "Menunggu antrean"
              : run.status === "running"
                ? "Pipeline sedang berjalan"
                : run.status === "succeeded"
                  ? "Pipeline selesai"
                  : "Pipeline gagal"}
          </p>
        </div>
        <StatusBadge value={run.status} />
      </div>

      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full bg-brand-600 transition-all duration-700"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-muted">
        {STEPS.map((step, index) => (
          <span
            key={step.key}
            className={index <= activeIndex ? "font-semibold text-brand-700" : ""}
          >
            {step.label}
          </span>
        ))}
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted sm:grid-cols-3">
        <p className="flex items-center gap-1.5">
          <Clock3 className="h-3 w-3" />
          Mulai: {formatDateTime(run.created_at)}
        </p>
        <p>As-of: {run.as_of}</p>
        <p>Sumber: {run.source === "demo" ? "Data demo" : "Upload"}</p>
      </div>

      {run.error && (
        <p className="mt-3 break-words rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
          {run.error}
        </p>
      )}
    </div>
  );
}
