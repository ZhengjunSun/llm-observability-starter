# LLM Observability Starter

[![CI](https://github.com/ZhengjunSun/llm-observability-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/ZhengjunSun/llm-observability-starter/actions/workflows/ci.yml)

A tiny OpenTelemetry-inspired tracing core for LLM and agent applications. It records nested spans, token usage, estimated cost, latency, tool failures, and quality scores, then exports JSON traces and an aggregate service report.

```bash
python -m llm_observability.demo
python -m unittest discover -s tests -v
```

## Signals

- End-to-end traces for agent, model, retrieval, and tool operations
- Parent/child causal relationships
- Token and cost accounting by model
- Error rate and p50/p95 latency
- Quality scores attached to spans
- Secret redaction before export

This is an educational starter, not a replacement for OpenTelemetry, Phoenix, Langfuse, or an enterprise monitoring backend.

## License

MIT
