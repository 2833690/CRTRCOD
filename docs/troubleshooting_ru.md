# CRTRCOD — почему «не работает» и как быстро проверить

## Главная причина в текущем окружении

В этой среде `uv sync` не смог скачать зависимости с PyPI из-за сетевой/tunnel ошибки. После этого Python не видит runtime-пакеты (`polars`, `fastapi`, `sqlalchemy`, `ccxt` и т.д.), поэтому тесты падают на `ModuleNotFoundError`.

Это не ошибка импорта внутри CRTRCOD: зависимости просто не установлены.

## Быстрая диагностика

Запустите doctor-команду, она не требует внешних зависимостей:

```bash
python scripts/doctor.py
```

Если увидите `missing; run uv sync`, выполните установку зависимостей в окружении с доступом к PyPI:

```bash
uv sync
uv run pytest tests/ -v
```

## Если PyPI заблокирован

1. Проверьте DNS/сеть до `pypi.org`.
2. Настройте корпоративный proxy или internal package mirror.
3. Повторите `uv sync`.
4. Не запускайте live/paper workflows до успешных `ruff`, `mypy`, `pytest`.

## Проверка без установленных зависимостей

Можно проверить синтаксис локального кода:

```bash
python -m py_compile $(find packages apps scripts -name '*.py')
ruff check .
```

## Правильный порядок запуска v2

```bash
python scripts/doctor.py
uv sync
uv run ruff check .
uv run mypy packages/ apps/ --ignore-missing-imports
uv run pytest tests/ -v
docker compose -f docker/docker-compose.yml up -d
uv run uvicorn apps.api.main:app --reload
```
