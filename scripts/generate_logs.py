"""
Генерація синтетичних логів сервісу /predict (той самий контракт, що
й у ЛР1: predicted_label, confidence, latency_ms — плюс text_length,
проста числова характеристика вхідного тексту) для трьох періодів:

- reference.csv     — базовий період (як мало б виглядати "нормальне" навантаження)
- day_01 .. day_07   — стабільний період, розподіл ЯК У reference
- day_08 .. day_14   — ДРЕЙФ ОЗНАК (text_length) БЕЗ дрейфу цільової
                       (predicted_label лишається розподіленим так само) —
                       навмисно змодельований "хибнотривожний" випадок
                       (підрозділ 3.6 методички)
- day_15 .. day_20   — дрейф ОБОХ: і ознак, і цільової змінної разом —
                       "справжня" проблема, а не хибна тривога

Цей скрипт ГОТОВИЙ (не редагувати) — мета роботи не в генерації даних,
а в їх аналізі. Запуск:
    python scripts/generate_logs.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

N_REFERENCE = 500
N_PER_DAY = 200
N_STABLE_DAYS = 7
N_FEATURE_DRIFT_DAYS = 7
N_FULL_DRIFT_DAYS = 6


def _generate_batch(
    n: int, text_length_mean: float, text_length_std: float, positive_share: float, seed: int
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    text_length = rng.normal(text_length_mean, text_length_std, n).clip(5, None)
    latency_ms = rng.normal(45, 8, n).clip(5, None)
    is_positive = rng.random(n) < positive_share
    predicted_label = np.where(is_positive, "POSITIVE", "NEGATIVE")
    confidence = np.where(is_positive, rng.beta(8, 2, n), rng.beta(7, 2, n))
    return pd.DataFrame(
        {
            "text_length": text_length,
            "latency_ms": latency_ms,
            "predicted_label": predicted_label,
            "confidence": confidence,
        }
    )


def generate_reference() -> pd.DataFrame:
    return _generate_batch(N_REFERENCE, text_length_mean=60, text_length_std=15, positive_share=0.6, seed=0)


def generate_current_batches() -> dict[str, pd.DataFrame]:
    batches: dict[str, pd.DataFrame] = {}
    day = 1

    for _ in range(N_STABLE_DAYS):
        batches[f"day_{day:02d}"] = _generate_batch(N_PER_DAY, 60, 15, 0.6, seed=100 + day)
        day += 1

    for _ in range(N_FEATURE_DRIFT_DAYS):
        batches[f"day_{day:02d}"] = _generate_batch(N_PER_DAY, 110, 20, 0.6, seed=100 + day)
        day += 1

    for _ in range(N_FULL_DRIFT_DAYS):
        batches[f"day_{day:02d}"] = _generate_batch(N_PER_DAY, 115, 25, 0.25, seed=100 + day)
        day += 1

    return batches


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    reference = generate_reference()
    reference.to_csv(DATA_DIR / "reference.csv", index=False)
    print(f"reference.csv: {len(reference)} записів")

    for name, batch in generate_current_batches().items():
        batch.to_csv(DATA_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(batch)} записів")


if __name__ == "__main__":
    main()
