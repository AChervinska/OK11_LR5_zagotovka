"""
Сервіс метрик: симулює надходження нових "днів" продакшн-даних і
виставляє метрики дрейфу для Prometheus через HTTP-ендпоінт /metrics.

Запуск:
    python scripts/metrics_server.py

ЕТАЛОННЕ РІШЕННЯ — для викладача.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from prometheus_client import Gauge, start_http_server

from app.config import Settings
from app.drift import compute_drift_report, extract_drift_summary

settings = Settings()

DRIFT_SHARE = Gauge("drift_columns_share", "Частка колонок з виявленим дрейфом (0-1)")
COLUMN_P_VALUE = Gauge("drift_column_p_value", "p-value тесту дрейфу для колонки", ["column"])
COLUMN_DRIFTED = Gauge(
    "drift_column_is_drifted", "1, якщо колонка дрейфувала (p < alpha), інакше 0", ["column"]
)


def list_days(data_dir: Path) -> list[str]:
    return sorted(p.stem for p in data_dir.glob("day_*.csv"))


def process_day(reference: pd.DataFrame, data_dir: Path, day: str) -> None:
    current = pd.read_csv(data_dir / f"{day}.csv")
    result = compute_drift_report(reference, current)
    summary = extract_drift_summary(result)

    DRIFT_SHARE.set(summary.drifted_columns_share)
    for column, p_value in summary.column_p_values.items():
        COLUMN_P_VALUE.labels(column=column).set(p_value)
        COLUMN_DRIFTED.labels(column=column).set(
            1.0 if summary.is_drifted(column, settings.drift_alpha) else 0.0
        )

    print(f"{day}: частка дрейфу={summary.drifted_columns_share:.2f}")


def main() -> None:
    data_dir = Path(settings.data_dir)
    reference = pd.read_csv(data_dir / "reference.csv")

    days = list_days(data_dir)
    if not days:
        raise SystemExit("Немає файлів day_*.csv — спершу python scripts/generate_logs.py")

    start_http_server(settings.metrics_port)
    print(f"Метрики доступні на http://localhost:{settings.metrics_port}/metrics")

    for day in days:
        process_day(reference, data_dir, day)
        time.sleep(settings.simulated_day_seconds)

    print("Усі дні оброблено — сервіс продовжує віддавати останні метрики (Ctrl+C для виходу).")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
