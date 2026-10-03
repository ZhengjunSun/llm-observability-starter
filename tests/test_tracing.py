import unittest

from llm_observability import TraceCollector


class TracingTests(unittest.TestCase):
    def test_nested_spans_and_usage(self):
        collector = TraceCollector()
        with collector.span("root", "agent"):
            with collector.span("model", "llm", **{"llm.input_tokens": 10, "llm.output_tokens": 4, "llm.cost_usd": 0.002}):
                pass
        self.assertEqual(len(collector.spans), 2)
        self.assertEqual(collector.spans[0].parent_id, collector.spans[1].span_id)
        self.assertEqual(collector.report()["input_tokens"], 10)

    def test_error_is_recorded(self):
        collector = TraceCollector()
        with self.assertRaises(RuntimeError):
            with collector.span("tool", "tool"):
                raise RuntimeError("failed")
        self.assertEqual(collector.report()["error_rate"], 1.0)

    def test_secrets_are_redacted(self):
        collector = TraceCollector()
        with collector.span("model", api_key="not-a-real-key"):
            pass
        self.assertEqual(collector.spans[0].attributes["api_key"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
