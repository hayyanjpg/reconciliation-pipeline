import { useRef, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  FileText,
  Trash2,
  UploadCloud,
  XCircle,
} from "lucide-react";
import { templateUrl } from "../api";
import type { FileSchema, FileValidation } from "../types";
import { cn, formatBytes } from "../utils";
import { StatusBadge } from "./ui";

export function UploadSlot({
  schema,
  file,
  validation,
  disabled,
  onFile,
  onClear,
}: {
  schema: FileSchema;
  file: File | null;
  validation?: FileValidation;
  disabled?: boolean;
  onFile: (file: File) => void;
  onClear: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const status = validation?.status;
  const Icon =
    status === "ok"
      ? CheckCircle2
      : status === "warning"
        ? AlertTriangle
        : status === "error"
          ? XCircle
          : FileText;

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        if (disabled) return;
        const dropped = event.dataTransfer.files?.[0];
        if (dropped) onFile(dropped);
      }}
      className={cn(
        "min-w-0 rounded-xl border bg-white p-4 transition",
        dragging
          ? "border-brand-500 bg-brand-50"
          : "border-line hover:border-line-strong",
        disabled && "opacity-70",
      )}
    >
      <div className="flex min-w-0 items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <span
            className={cn(
              "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
              status === "error"
                ? "bg-rose-50 text-rose-700"
                : status === "ok"
                  ? "bg-brand-50 text-brand-700"
                  : "bg-surface-muted text-ink-soft",
            )}
          >
            <Icon className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-ink">{schema.label}</p>
            <p className="mt-0.5 text-xs text-muted">{schema.description}</p>
            <code className="mt-1 inline-block max-w-full break-all rounded border border-line bg-surface-muted px-1.5 py-0.5 font-mono text-xs text-ink-soft">
              {schema.filename}
            </code>
          </div>
        </div>
        {validation && <StatusBadge value={validation.status} />}
      </div>

      {file ? (
        <div className="mt-3 flex min-w-0 items-center justify-between gap-2 rounded-lg border border-line bg-surface-muted px-3 py-2">
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-ink">{file.name}</p>
            <p className="text-xs text-muted">
              {formatBytes(file.size)}
              {validation ? ` · ${validation.row_count} baris` : ""}
            </p>
          </div>
          <button
            type="button"
            onClick={onClear}
            disabled={disabled}
            className="shrink-0 rounded-md p-1.5 text-muted transition hover:bg-rose-50 hover:text-rose-700"
            aria-label={`Hapus ${file.name}`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-line-strong bg-surface-muted px-3 py-4 text-xs font-medium text-ink-soft transition hover:border-brand-400 hover:bg-brand-50 hover:text-brand-800"
        >
          <UploadCloud className="h-4 w-4" />
          Pilih atau tarik file CSV
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={(event) => {
          const selected = event.target.files?.[0];
          if (selected) onFile(selected);
          event.target.value = "";
        }}
      />

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <a
          href={templateUrl(schema.key)}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-brand-700 transition hover:text-brand-800"
        >
          <Download className="h-3.5 w-3.5" />
          Template CSV
        </a>
        <span className="text-xs text-muted">
          {schema.fields.filter((field) => field.required).length} kolom wajib
        </span>
      </div>
    </div>
  );
}
