import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  PolarAngleAxis,
  RadialBar,
  RadialBarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  FileJson,
  FileText,
  RotateCcw,
  Search,
} from "lucide-react";
import { artifactUrl, fetchCsv } from "../api";
import type { Check, CsvRows, ResultsResponse } from "../types";
import {
  formatBytes,
  formatNumber,
  formatRupiah,
  parseCsv,
  severityWeight,
} from "../utils";
import { DataTable, KpiCard, SectionHeading, Spinner, StatusBadge } from "./ui";

const CSV_FILES = [
  "processed/amount_mismatch.csv",
  "processed/orphan_payments.csv",
  "processed/order_without_payment.csv",
  "processed/rejected_rows.csv",
  "processed/duplicate_orders.csv",
  "processed/cross_channel_duplicates.csv",
  "processed/duplicate_payments.csv",
];

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#dc2626",
  warning: "#d97706",
  info: "#0284c7",
};

const TOOLTIP_STYLE = {
  background: "#ffffff",
  border: "1px solid #dedbd2",
  borderRadius: 8,
  fontSize: 12,
  color: "#1c2523",
  boxShadow: "0 8px 24px -12px rgba(28, 37, 35, 0.25)",
};

type TabKey = "checks" | "recon" | "data" | "artifacts";

const TABS: { key: TabKey; label: string }[] = [
  { key: "checks", label: "Checks" },
  { key: "recon", label: "Rekonsiliasi" },
  { key: "data", label: "Data bermasalah" },
  { key: "artifacts", label: "Artefak" },
];

export function Results({
  results,
  onNewRun,
}: {
  results: ResultsResponse;
  onNewRun: () => void;
}) {
  const { run, summary } = results;
  const recon = summary.reconciliation;
  const [tab, setTab] = useState<TabKey>("checks");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [csv, setCsv] = useState<Record<string, CsvRows>>({});
  const [csvLoading, setCsvLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setCsvLoading(true);
    Promise.all(
      CSV_FILES.map(async (name) => {
        try {
          const text = await fetchCsv(artifactUrl(run.id, name));
          return [name, parseCsv(text)] as const;
        } catch {
          return [name, [] as CsvRows] as const;
        }
      }),
    ).then((entries) => {
      if (cancelled) return;
      setCsv(Object.fromEntries(entries));
      setCsvLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [run.id]);

  const checks = useMemo(
    () =>
      [...summary.checks].sort((left, right) => {
        const severity =
          severityWeight(left.severity) - severityWeight(right.severity);
        if (severity !== 0) return severity;
        if (left.status !== right.status) return left.status === "FAIL" ? -1 : 1;
        return left.name.localeCompare(right.name);
      }),
    [summary.checks],
  );

  const failedChecks = useMemo(
    () => checks.filter((check) => check.status === "FAIL"),
    [checks],
  );

  const filteredChecks = useMemo(
    () =>
      checks.filter((check) => {
        if (statusFilter !== "ALL" && check.status !== statusFilter) {
          return false;
        }
        if (severityFilter !== "ALL" && check.severity !== severityFilter) {
          return false;
        }
        if (
          search &&
          !check.name.toLowerCase().includes(search.toLowerCase()) &&
          !check.description.toLowerCase().includes(search.toLowerCase())
        ) {
          return false;
        }
        return true;
      }),
    [checks, statusFilter, severityFilter, search],
  );

  const statusData = [
    { name: "PASS", value: summary.check_summary.passed, fill: "#146a60" },
    { name: "FAIL", value: summary.check_summary.failed, fill: "#dc2626" },
    { name: "ERROR", value: summary.check_summary.errored, fill: "#d97706" },
  ].filter((item) => item.value > 0);

  const failedData = failedChecks
    .slice(0, 9)
    .map((check) => ({
      name: check.name,
      failed_rows: check.failed_rows,
      fill: SEVERITY_COLORS[check.severity] ?? "#146a60",
    }))
    .reverse();

  const criticalFailed = checks.filter(
    (check) => check.status === "FAIL" && check.severity === "critical",
  ).length;

  const csvOrEmpty = (name: string): CsvRows => csv[name] ?? [];

  return (
    <section
      id="results"
      className="mx-auto w-full min-w-0 max-w-7xl px-4 pb-16 sm:px-6"
    >
      <SectionHeading
        eyebrow="Hasil pipeline"
        title="Laporan kualitas data"
        sub={`Run ${run.id.slice(0, 8)} · as of ${summary.as_of} · ${run.source === "demo" ? "data demo" : "data upload"}`}
        right={
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={artifactUrl(run.id, "daily_report.md")}
              className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-ink-soft transition hover:bg-surface-muted"
            >
              <FileText className="h-3.5 w-3.5" />
              Laporan harian
            </a>
            <a
              href={artifactUrl(run.id, "dq_summary.json")}
              className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-ink-soft transition hover:bg-surface-muted"
            >
              <FileJson className="h-3.5 w-3.5" />
              JSON
            </a>
            <button
              type="button"
              onClick={onNewRun}
              className="inline-flex items-center gap-1.5 rounded-lg bg-brand-700 px-3 py-2 text-xs font-semibold text-white transition hover:bg-brand-800"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Run baru
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard
          label="Order rows"
          value={formatNumber(recon.total_order_rows)}
          sub={`${formatNumber(recon.unique_orders)} order unik`}
          tone="brand"
        />
        <KpiCard
          label="Order matched"
          value={formatNumber(recon.matched_orders)}
          sub={`${((recon.matched_orders / Math.max(recon.unique_orders, 1)) * 100).toFixed(1)}% dari order unik`}
          tone="emerald"
        />
        <KpiCard
          label="Critical gagal"
          value={formatNumber(criticalFailed)}
          sub={`dari ${summary.check_summary.total} check`}
          tone={criticalFailed ? "rose" : "emerald"}
        />
        <KpiCard
          label="Pembayaran yatim"
          value={formatNumber(recon.orphan_payments)}
          sub="tanpa order induk"
          tone={recon.orphan_payments ? "amber" : "emerald"}
        />
        <KpiCard
          label="Nominal berisiko"
          value={formatRupiah(recon.amount_at_risk)}
          sub="mismatch + orphan + unpaid"
          tone={recon.amount_at_risk ? "rose" : "emerald"}
        />
      </div>

      <div className="mt-4 grid min-w-0 gap-4 lg:grid-cols-3">
        <div className="min-w-0 rounded-xl border border-line bg-white p-4 shadow-card">
          <p className="text-sm font-semibold text-ink">Pass rate</p>
          <div className="relative mt-2 h-[190px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="72%"
                outerRadius="100%"
                startAngle={90}
                endAngle={-270}
                data={[
                  {
                    name: "Pass",
                    value: summary.check_summary.pass_rate,
                    fill: "#146a60",
                  },
                ]}
              >
                <PolarAngleAxis
                  type="number"
                  domain={[0, 100]}
                  tick={false}
                />
                <RadialBar
                  dataKey="value"
                  background={{ fill: "#e7e5df" }}
                  cornerRadius={20}
                />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-3xl font-semibold text-ink">
                {summary.check_summary.pass_rate.toFixed(1)}%
              </span>
              <span className="text-xs text-muted">
                {summary.check_summary.passed} dari{" "}
                {summary.check_summary.total} lulus
              </span>
            </div>
          </div>
        </div>

        <div className="min-w-0 rounded-xl border border-line bg-white p-4 shadow-card">
          <p className="text-sm font-semibold text-ink">Status check</p>
          <div className="mt-2 h-[190px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={52}
                  outerRadius={78}
                  paddingAngle={3}
                  stroke="none"
                >
                  {statusData.map((entry) => (
                    <Cell key={entry.name} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-1 flex flex-wrap justify-center gap-3 text-xs">
            {statusData.map((entry) => (
              <span
                key={entry.name}
                className="flex items-center gap-1.5 text-ink-soft"
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ background: entry.fill }}
                />
                {entry.name} {entry.value}
              </span>
            ))}
          </div>
        </div>

        <div className="min-w-0 rounded-xl border border-line bg-white p-4 shadow-card">
          <p className="text-sm font-semibold text-ink">Check gagal</p>
          <p className="text-xs text-muted">Jumlah baris bermasalah</p>
          <div className="mt-2 h-[190px]">
            {failedData.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={failedData}
                  layout="vertical"
                  margin={{ left: 4, right: 12, top: 4, bottom: 4 }}
                >
                  <CartesianGrid horizontal={false} stroke="#e7e5df" />
                  <XAxis
                    type="number"
                    tick={{ fill: "#67736f", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={132}
                    tick={{ fill: "#34423f", fontSize: 9 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="failed_rows" radius={[0, 6, 6, 0]}>
                    {failedData.map((entry) => (
                      <Cell key={entry.name} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <CheckCircle2 className="h-6 w-6 text-brand-700" />
                <p className="mt-2 text-xs text-muted">
                  Tidak ada check gagal.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 flex w-full max-w-full items-center gap-2 overflow-x-auto pb-1.5 scrollbar-thin">
        {TABS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setTab(item.key)}
            className={
              tab === item.key
                ? "shrink-0 rounded-lg bg-brand-700 px-3.5 py-2 text-xs font-semibold text-white shadow-sm"
                : "shrink-0 rounded-lg border border-line bg-white px-3.5 py-2 text-xs font-semibold text-ink-soft transition hover:bg-surface-muted"
            }
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="mt-4 min-w-0 overflow-hidden rounded-xl border border-line bg-white p-3 sm:p-4">
        {tab === "checks" && (
          <div>
            <div className="flex flex-wrap items-end gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted">
                Status
                <select
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value)}
                  className="mt-1 block rounded-lg border border-line bg-white px-2.5 py-2 text-xs text-ink outline-none focus:border-brand-500"
                >
                  <option value="ALL">Semua</option>
                  <option value="FAIL">FAIL</option>
                  <option value="PASS">PASS</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </label>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted">
                Severity
                <select
                  value={severityFilter}
                  onChange={(event) => setSeverityFilter(event.target.value)}
                  className="mt-1 block rounded-lg border border-line bg-white px-2.5 py-2 text-xs text-ink outline-none focus:border-brand-500"
                >
                  <option value="ALL">Semua</option>
                  <option value="critical">Critical</option>
                  <option value="warning">Warning</option>
                  <option value="info">Info</option>
                </select>
              </label>
              <label className="min-w-[200px] flex-1 text-xs font-semibold uppercase tracking-wider text-muted">
                Cari
                <span className="relative mt-1 block">
                  <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="nama atau deskripsi check"
                    className="w-full rounded-lg border border-line bg-white py-2 pl-8 pr-2.5 text-xs text-ink outline-none placeholder:text-muted focus:border-brand-500"
                  />
                </span>
              </label>
            </div>

            <div className="mt-3 w-full min-w-0 max-w-full overflow-auto rounded-lg border border-line">
              <table className="min-w-full border-collapse text-left text-xs">
                <thead className="sticky top-0 bg-surface-muted">
                  <tr>
                    {["Check", "Kategori", "Severity", "Status", "Gagal", "Total"].map(
                      (header) => (
                        <th
                          key={header}
                          className="whitespace-nowrap border-b border-line px-3 py-2.5 font-semibold uppercase tracking-wide text-muted"
                        >
                          {header}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-line/70">
                  {filteredChecks.map((check) => (
                    <CheckRow key={check.name} check={check} />
                  ))}
                </tbody>
              </table>
              {!filteredChecks.length && (
                <p className="p-6 text-center text-sm text-muted">
                  Tidak ada check yang cocok dengan filter.
                </p>
              )}
            </div>
          </div>
        )}

        {tab === "recon" && (
          <div className="space-y-4">
            <div className="grid min-w-0 gap-4 lg:grid-cols-[0.9fr_1.1fr]">
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Ringkasan klasifikasi
                </p>
                <DataTable
                  rows={[
                    ["Matched", recon.matched_orders],
                    ["Amount mismatch", recon.amount_mismatch],
                    ["Order tanpa pembayaran", recon.order_without_payment],
                    ["Pembayaran yatim", recon.orphan_payments],
                    ["Duplikat dalam file", recon.duplicate_order_rows],
                    ["Duplikat antar channel", recon.cross_channel_duplicates],
                    ["Pembayaran ganda", recon.duplicate_payments],
                  ].map(([Kategori, Jumlah]) => ({
                    Kategori: String(Kategori),
                    Jumlah: formatNumber(Number(Jumlah)),
                  }))}
                />
              </div>
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Amount mismatch
                </p>
                {csvLoading ? (
                  <div className="flex h-24 items-center justify-center">
                    <Spinner />
                  </div>
                ) : (
                  <DataTable
                    rows={csvOrEmpty("processed/amount_mismatch.csv")}
                    empty="Tidak ada mismatch nominal."
                    maxHeight="260px"
                  />
                )}
              </div>
            </div>
            <div className="grid min-w-0 gap-4 lg:grid-cols-2">
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Pembayaran yatim
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/orphan_payments.csv")}
                  empty="Tidak ada pembayaran yatim."
                  maxHeight="240px"
                />
              </div>
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Order belum dibayar
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/order_without_payment.csv")}
                  empty="Semua order sudah dibayar."
                  maxHeight="240px"
                />
              </div>
            </div>
          </div>
        )}

        {tab === "data" && (
          <div className="space-y-4">
            <div className="grid min-w-0 gap-4 lg:grid-cols-2">
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Baris ditolak
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/rejected_rows.csv")}
                  empty="Tidak ada baris yang ditolak."
                  maxHeight="240px"
                />
              </div>
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Duplikat dalam file
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/duplicate_orders.csv")}
                  empty="Tidak ada duplikat dalam file."
                  maxHeight="240px"
                />
              </div>
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Duplikat antar channel
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/cross_channel_duplicates.csv")}
                  empty="Tidak ada duplikat antar channel."
                  maxHeight="240px"
                />
              </div>
              <div className="min-w-0">
                <p className="mb-2 text-sm font-semibold text-ink">
                  Pembayaran ganda
                </p>
                <DataTable
                  rows={csvOrEmpty("processed/duplicate_payments.csv")}
                  empty="Tidak ada pembayaran ganda."
                  maxHeight="240px"
                />
              </div>
            </div>
          </div>
        )}

        {tab === "artifacts" && (
          <div className="grid min-w-0 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {results.artifacts.map((artifact) => (
              <a
                key={artifact.name}
                href={artifactUrl(run.id, artifact.name)}
                className="flex min-w-0 items-center justify-between gap-3 overflow-hidden rounded-lg border border-line bg-surface-muted px-3 py-2.5 transition hover:border-brand-300 hover:bg-brand-50"
              >
                <div className="flex min-w-0 items-center gap-2">
                  {artifact.name.endsWith(".json") ? (
                    <FileJson className="h-4 w-4 shrink-0 text-amber-700" />
                  ) : (
                    <FileText className="h-4 w-4 shrink-0 text-brand-700" />
                  )}
                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold text-ink">
                      {artifact.label}
                    </p>
                    <p className="truncate font-mono text-xs text-muted">
                      {artifact.name}
                    </p>
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="text-xs text-muted">
                    {formatBytes(artifact.size)}
                  </span>
                  <Download className="h-3.5 w-3.5 text-muted" />
                </div>
              </a>
            ))}
          </div>
        )}
      </div>

      {criticalFailed > 0 && (
        <div className="mt-4 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose-700" />
          <p className="break-words text-xs leading-relaxed text-rose-700">
            {criticalFailed} critical check gagal. Prioritaskan amount mismatch,
            pembayaran yatim, dan order belum dibayar sebelum data dipakai untuk
            pelaporan.
          </p>
        </div>
      )}
    </section>
  );
}

function CheckRow({ check }: { check: Check }) {
  return (
    <tr className="hover:bg-surface-muted">
      <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-ink">
        {check.name}
      </td>
      <td className="whitespace-nowrap px-3 py-2 text-muted">
        {check.category}
      </td>
      <td className="whitespace-nowrap px-3 py-2">
        <StatusBadge value={check.severity} />
      </td>
      <td className="whitespace-nowrap px-3 py-2">
        <StatusBadge value={check.status} />
      </td>
      <td className="whitespace-nowrap px-3 py-2 font-semibold text-ink">
        {formatNumber(check.failed_rows)}
      </td>
      <td className="whitespace-nowrap px-3 py-2 text-muted">
        {formatNumber(check.total_rows)}
      </td>
    </tr>
  );
}
