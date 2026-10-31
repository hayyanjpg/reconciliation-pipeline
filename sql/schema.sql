-- Skema Data Quality Assurance
-- Lapisan staging sengaja tidak diberi constraint unik agar check duplikat
-- bisa mendeteksi masalah. Constraint ditegakkan di lapisan curated.

DROP VIEW IF EXISTS orders_dedup;
DROP TABLE IF EXISTS payments_curated;
DROP TABLE IF EXISTS orders_curated;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id        TEXT NOT NULL,
    customer_id     TEXT,
    order_date      TEXT,
    amount          INTEGER,
    status          TEXT,
    channel         TEXT,
    source_file     TEXT,
    raw_order_date  TEXT,
    raw_amount      TEXT
);

CREATE TABLE payments (
    payment_id       TEXT NOT NULL,
    order_id         TEXT NOT NULL,
    paid_at          TEXT,
    paid_amount      INTEGER,
    method           TEXT,
    status           TEXT,
    source_file      TEXT,
    raw_paid_at      TEXT,
    raw_paid_amount  TEXT
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_payment_id ON payments(payment_id);

-- Satu baris per order_id (baris pertama menang), dipakai untuk join rekonsiliasi.
CREATE VIEW orders_dedup AS
SELECT *
FROM orders
WHERE rowid IN (SELECT MIN(rowid) FROM orders GROUP BY order_id);

-- Lapisan curated: hanya baris yang lolos validasi yang boleh masuk sini.
CREATE TABLE orders_curated (
    order_id     TEXT PRIMARY KEY,
    customer_id  TEXT NOT NULL,
    order_date   TEXT NOT NULL,
    amount       INTEGER NOT NULL CHECK (amount > 0),
    status       TEXT NOT NULL
                 CHECK (status IN ('COMPLETED', 'PENDING', 'CANCELLED', 'REFUNDED')),
    channel      TEXT NOT NULL
);

CREATE TABLE payments_curated (
    payment_id   TEXT PRIMARY KEY,
    order_id     TEXT NOT NULL REFERENCES orders_curated(order_id),
    paid_at      TEXT NOT NULL,
    paid_amount  INTEGER NOT NULL CHECK (paid_amount >= 0),
    method       TEXT NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('PAID', 'PENDING', 'FAILED'))
);
