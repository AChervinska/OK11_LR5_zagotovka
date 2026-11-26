"""
Тести app/drift.py. Дані — детерміновано згенеровані scripts/generate_logs.py
(той самий seed щоразу), тому очікувану поведінку можна перевіряти точно,
а не лише "щось повернулось".
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.drift import compute_drift_report, extract_drift_summary
from scripts.generate_logs import generate_current_batches, generate_reference

REFERENCE = generate_reference()
BATCHES = generate_current_batches()


def test_stable_day_shows_no_drift():
    result = compute_drift_report(REFERENCE, BATCHES["day_03"])
    summary = extract_drift_summary(result)
    assert summary.drifted_columns_share == 0.0
    assert not summary.is_drifted("text_length")
    assert not summary.is_drifted("predicted_label")


def test_feature_drift_day_drifts_text_length_only():
    """День 10 — навмисно змодельований дрейф ОЗНАК без дрейфу цільової
    (підрозділ 3.6 методички) — ключовий тестовий сценарій роботи."""
    result = compute_drift_report(REFERENCE, BATCHES["day_10"])
    summary = extract_drift_summary(result)
    assert summary.is_drifted("text_length")
    assert not summary.is_drifted("predicted_label")


def test_full_drift_day_drifts_both_feature_and_target():
    result = compute_drift_report(REFERENCE, BATCHES["day_18"])
    summary = extract_drift_summary(result)
    assert summary.is_drifted("text_length")
    assert summary.is_drifted("predicted_label")


def test_drift_summary_has_p_value_for_every_configured_column():
    result = compute_drift_report(REFERENCE, BATCHES["day_10"])
    summary = extract_drift_summary(result)
    for column in ["text_length", "latency_ms", "confidence", "predicted_label"]:
        assert column in summary.column_p_values


def test_is_drifted_respects_custom_alpha():
    result = compute_drift_report(REFERENCE, BATCHES["day_10"])
    summary = extract_drift_summary(result)
    # p-value для text_length у день 10 astronomically малий — навіть
    # дуже суворий alpha=1e-100 мав би його впіймати
    assert summary.is_drifted("text_length", alpha=1e-100)
    # а надзвичайно м'який поріг (alpha майже 0) не впіймає жодного дрейфу,
    # окрім хіба що p-value=0.0 рівно
    assert not summary.is_drifted("predicted_label", alpha=1e-100) or (
        summary.column_p_values["predicted_label"] == 0.0
    )
