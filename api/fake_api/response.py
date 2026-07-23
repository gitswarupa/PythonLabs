from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class Response:
    status_code: int

    data: object | None = None

    error: str | None = None

    processing_time_ms: int = 0

    request_id: str = field(default_factory=lambda: str(uuid4()))

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self):
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "processing_time_ms": self.processing_time_ms,
            "status_code": self.status_code,
            "data": self.data,
            "error": self.error,
        }

    def __repr__(self):
        return f"<Response [{self.status_code}] request_id={self.request_id}>"
