from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "raw"
SQL_DIR = ROOT / "sql"
REPORT_DIR = ROOT / "reports"
PROCESSED_DIR = REPORT_DIR / "processed"
DB_PATH = REPORT_DIR / "qa.db"

ORDER_SOURCES = {
    "orders_web.csv": "WEB",
    "orders_app.csv": "APP",
}
PAYMENTS_FILE = "payments.csv"

ALLOWED_STATUS = ("COMPLETED", "PENDING", "CANCELLED", "REFUNDED")
ALLOWED_PAYMENT_STATUS = ("PAID", "PENDING", "FAILED")

AMOUNT_TOLERANCE = 0
FRESHNESS_DAYS = 2
LATE_PAYMENT_DAYS = 7
