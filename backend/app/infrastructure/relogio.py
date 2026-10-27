from datetime import UTC, datetime


class RelogioDoSistema:
    def agora(self) -> datetime:
        return datetime.now(UTC)
