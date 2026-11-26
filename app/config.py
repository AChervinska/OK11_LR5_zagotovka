"""Конфігурація через змінні середовища — той самий підхід, що в ЛР1-ЛР4."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OK11_", env_file=".env", extra="ignore")

    data_dir: str = "data"
    reports_dir: str = "reports"

    # Поріг p-value для "дрейф є" (крок 4). 0.05 — типове значення в
    # статистиці, але саме воно і є предметом обґрунтування в кроці 8
    # (поглиблений рівень) — не приймайте його на віру без перевірки.
    drift_alpha: float = 0.05

    # Скільки ПОСПІЛЬ днів з дрейфом потрібно, щоб визнати його стійким,
    # а не одноразовим викидом (крок 9, поглиблений рівень).
    consecutive_days_for_alert: int = 3

    # Порт, на якому metrics_server.py віддає /metrics для Prometheus.
    metrics_port: int = 8001

    # Пауза між "днями" симуляції в metrics_server.py (секунди).
    # Замало для реального виробництва (там — часи чи дні), але зручно
    # для спостереження за графіком у Grafana під час заняття.
    simulated_day_seconds: float = 5.0
