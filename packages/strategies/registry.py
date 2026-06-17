from .base_strategy import BaseStrategy


class StrategyRegistry:
    _items: dict[str, type[BaseStrategy]] = {}

    @classmethod
    def register(cls, strategy_cls: type[BaseStrategy]) -> None:
        cls._items[strategy_cls.strategy_id] = strategy_cls

    @classmethod
    def get(cls, strategy_id: str) -> BaseStrategy:
        return cls._items[strategy_id]()

    @classmethod
    def list_all(cls) -> list[str]:
        return sorted(cls._items)


def register_strategy(cls: type[BaseStrategy]) -> type[BaseStrategy]:
    StrategyRegistry.register(cls)
    return cls
