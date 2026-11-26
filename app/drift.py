"""
Обчислення дрейфу через Evidently — спільна логіка для одноразового
CLI-звіту (scripts/calculate_drift.py) і для сервісу метрик
(scripts/metrics_server.py), щоб не дублювати побудову Report.

Зафіксована версія evidently==0.7.21 — API цієї бібліотеки істотно
змінювався між мажорними версіями (детальніше — підрозділ 3.2
методички); приклади з інтернету під старіші версії (Report(metrics=[
DataDriftPreset()]) з інтерфейсом profile_sections тощо) із цим кодом
несумісні.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from evidently import Dataset, DataDefinition, Report
from evidently.core.report import Snapshot
from evidently.presets import DataDriftPreset

NUMERICAL_COLUMNS = ["text_length", "latency_ms", "confidence"]
CATEGORICAL_COLUMNS = ["predicted_label"]


def _schema() -> DataDefinition:
    return DataDefinition(
        numerical_columns=NUMERICAL_COLUMNS, categorical_columns=CATEGORICAL_COLUMNS
    )


@dataclass
class DriftSummary:
    """Компактне представлення результату Report — те, що реально
    потрібно для алертів і метрик, без обходу вкладеної структури
    result.dict() щоразу заново."""

    drifted_columns_share: float
    # колонка -> p-value (менше = сильніший дрейф)
    column_p_values: dict[str, float]

    def is_drifted(self, column: str, alpha: float = 0.05) -> bool:
        return self.column_p_values[column] < alpha


def compute_drift_report(reference, current):
    schema = _schema()

    ref_ds = Dataset.from_pandas(
        reference,
        data_definition=schema
    )

    cur_ds = Dataset.from_pandas(
        current,
        data_definition=schema
    )

    report = Report(metrics=[DataDriftPreset()])

    return report.run(
        reference_data=ref_ds,
        current_data=cur_ds
    )


def extract_drift_summary(result):
    data = result.dict()

    drifted_share = 0.0
    p_values = {}

    for metric in data["metrics"]:
        name = metric["metric_name"]

        if name.startswith("DriftedColumnsCount"):
            drifted_share = metric["value"]["share"]

        elif name.startswith("ValueDrift(column="):
            column = metric["config"]["column"]
            p_values[column] = metric["value"]

    return DriftSummary(
        drifted_columns_share=drifted_share,
        column_p_values=p_values
    )
