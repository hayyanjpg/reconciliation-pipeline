export type FileKey = "orders_web" | "orders_app" | "payments";

export type RunStatus = "queued" | "running" | "succeeded" | "failed";

export type FieldSchema = {
  name: string;
  required: boolean;
  recommended: boolean;
  aliases: string[];
  example: string;
  description: string;
};

export type FileSchema = {
  key: FileKey;
  filename: string;
  label: string;
  description: string;
  fields: FieldSchema[];
  example: Record<string, string>;
};

export type Meta = {
  schema: {
    files: FileSchema[];
    accepted_formats: Record<string, string[]>;
  };
  limits: {
    max_file_mb: number;
    ttl_hours: number;
  };
  demo_available: boolean;
};

export type FileValidation = {
  key: FileKey;
  filename: string;
  status: "ok" | "warning" | "error";
  errors: string[];
  warnings: string[];
  encoding: string | null;
  delimiter: string | null;
  row_count: number;
  headers: string[];
  recognized: string[];
  missing_required: string[];
  missing_recommended: string[];
  unknown_columns: string[];
  duplicate_columns: string[];
  preview: Record<string, string>[];
};

export type ValidationResponse = {
  ok: boolean;
  files: Record<string, FileValidation>;
  missing_files: string[];
};

export type Check = {
  name: string;
  category: string;
  severity: string;
  status: "PASS" | "FAIL" | "ERROR";
  failed_rows: number;
  total_rows: number;
  description: string;
  sample?: unknown;
};

export type Reconciliation = {
  total_order_rows: number;
  unique_orders: number;
  matched_orders: number;
  amount_mismatch: number;
  order_without_payment: number;
  orphan_payments: number;
  duplicate_order_rows: number;
  cross_channel_duplicates: number;
  duplicate_payments: number;
  amount_at_risk: number;
  [key: string]: number;
};

export type Summary = {
  as_of: string;
  generated_at: string;
  check_summary: {
    total: number;
    passed: number;
    failed: number;
    errored: number;
    pass_rate: number;
  };
  checks: Check[];
  reconciliation: Reconciliation;
  rejected_rows: number;
};

export type Run = {
  id: string;
  status: RunStatus;
  source: "upload" | "demo";
  as_of: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  files: Record<string, { filename: string; size: number }>;
  summary: Summary | null;
};

export type Artifact = {
  name: string;
  label: string;
  media_type: string;
  size: number;
};

export type ResultsResponse = {
  run: Run;
  summary: Summary;
  artifacts: Artifact[];
};

export type CsvRows = Record<string, string>[];
