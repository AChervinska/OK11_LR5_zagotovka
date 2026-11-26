"""Крок 8-9 (поглиблений рівень): тести калібрування порогу та
логіки стійкого дрейфу."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

pytestmark = pytest.mark.advanced

from app.threshold import calibrate_threshold, is_persistent_drift, normalized_wasserstein_distance
from scripts.generate_logs import generate_current_batches, generate_reference

REFERENCE = generate_reference()
BATCHES = generate_current_batches()


def test_identical_distribution_has_near_zero_distance():
    same = REFERENCE.copy()
    assert normalized_wasserstein_distance(REFERENCE["text_length"], same["text_length"]) == pytest.approx(0.0, abs=1e-9)


def test_calibrate_threshold_returns_lower_fpr_for_higher_threshold():
    stable_batches = [BATCHES[f"day_{i:02d}"]["text_length"] for i in range(1, 8)]
    result = calibrate_threshold(
        REFERENCE["text_length"], stable_batches, candidate_thresholds=[0.05, 0.1, 0.3]
    )
    assert result[0.05] >= result[0.1] >= result[0.3]


def test_calibrate_threshold_at_loose_threshold_has_zero_false_positives():
    stable_batches = [BATCHES[f"day_{i:02d}"]["text_length"] for i in range(1, 8)]
    result = calibrate_threshold(REFERENCE["text_length"], stable_batches, candidate_thresholds=[0.3])
    assert result[0.3] == 0.0


def test_is_persistent_drift_requires_trailing_consecutive_true():
    assert is_persistent_drift([True, True, False], min_consecutive=3) is False
    assert is_persistent_drift([False, True, True, True], min_consecutive=3) is True


def test_is_persistent_drift_false_when_not_enough_history():
    assert is_persistent_drift([True, True], min_consecutive=3) is False


def test_is_persistent_drift_ignores_older_flags_before_the_window():
    # Перший False поза вікном (min_consecutive=2) не повинен впливати —
    # важать лише ОСТАННІ 2 елементи.
    assert is_persistent_drift([False, True, True], min_consecutive=2) is True
