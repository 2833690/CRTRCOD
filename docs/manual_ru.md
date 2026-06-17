# CRTRCOD v2 — руководство на русском языке

> **Важно:** CRTRCOD не гарантирует прибыль. Это инженерная платформа для исследований, тестирования гипотез, paper trading и контролируемого запуска spot-стратегий. Не используйте ключи с правом вывода средств.

## 1. Что такое CRTRCOD

CRTRCOD — модульная research-first платформа для криптовалютной spot-торговли. Проект разделён на независимые слои:

1. **Data** — загрузка OHLCV через CCXT, поиск пропусков, запись в Parquet/DuckDB.
2. **Features** — индикаторы и рыночные режимы без lookahead bias.
3. **Strategies** — торговые гипотезы с единым интерфейсом `BaseStrategy`.
4. **Backtesting** — комиссии, проскальзывание, метрики, отчёты и parameter sweep.
5. **Risk** — kill switch, лимиты, circuit breakers, проверка каждого ордера.
6. **Execution** — симулятор fill, paper trader, live adapter.
7. **Apps** — FastAPI API, Celery worker, Streamlit dashboard.
8. **Ops** — Docker Compose, Alembic, CI, документация.

## 2. Быстрый старт

```bash
uv sync
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d
uv run ruff check .
uv run pytest tests/ -v
```

Если `uv sync` не может скачать зависимости из-за сети, сначала проверьте доступ к PyPI. Без установленных зависимостей тесты, использующие `polars`, `fastapi`, `sqlalchemy`, `ccxt`, не запустятся.

## 3. Настройка `.env`

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

Минимум для локальной разработки:

- `DATABASE_URL=postgresql://crtrcod:crtrcod@localhost:5432/crtrcod`
- `REDIS_URL=redis://localhost:6379/0`
- `EXCHANGE_NAME=binance`

Для реального API ключа биржи:

- включайте **только trade permissions**;
- **withdrawal permissions должны быть выключены**;
- ключи нельзя коммитить в Git;
- ключи нельзя отправлять в alerts/logs.

## 4. Как устроен поток данных

```text
CCXT exchange
  -> CCXTClient.fetch_ohlcv()
  -> OHLCVFetcher.fetch_and_store()
  -> validate_dataframe()
  -> GapDetector.find_gaps()
  -> ParquetWriter.write()
  -> DuckDBClient.get_ohlcv()
  -> IndicatorEngine.add_all()
  -> Strategy.populate_entry_signal()
  -> RiskEngine.validate_order()
  -> FillSimulator/PaperTrader или LiveAdapter
```

Главная идея: стратегия не должна видеть будущие данные. Поэтому индикаторы используют `.shift(1)`, а risk engine повторно проверяет условия непосредственно перед исполнением.

## 5. Как добавить новую стратегию

1. Создайте файл в `packages/strategies/`.
2. Унаследуйте класс от `BaseStrategy`.
3. Задайте `strategy_id`, `version`, `timeframe`, `min_candles`.
4. Реализуйте методы:
   - `populate_indicators()` — только с shift на вычисленных колонках;
   - `populate_entry_signal()` — добавляет `entry_long` и `entry_short`;
   - `populate_exit_signal()` — добавляет `exit_long` и `exit_short`;
   - `confirm_entry()` — live-фильтры: spread, expected edge, fees/slippage.
5. Добавьте декоратор `@register_strategy`.
6. Добавьте unit/regression тест.

Пример минимального паттерна:

```python
@register_strategy
class MyStrategy(BaseStrategy):
    strategy_id = "my_strategy_v1"
    version = "1.0.0"
    timeframe = "5m"
    min_candles = 100

    def populate_indicators(self, df):
        return IndicatorEngine().add_ema(df, 21)

    def populate_entry_signal(self, df):
        return df.with_columns((pl.col("close") > pl.col("ema_21")).alias("entry_long"))

    def populate_exit_signal(self, df):
        return df.with_columns((pl.col("close") < pl.col("ema_21")).alias("exit_long"))
```

## 6. Как работает risk engine

`RiskEngine.validate_order()` — обязательный gate перед paper/live исполнением. Проверки идут fail-fast:

1. Kill switch не блокирует торговлю.
2. Daily loss меньше лимита.
3. Размер позиции не превышает лимит.
4. Количество открытых позиций в норме.
5. Spread не выше допустимого.
6. Данные не устарели.

Результат всегда один из:

- `ALLOW` — ордер можно исполнять;
- `REDUCE` — ордер допустим только после уменьшения размера;
- `REJECT` — ордер запрещён.

Каждый вызов пишет audit-событие, чтобы оператор мог восстановить причину решения.

## 7. Kill switch

Состояния:

| State | Значение | Что означает |
|---|---:|---|
| ACTIVE | 0 | Торговля разрешена |
| PAUSED | 1 | Новые входы запрещены, позиции удерживаются |
| CLOSED | 2 | Закрыть позиции, новые входы запрещены |
| EMERGENCY | 3 | Срочно выйти и отключить торговлю |

Проверка через API:

```bash
curl http://localhost:8000/v1/risk/status
```

Пауза торговли:

```bash
curl -X POST http://localhost:8000/v1/risk/kill-switch \
  -H 'Content-Type: application/json' \
  -d '{"state":1,"reason":"manual operator pause"}'
```

## 8. Paper trading перед live

Перед live-режимом стратегия должна пройти:

- reproducible backtest;
- out-of-sample validation;
- walk-forward validation;
- Monte Carlo stress check;
- paper trading минимум несколько торговых дней;
- проверку fee/slippage impact;
- операторское approval через API.

## 9. Live trading правила

Live trading запрещён, если:

- kill switch не `ACTIVE`;
- нет operator approval;
- ключ биржи имеет withdrawal permissions;
- стратегия не прошла checklist;
- daily loss limit превышен;
- данные устарели;
- spread выше лимита.

## 10. Команды оператора

```bash
# Проверка стиля
uv run ruff check .

# Проверка типов
uv run mypy packages/ apps/ --ignore-missing-imports

# Тесты
uv run pytest tests/ -v

# API локально
uv run uvicorn apps.api.main:app --reload

# Worker локально
uv run celery -A apps.worker.celery_app worker --loglevel=info

# Dashboard локально
uv run streamlit run apps/dashboard/main.py
```

## 11. v2 stability checklist

- Все секреты вынесены в `.env`.
- Логи и alerts маскируют секреты.
- Risk limits immutable через frozen dataclass.
- Strategy registry централизует доступ к стратегиям.
- Docker Compose поднимает Postgres/Redis/MLflow/Adminer.
- Alembic migration создаёт базовые таблицы.
- CI запускает lint, types, tests.
- README и docs описывают запуск и риски.

## 12. Частые ошибки

### `ModuleNotFoundError: polars`

Зависимости не установлены. Выполните:

```bash
uv sync
```

### `uv sync` не может скачать пакеты

Проверьте сеть, proxy/VPN, доступ к `https://pypi.org/simple/`.

### API ключи случайно попали в файл

Сразу удалите ключи, перевыпустите их на бирже и убедитесь, что `.env` в `.gitignore`.

### Стратегия показывает слишком хороший backtest

Проверьте lookahead bias, комиссии, slippage, survivorship bias, режимы рынка и sample size.
