from .tracing import TraceCollector


def main() -> None:
    traces = TraceCollector()
    with traces.span("incident-workflow", "agent", environment="demo"):
        with traces.span("retrieve-runbook", "retrieval", documents=4):
            pass
        with traces.span("generate-summary", "llm", **{"llm.model": "demo-model", "llm.input_tokens": 320, "llm.output_tokens": 80, "llm.cost_usd": 0.0012}):
            pass
    print(traces.export_json())
    print(traces.report())


if __name__ == "__main__":
    main()
