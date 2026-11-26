"""
Калібрування порогу дрейфу та логіка "стійкого" (а не одноразового)
дрейфу для алертів — поглиблений рівень, кроки 8-9.
"""

from __future__ import annotations

import pandas as pd
from scipy.stats import wasserstein_distance


def normalized_wasserstein_distance(reference: pd.Series, current: pd.Series) -> float:
    """
    Той самий спосіб нормалізації, що використовує Evidently для
    method="wasserstein" (перевірте це самостійно експериментом,
    підрозділ 3.8 методички): "сира" відстань Вассерштейна, поділена
    на стандартне відхилення REFERENCE-розподілу. Завдяки цьому той
    самий поріг (наприклад, 0.1) має однаковий сенс незалежно від
    масштабу конкретної ознаки (секунди затримки чи символи довжини
    тексту).

    Готова функція (не редагувати) — використовується у TODO нижче.
    """
    return wasserstein_distance(reference, current) / reference.std()


def calibrate_threshold(
    reference,
    stable_batches,
    candidate_thresholds
):
    fpr_by_threshold = {}

    for threshold in candidate_thresholds:
        false_positives = sum(
            normalized_wasserstein_distance(
                reference, batch
            ) > threshold
            for batch in stable_batches
        )

        fpr_by_threshold[threshold] = (
            false_positives / len(stable_batches)
        )

    return fpr_by_threshold


def is_persistent_drift(drift_flags, min_consecutive):
    if len(drift_flags) < min_consecutive:
        return False

    return all(drift_flags[-min_consecutive:])
