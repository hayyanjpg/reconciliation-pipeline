from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_renders_without_exception():
    app = AppTest.from_file(str(ROOT / "streamlit" / "dashboard.py"), default_timeout=60)
    app.run()

    assert not app.exception
    assert len(app.tabs) == 5
    assert len(app.selectbox) >= 1
