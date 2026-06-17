from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    exchange_name: str = "binance"
    exchange_api_key: str = ""
    exchange_secret: str = ""
    database_url: str = "postgresql://crtrcod:crtrcod@localhost:5432/crtrcod"
    redis_url: str = "redis://localhost:6379/0"
    mlflow_tracking_uri: str = "http://localhost:5000"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    environment: str = "development"
    log_level: str = "INFO"
    max_capital_per_strategy_pct: float = 0.05
    max_risk_per_trade_pct: float = 0.0025
    max_daily_loss_pct: float = 0.01
    max_concurrent_positions: int = 2
    max_spread_bps: float = 5.0
    max_consecutive_losses: int = 5
    data_staleness_multiplier: float = 2.0
    model_config = {"env_file": ".env", "case_sensitive": False}


def get_settings() -> Settings:
    return Settings()
