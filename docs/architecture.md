# Architecture
```text
Exchange/API -> Data Ingestion -> Parquet/DuckDB -> Features -> Strategies -> Backtesting
                                           |                         |
PostgreSQL <-> API/Worker <-> Risk Engine/Kill Switch <-> Paper/Live Execution
                                           |
                                     Dashboard/Alerts
```
Modules: [common](../packages/common), [data](../packages/data), [features](../packages/features), [strategies](../packages/strategies), [risk](../packages/risk), [backtesting](../packages/backtesting), [execution](../packages/execution), [analytics](../packages/analytics).
