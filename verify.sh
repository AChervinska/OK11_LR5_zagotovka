#!/usr/bin/env bash
# Наскрізна перевірка ЛР5. Запускати з кореня репозиторію.
#
# Використання:
#   bash verify.sh            # базовий рівень
#   bash verify.sh advanced   # додатково перевіряє калібрування порогу

set -euo pipefail
FAILED=0
pass() { echo "OK: $1"; }
fail() { echo "FAIL: $1"; FAILED=1; }

echo "== Генерація даних =="
python scripts/generate_logs.py

echo "== Тести (базовий рівень) =="
if pytest -m "not advanced" -v; then pass "базові тести"; else fail "базові тести"; fi

echo "== Одноразовий звіт (день 10 — очікується дрейф лише text_length) =="
python scripts/calculate_drift.py day_10

echo "== Сервіс метрик + Prometheus (30 секунд симуляції) =="
python scripts/metrics_server.py > /tmp/ok11_lr5_metrics.log 2>&1 &
METRICS_PID=$!
sleep 5

if curl -sf http://localhost:8001/metrics | grep -q "^drift_columns_share"; then
    pass "сервіс метрик віддає /metrics"
else
    fail "сервіс метрик недоступний"
fi

if command -v prometheus >/dev/null 2>&1; then
    prometheus --config.file=prometheus/prometheus.yml \
        --storage.tsdb.path="$(mktemp -d)" \
        --web.listen-address=:9090 > /tmp/ok11_lr5_prometheus.log 2>&1 &
    PROM_PID=$!
    sleep 5
    if curl -sf 'http://localhost:9090/api/v1/query?query=drift_columns_share' | grep -q '"status":"success"'; then
        pass "Prometheus реально скрейпить метрики"
    else
        fail "Prometheus не бачить метрики"
    fi
    kill "$PROM_PID" 2>/dev/null || true
else
    echo "Prometheus не встановлено в PATH — пропускаю цю перевірку (встановіть за посиланням у методичці, крок 5)"
fi

kill "$METRICS_PID" 2>/dev/null || true
wait 2>/dev/null || true

if [ "${1:-}" = "advanced" ]; then
    echo "== Тести (поглиблений рівень) =="
    if pytest -m advanced -v; then pass "поглиблені тести"; else fail "поглиблені тести"; fi
fi

if [ "$FAILED" -eq 0 ]; then
    echo ""
    echo "УСІ ПЕРЕВІРКИ ПРОЙДЕНО"
    exit 0
else
    echo ""
    echo "Є ПОМИЛКИ — див. FAIL вище"
    exit 1
fi
