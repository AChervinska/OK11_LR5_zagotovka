# ЛР5 · Виявлення дрейфу даних та якості моделі

Повний текст інструкції — у файлі `ЛР5_Методичні_вказівки.docx`. Цей
README — лише технічна навігація.

На відміну від ЛР1-ЛР4, тут немає одного "живого" сервісу, який
переноситься з роботи в роботу — є аналітичний стек: Evidently
(обчислення дрейфу) → Prometheus (зберігання метрик у часі) → Grafana
(візуалізація). Дані — синтетичні логи, що імітують те, що логував би
middleware сервісу з ЛР1.

Два рівні:

- **Базовий (обов'язковий)** — кроки 1-6: генерація даних, обчислення
  дрейфу через Evidently, сервіс метрик, Prometheus.
- **Поглиблений (додатково)** — кроки 7-10: калібрування порогу за
  false positive rate, сценарій дрейфу без дрейфу цільової, Grafana,
  логіка "стійкого" дрейфу для алертів.

## Структура

```
app/
  config.py       — готові налаштування (не редагувати)
  drift.py         — TODO: compute_drift_report(), extract_drift_summary() (кроки 3-4)
  threshold.py      — TODO: calibrate_threshold(), is_persistent_drift() (кроки 8-9)
scripts/
  generate_logs.py    — готовий, генерує data/*.csv (не редагувати)
  calculate_drift.py   — готовий CLI-скрипт одноразового звіту
  metrics_server.py     — готовий сервіс метрик для Prometheus
prometheus/
  prometheus.yml          — конфігурація скрейпу
grafana/
  provisioning/...          — TODO: вказати абсолютний шлях (крок 10)
  dashboards/drift_dashboard.json
tests/                       — усі готові, не редагувати
requirements.txt
pytest.ini
verify.sh
```

## Передумови

```bash
pip install -r requirements.txt
```

Prometheus — окремий бінарник (не Python-пакет), встановлення описано
в методичці, крок 5. Grafana — крок 10 (поглиблений рівень), теж окремий
бінарник/пакет.

## Порядок виконання

1. `python scripts/generate_logs.py` — згенерувати дані.
2. Ознайомитись зі структурою (app/config.py, схема логів).
3. Реалізувати `compute_drift_report()`.
4. Реалізувати `extract_drift_summary()`.
5. Встановити Prometheus, `python scripts/calculate_drift.py day_10` — перший звіт.
6. `python scripts/metrics_server.py` + Prometheus — перевірити в UI, звіт базового рівня.

Поглиблений рівень:

7. `pytest tests/test_threshold.py -v -m advanced` (до реалізації — падає).
8. Реалізувати `calibrate_threshold()`.
9. Реалізувати `is_persistent_drift()`.
10. Grafana — дашборд, звіт поглибленого рівня.

## Важливо

`bash verify.sh` вимагає встановленого `prometheus` у PATH — якщо
його немає, ця частина перевірки пропускається з попередженням, а не
падає.
