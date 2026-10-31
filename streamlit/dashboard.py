"""Dashboard Data Quality Assurance.

Jalankan: streamlit run streamlit/dashboard.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

DATASETS = {
    "Dirty - data uji": ROOT / "reports",
    "Clean - uji false positive": ROOT / "reports_clean",
}

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}
SEVERITY_COLOR = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#0ea5e9"}
STATUS_COLOR = {"PASS": "#10b981", "FAIL": "#ef4444", "ERROR": "#f59e0b"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f5f7fb;
    --card: #ffffff;
    --ink: #0f172a;
    --muted: #64748b;
    --line: #e2e8f0;
    --primary: #4f46e5;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

.stApp {
    background: var(--bg);
}

.block-container {
    padding: 1.4rem 2rem 3rem;
    max-width: 1500px;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(120deg, #0f172a 0%, #312e81 55%, #4f46e5 100%);
    border-radius: 20px;
    padding: 28px 32px;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    box-shadow: 0 18px 40px -24px rgba(49, 46, 129, 0.9);
    margin-bottom: 20px;
}

.hero h1 {
    margin: 4px 0 8px;
    font-size: 2.15rem;
    line-height: 1.1;
    letter-spacing: -0.03em;
    color: #ffffff;
}

.hero p {
    margin: 0 0 16px;
    color: #c7d2fe;
    font-size: 0.95rem;
    max-width: 620px;
}

.eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #a5b4fc;
    font-weight: 700;
}

.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.chip {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 0.76rem;
    color: #e0e7ff;
}

.chip.ok {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.5);
    color: #a7f3d0;
}

.chip.danger {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
    color: #fecaca;
}

.hero-right {
    text-align: right;
    min-width: 150px;
}

.hero-rate {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
}

.hero-rate-label {
    color: #c7d2fe;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-top: 6px;
}

/* ---------- KPI cards ---------- */
.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent, #4f46e5);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    height: 100%;
}

.kpi-label {
    color: var(--muted);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
}

.kpi-value {
    color: var(--ink);
    font-size: 1.7rem;
    font-weight: 750;
    letter-spacing: -0.03em;
    margin: 6px 0 2px;
    line-height: 1.15;
}

.kpi-sub {
    color: var(--muted);
    font-size: 0.76rem;
}

/* ---------- Sections ---------- */
.section {
    margin: 8px 0 10px;
}

.section-title {
    color: var(--ink);
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}

.section-sub {
    color: var(--muted);
    font-size: 0.8rem;
    margin-top: 2px;
}

/* ---------- Callout ---------- */
.callout {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 14px;
    padding: 18px;
}

.callout.ok {
    background: #ecfdf5;
    border-color: #a7f3d0;
}

.callout-label {
    color: #9f1239;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
}

.callout.ok .callout-label {
    color: #047857;
}

.callout-value {
    color: #881337;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 4px 0;
}

.callout.ok .callout-value {
    color: #065f46;
}

.callout-sub {
    color: #9f1239;
    font-size: 0.8rem;
}

.callout.ok .callout-sub {
    color: #047857;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #e8ecf7;
    padding: 6px;
    border-radius: 12px;
    margin-bottom: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 0.86rem;
    color: #475569;
}

.stTabs [aria-selected="true"] {
    background: #ffffff;
    color: #1e1b4b;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0 8px;
}

.brand-mark {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #ffffff;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    letter-spacing: -0.02em;
}

.brand-title {
    color: var(--ink);
    font-weight: 700;
    font-size: 0.98rem;
    line-height: 1.1;
}

.brand-sub {
    color: var(--muted);
    font-size: 0.75rem;
}

/* ---------- Dataframe ---------- */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

.footer {
    color: var(--muted);
    font-size: 0.76rem;
    text-align: center;
    margin-top: 28px;
}
</style>
"""


@st.cache_data(show_spinner=False)
def load_summary(report_dir: str) -> dict | None:
    path = Path(report_dir) / "dq_summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_csv(report_dir: str, name: str) -> pd.DataFrame:
    path = Path(report_dir) / "processed" / name
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def kpi_card(label: str, value: str, sub: str, accent: str) -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f"</div>"
    )


def section(title: str, sub: str = "") -> str:
    return (
        f'<div class="section"><div class="section-title">{title}</div>'
        f'<div class="section-sub">{sub}</div></div>'
    )


def render_section(title: str, sub: str = "") -> None:
    st.markdown(section(title, sub), unsafe_allow_html=True)


def gauge_figure(pass_rate: float) -> go.Figure:
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pass_rate,
            number={"suffix": "%", "font": {"size": 32, "color": "#0f172a"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "#cbd5e1"},
                "bar": {"color": "#4f46e5", "thickness": 0.32},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 90], "color": "#fef3c7"},
                    {"range": [90, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    figure.update_layout(
        height=210,
        margin={"l": 16, "r": 16, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#0f172a"},
    )
    return figure


def donut_figure(passed: int, failed: int, errored: int) -> go.Figure:
    labels = ["PASS", "FAIL", "ERROR"]
    values = [passed, failed, errored]
    colors = [STATUS_COLOR[label] for label in labels]
    figure = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.64,
            marker={"colors": colors},
            textinfo="label+value",
            textfont={"size": 12},
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    figure.update_layout(
        height=210,
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#0f172a"},
    )
    return figure


def failed_bar_figure(frame: pd.DataFrame) -> go.Figure:
    failed = frame[frame["Status"] == "FAIL"].sort_values("Baris gagal").tail(9)
    colors = [
        SEVERITY_COLOR.get(severity, "#4f46e5")
        for severity in failed["Severity"]
    ]
    figure = go.Figure(
        go.Bar(
            x=failed["Baris gagal"],
            y=failed["Check"],
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            hovertemplate="%{y}: %{x} baris<extra></extra>",
        )
    )
    figure.update_layout(
        height=280,
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#0f172a"},
        xaxis={"gridcolor": "#eef2f7", "title": None},
        yaxis={"title": None, "automargin": True},
        bargap=0.35,
    )
    return figure


def channel_bar_figure(mismatches: pd.DataFrame) -> go.Figure:
    grouped = (
        mismatches.assign(abs_difference=mismatches["difference"].abs())
        .groupby("channel")["abs_difference"]
        .sum()
        .reset_index()
    )
    figure = go.Figure(
        go.Bar(
            x=grouped["channel"],
            y=grouped["abs_difference"],
            marker={"color": ["#4f46e5", "#7c3aed", "#0ea5e9"][: len(grouped)]},
            hovertemplate="%{x}: Rp %{y:,.0f}<extra></extra>",
        )
    )
    figure.update_layout(
        height=260,
        margin={"l": 8, "r": 16, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#0f172a"},
        xaxis={"title": None},
        yaxis={"gridcolor": "#eef2f7", "title": None},
        bargap=0.45,
    )
    return figure


def style_status(frame: pd.DataFrame):
    def color(value: str) -> str:
        return {
            "PASS": "background-color:#dcfce7;color:#166534;font-weight:600",
            "FAIL": "background-color:#fee2e2;color:#991b1b;font-weight:600",
            "ERROR": "background-color:#fef3c7;color:#92400e;font-weight:600",
        }.get(value, "")

    styler = frame.style
    if hasattr(styler, "map"):
        return styler.map(color, subset=["Status"])
    return styler.applymap(color, subset=["Status"])


def main() -> None:
    st.set_page_config(
        page_title="Data Quality Command Center",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            '<div class="brand"><span class="brand-mark">DQ</span>'
            '<div><div class="brand-title">Data Quality</div>'
            '<div class="brand-sub">Command Center</div></div></div>',
            unsafe_allow_html=True,
        )
        label = st.selectbox("Dataset", list(DATASETS.keys()))
        report_dir = DATASETS[label]
        summary = load_summary(str(report_dir))

        if summary is not None:
            st.caption(f"Tanggal acuan: {summary['as_of']}")
            st.divider()
            st.markdown("**Unduh hasil**")
            summary_path = Path(report_dir) / "dq_summary.json"
            report_path = Path(report_dir) / "daily_report.md"
            if summary_path.exists():
                st.download_button(
                    "Ringkasan JSON",
                    summary_path.read_bytes(),
                    file_name="dq_summary.json",
                    mime="application/json",
                    use_container_width=True,
                )
            if report_path.exists():
                st.download_button(
                    "Laporan harian",
                    report_path.read_bytes(),
                    file_name="daily_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
        st.divider()
        with st.expander("Tentang proyek"):
            st.write(
                "Pipeline Data Quality Assurance untuk data order dan payment "
                "multichannel: normalisasi, 16 SQL check, rekonsiliasi, dan "
                "laporan harian."
            )
            st.write("Stack: Python, SQL (SQLite), Plotly, Streamlit, pytest.")

    if summary is None:
        st.error(
            f"Belum ada hasil untuk {label}. Jalankan pipeline terlebih dahulu:\n\n"
            "`python scripts/run_pipeline.py --as-of 2026-10-31`"
        )
        st.stop()

    check_summary = summary["check_summary"]
    reconciliation = summary["reconciliation"]
    checks = sorted(
        summary["checks"],
        key=lambda item: (
            SEVERITY_ORDER.get(item.get("severity", "info"), 3),
            item["status"] != "FAIL",
            item["name"],
        ),
    )

    critical_failed = sum(
        1
        for check in checks
        if check["status"] == "FAIL" and check.get("severity") == "critical"
    )
    status_text = "Perlu tindakan" if critical_failed else "Sehat"
    status_class = "danger" if critical_failed else "ok"

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-left">
                <div class="eyebrow">Data Quality Assurance</div>
                <h1>Command Center</h1>
                <p>Rekonsiliasi order vs payment, 16 SQL checks, dan monitoring
                kualitas data harian dalam satu tampilan.</p>
                <div class="chips">
                    <span class="chip">{label}</span>
                    <span class="chip">as of {summary['as_of']}</span>
                    <span class="chip {status_class}">{status_text}</span>
                </div>
            </div>
            <div class="hero-right">
                <div class="hero-rate">{check_summary['pass_rate']:.1f}%</div>
                <div class="hero-rate-label">pass rate</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        (
            "Order rows",
            f"{reconciliation['total_order_rows']:,}",
            f"{reconciliation['unique_orders']:,} order unik",
            "#4f46e5",
        ),
        (
            "Order matched",
            f"{reconciliation['matched_orders']:,}",
            f"{reconciliation['matched_orders'] / max(reconciliation['unique_orders'], 1) * 100:.1f}% dari order unik",
            "#10b981",
        ),
        (
            "Critical gagal",
            f"{critical_failed}",
            f"dari {len(checks)} check",
            "#ef4444" if critical_failed else "#10b981",
        ),
        (
            "Pembayaran yatim",
            f"{reconciliation['orphan_payments']:,}",
            "tanpa order induk",
            "#f59e0b" if reconciliation["orphan_payments"] else "#10b981",
        ),
        (
            "Nominal berisiko",
            f"Rp {reconciliation['amount_at_risk']:,}",
            "mismatch + orphan + unpaid",
            "#ef4444" if reconciliation["amount_at_risk"] else "#10b981",
        ),
    ]
    columns = st.columns(5)
    for column, (card_label, value, sub, accent) in zip(columns, cards):
        column.markdown(kpi_card(card_label, value, sub, accent), unsafe_allow_html=True)

    st.write("")

    tab_overview, tab_checks, tab_recon, tab_rows, tab_report = st.tabs(
        ["Ringkasan", "Checks", "Rekonsiliasi", "Data Bermasalah", "Laporan Harian"]
    )

    check_frame = pd.DataFrame(
        [
            {
                "Check": check["name"],
                "Kategori": check.get("category", "-"),
                "Severity": check.get("severity", "-"),
                "Status": check["status"],
                "Baris gagal": check["failed_rows"],
                "Total baris": check["total_rows"],
                "Deskripsi": check.get("description", ""),
            }
            for check in checks
        ]
    )

    with tab_overview:
        col_gauge, col_donut, col_bar = st.columns([1, 1, 1.5])
        with col_gauge:
            render_section("Pass rate", "Persentase check yang lulus")
            st.plotly_chart(
                gauge_figure(check_summary["pass_rate"]),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with col_donut:
            render_section("Status check", "Distribusi 16 check")
            st.plotly_chart(
                donut_figure(
                    check_summary["passed"],
                    check_summary["failed"],
                    check_summary["errored"],
                ),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with col_bar:
            render_section("Check gagal", "Jumlah baris bermasalah")
            if check_summary["failed"]:
                st.plotly_chart(
                    failed_bar_figure(check_frame),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.success("Tidak ada check yang gagal.")

        st.write("")
        col_recon, col_callout = st.columns([2, 1])
        with col_recon:
            render_section("Rekonsiliasi order vs payment", "Ringkasan klasifikasi")
            st.dataframe(
                pd.DataFrame(
                    [
                        ("Matched", reconciliation["matched_orders"]),
                        ("Amount mismatch", reconciliation["amount_mismatch"]),
                        ("Order tanpa pembayaran", reconciliation["order_without_payment"]),
                        ("Pembayaran yatim", reconciliation["orphan_payments"]),
                        ("Duplikat dalam file", reconciliation["duplicate_order_rows"]),
                        ("Duplikat antar channel", reconciliation["cross_channel_duplicates"]),
                        ("Pembayaran ganda", reconciliation["duplicate_payments"]),
                    ],
                    columns=["Kategori", "Jumlah"],
                ),
                hide_index=True,
                use_container_width=True,
            )
        with col_callout:
            render_section("Dampak finansial", "Estimasi nominal berisiko")
            if reconciliation["amount_at_risk"]:
                st.markdown(
                    f'<div class="callout"><div class="callout-label">Perlu tindakan</div>'
                    f'<div class="callout-value">Rp {reconciliation["amount_at_risk"]:,}</div>'
                    f'<div class="callout-sub">Selisih mismatch, pembayaran yatim, dan order belum dibayar.</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="callout ok"><div class="callout-label">Aman</div>'
                    '<div class="callout-value">Rp 0</div>'
                    '<div class="callout-sub">Tidak ada nominal berisiko.</div></div>',
                    unsafe_allow_html=True,
                )

    with tab_checks:
        render_section("16 SQL checks", "Filter berdasarkan status, severity, atau nama")
        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1.4])
        with filter_col1:
            status_filter = st.multiselect(
                "Status", ["FAIL", "PASS", "ERROR"], default=["FAIL", "ERROR"]
            )
        with filter_col2:
            severity_filter = st.multiselect(
                "Severity", ["critical", "warning", "info"],
                default=["critical", "warning", "info"],
            )
        with filter_col3:
            search = st.text_input("Cari check", placeholder="mis. mismatch, orphan")

        filtered = check_frame[
            check_frame["Status"].isin(status_filter)
            & check_frame["Severity"].isin(severity_filter)
            & check_frame["Check"].str.contains(search, case=False, na=False)
        ]

        if filtered.empty:
            st.success("Tidak ada check yang cocok dengan filter.")
        else:
            st.dataframe(
                style_status(filtered),
                hide_index=True,
                use_container_width=True,
                height=min(520, 44 + 35 * len(filtered)),
            )

        with st.expander("Lihat contoh baris yang gagal"):
            options = [check["name"] for check in checks if check.get("sample")]
            if not options:
                st.info("Tidak ada sampel baris gagal.")
            else:
                selected = st.selectbox("Check", options)
                check = next(item for item in checks if item["name"] == selected)
                st.json(check["sample"])

    with tab_recon:
        mismatches = load_csv(str(report_dir), "amount_mismatch.csv")
        orphans = load_csv(str(report_dir), "orphan_payments.csv")
        unpaid = load_csv(str(report_dir), "order_without_payment.csv")

        render_section("Mismatch nominal per channel", "Total selisih absolut")
        if mismatches.empty:
            st.success("Tidak ada mismatch nominal.")
        else:
            st.plotly_chart(
                channel_bar_figure(mismatches),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            st.dataframe(
                mismatches[
                    [
                        "order_id",
                        "channel",
                        "expected_amount",
                        "paid_amount",
                        "difference",
                        "payment_count",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
                height=320,
            )

        col_orphan, col_unpaid = st.columns(2)
        with col_orphan:
            render_section("Pembayaran yatim", "Tanpa order induk")
            if orphans.empty:
                st.success("Tidak ada pembayaran yatim.")
            else:
                st.dataframe(orphans, hide_index=True, use_container_width=True, height=280)
        with col_unpaid:
            render_section("Order belum dibayar", "Tidak ada pembayaran valid")
            if unpaid.empty:
                st.success("Semua order sudah dibayar.")
            else:
                columns = ["order_id", "channel", "order_date", "amount", "status"]
                st.dataframe(
                    unpaid[[c for c in columns if c in unpaid.columns]],
                    hide_index=True,
                    use_container_width=True,
                    height=280,
                )

    with tab_rows:
        rejected = load_csv(str(report_dir), "rejected_rows.csv")
        duplicates = load_csv(str(report_dir), "duplicate_orders.csv")
        cross_channel = load_csv(str(report_dir), "cross_channel_duplicates.csv")
        duplicate_payments = load_csv(str(report_dir), "duplicate_payments.csv")

        render_section("Baris ditolak saat ingest", "Tidak punya kunci unik")
        if rejected.empty:
            st.success("Tidak ada baris yang ditolak.")
        else:
            st.dataframe(rejected, hide_index=True, use_container_width=True)

        col_dup, col_cross = st.columns(2)
        with col_dup:
            render_section("Duplikat dalam file", "order_id berulang")
            if duplicates.empty:
                st.success("Tidak ada duplikat dalam file.")
            else:
                columns = [
                    "order_id", "source_file", "channel",
                    "raw_order_date", "raw_amount",
                ]
                st.dataframe(
                    duplicates[[c for c in columns if c in duplicates.columns]],
                    hide_index=True,
                    use_container_width=True,
                    height=280,
                )
        with col_cross:
            render_section("Duplikat antar channel", "Muncul di WEB dan APP")
            if cross_channel.empty:
                st.success("Tidak ada duplikat antar channel.")
            else:
                st.dataframe(
                    cross_channel, hide_index=True, use_container_width=True, height=280
                )

        render_section("Pembayaran ganda", "Lebih dari satu pembayaran valid")
        if duplicate_payments.empty:
            st.success("Tidak ada pembayaran ganda.")
        else:
            st.dataframe(
                duplicate_payments, hide_index=True, use_container_width=True
            )

    with tab_report:
        render_section("Laporan harian", "Ringkasan siap kirim ke tim lain")
        report_path = Path(report_dir) / "daily_report.md"
        if report_path.exists():
            if st.button("Muat ulang laporan"):
                st.cache_data.clear()
            st.markdown(report_path.read_text(encoding="utf-8"))
        else:
            st.info("Laporan harian belum dibuat.")

    st.markdown(
        '<div class="footer">Data Quality Command Center - Python, SQL, Plotly, Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
