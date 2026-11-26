"""
Одноразовий аналіз дрейфу: reference проти одного дня поточних даних.
Зберігає HTML-звіт (для візуального огляду) і друкує короткий підсумок.

Запуск:
    python scripts/calculate_drift.py day_10

ЕТАЛОННЕ РІШЕННЯ — для викладача.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app.config import Settings
from app.drift import compute_drift_report, extract_drift_summary


def main() -> None:
    if len(sys.argv) != 2:
        print("Використання: python scripts/calculate_drift.py <день, наприклад day_10>")
        sys.exit(1)

    day = sys.argv[1]
    settings = Settings()
    data_dir = Path(settings.data_dir)
    reports_dir = Path(settings.reports_dir)
    reports_dir.mkdir(exist_ok=True)

    reference = pd.read_csv(data_dir / "reference.csv")
    current = pd.read_csv(data_dir / f"{day}.csv")

    result = compute_drift_report(reference, current)
    html_path = reports_dir / f"drift_{day}.html"
    result.save_html(str(html_path))

    summary = extract_drift_summary(result)
    print(f"Звіт збережено: {html_path}")
    print(f"Частка «дрейфованих» колонок: {summary.drifted_columns_share:.1%}")
    print()
    header = f"{'колонка':<20}{'p-value':>12}{'дрейф (alpha=' + str(settings.drift_alpha) + ')':>22}"
    print(header)
    for column, p_value in summary.column_p_values.items():
        drifted = "ТАК" if summary.is_drifted(column, settings.drift_alpha) else "ні"
        print(f"{column:<20}{p_value:>12.2e}{drifted:>22}")


if __name__ == "__main__":
    main()
