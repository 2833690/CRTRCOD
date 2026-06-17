from packages.common.types import KillSwitchState


class KillSwitch:
    def __init__(self, redis_client=None, db_session=None):
        self.redis = redis_client
        self.db = db_session
        self.state = KillSwitchState.ACTIVE

    def get_state(self) -> KillSwitchState:
        val = (
            self.redis.get("crtrcod:kill_switch")
            if self.redis and hasattr(self.redis, "get")
            else None
        )
        return KillSwitchState(int(val)) if val is not None else self.state

    def set_state(self, state: KillSwitchState, actor: str, reason: str) -> None:
        self.state = state
        if self.redis and hasattr(self.redis, "set"):
            self.redis.set("crtrcod:kill_switch", int(state))
        if self.db and hasattr(self.db, "audit_log"):
            self.db.audit_log.append(
                {
                    "actor": actor,
                    "action": "kill_switch.set",
                    "reason": reason,
                    "after_value": {"state": int(state)},
                }
            )

    def is_trading_allowed(self) -> bool:
        return self.get_state() == KillSwitchState.ACTIVE

    def emergency_stop(self, actor: str) -> None:
        self.set_state(KillSwitchState.EMERGENCY, actor, "emergency_stop")
