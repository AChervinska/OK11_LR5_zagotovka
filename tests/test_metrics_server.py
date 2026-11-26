"""
Тест process_day() зі scripts/metrics_server.py — перевіряє, що Gauge'и
Prometheus справді оновлюються коректними значеннями, без реального
підняття HTTP-сервера (start_http_server) у тестах.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_logs import generate_current_batches, generate_reference
from scripts.metrics_server import COLUMN_DRIFTED, COLUMN_P_VALUE, DRIFT_SHARE, process_day


def test_process_day_updates_gauges_for_stable_day(tmp_path):
    reference = generate_reference()
    batches = generate_current_batches()
    data_dir = tmp_path
    batches["day_03"].to_csv(data_dir / "day_03.csv", index=False)

    process_day(reference, data_dir, "day_03")

    assert DRIFT_SHARE._value.get() == 0.0
    assert COLUMN_DRIFTED.labels(column="text_length")._value.get() == 0.0


def test_process_day_updates_gauges_for_feature_drift_day(tmp_path):
    reference = generate_reference()
    batches = generate_current_batches()
    data_dir = tmp_path
    batches["day_10"].to_csv(data_dir / "day_10.csv", index=False)

    process_day(reference, data_dir, "day_10")

    assert DRIFT_SHARE._value.get() == 0.25
    assert COLUMN_DRIFTED.labels(column="text_length")._value.get() == 1.0
    assert COLUMN_DRIFTED.labels(column="predicted_label")._value.get() == 0.0
    assert COLUMN_P_VALUE.labels(column="text_length")._value.get() < 1e-50
