from __future__ import annotations

import json
import re
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field


SECRET = re.compile(r"(?i)(api[_-]?key|token|password)\s*[=:]\s*[^\s,]+")


@dataclass
class Span:
    name: str
    kind: str
    trace_id: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_id: str | None = None
    started_ns: int = field(default_factory=time.time_ns)
    ended_ns: int | None = None
    status: str = "ok"
    attributes: dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.ended_ns or time.time_ns()
        return (end - self.started_ns) / 1_000_000


class TraceCollector:
    def __init__(self) -> None:
        self.spans: list[Span] = []
        self._stack: list[Span] = []

    @contextmanager
    def span(self, name: str, kind: str = "internal", **attributes):
        trace_id = self._stack[-1].trace_id if self._stack else uuid.uuid4().hex
        parent_id = self._stack[-1].span_id if self._stack else None
        current = Span(name, kind, trace_id, parent_id=parent_id, attributes=self._redact(attributes))
        self._stack.append(current)
        try:
            yield current
        except Exception as exc:
            current.status = "error"
            current.attributes["error.type"] = type(exc).__name__
            raise
        finally:
            current.ended_ns = time.time_ns()
            self._stack.pop()
            self.spans.append(current)

    def report(self) -> dict:
        durations = sorted(span.duration_ms for span in self.spans)
        percentile = lambda p: durations[min(int((len(durations) - 1) * p), len(durations) - 1)] if durations else 0.0
        return {
            "span_count": len(self.spans),
            "error_rate": sum(span.status == "error" for span in self.spans) / len(self.spans) if self.spans else 0.0,
            "p50_ms": round(percentile(0.50), 3),
            "p95_ms": round(percentile(0.95), 3),
            "input_tokens": sum(int(span.attributes.get("llm.input_tokens", 0)) for span in self.spans),
            "output_tokens": sum(int(span.attributes.get("llm.output_tokens", 0)) for span in self.spans),
            "estimated_cost_usd": round(sum(float(span.attributes.get("llm.cost_usd", 0)) for span in self.spans), 6),
        }

    def export_json(self) -> str:
        return json.dumps([{**asdict(span), "duration_ms": span.duration_ms} for span in self.spans], indent=2)

    @staticmethod
    def _redact(attributes: dict) -> dict:
        clean = {}
        for key, value in attributes.items():
            sensitive_key = key.lower() in {"secret", "password", "api_key", "access_token", "refresh_token"}
            if sensitive_key:
                clean[key] = "[REDACTED]"
            elif isinstance(value, str):
                clean[key] = SECRET.sub(lambda m: m.group(1) + "=[REDACTED]", value)
            else:
                clean[key] = value
        return clean
