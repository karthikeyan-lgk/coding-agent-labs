"""A nightly "release-prep" job that runs headless Claude Code three times.

    uv run --no-project --with opentelemetry-sdk --with opentelemetry-exporter-otlp-proto-http \
        python -I pipeline.py split     # each step on its own: three traces
    ... python -I pipeline.py joined    # one parent span, TRACEPARENT handed to every step: one trace

Uses the Claude Code login (no API key). Each step is one small Haiku prompt in out/repo.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import inject
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

ENDPOINT = "http://127.0.0.1:4318"
REPO = Path(__file__).parent / "out" / "repo"
RUN_ID = time.strftime("%Y%m%d-%H%M%S")
STEPS = [
    ("review", "Review the staged change (git diff --cached) for bugs. Answer in two sentences.",
     "Bash(git diff:*),Read"),
    ("changelog", "Write a one-line CHANGELOG entry for the staged change. Print it, don't edit files.",
     "Bash(git diff:*),Read"),
    ("lint", "Run the linter with `ruff check .` and summarise the result in one sentence.",
     "Read"),  # ruff isn't allowed here, so the shell call gets blocked
]

base_env = os.environ | {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
    "OTEL_TRACES_EXPORTER": "otlp",
    "OTEL_METRICS_EXPORTER": "none",
    "OTEL_LOGS_EXPORTER": "none",
    "OTEL_LOG_TOOL_DETAILS": "1",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": ENDPOINT,
    "OTEL_TRACES_EXPORT_INTERVAL": "1000",
    "ANTHROPIC_API_KEY": "",
}
base_env.pop("TRACEPARENT", None)


def claude(prompt: str, tools: str, extra: dict[str, str]) -> str:
    out = subprocess.run(["claude", "-p", prompt, "--model", "haiku", "--allowedTools", tools],
                         cwd=REPO, env=base_env | extra, capture_output=True, text=True, timeout=300)
    return out.stdout.strip() or f"(exit {out.returncode}) {out.stderr.strip()[:300]}"


def split() -> None:
    for name, prompt, tools in STEPS:
        print(f"[{name}]", claude(prompt, tools, {}), flush=True)


def joined() -> None:
    attrs = {"service.name": "release-prep", "cicd.pipeline.name": "release-prep", "cicd.pipeline.run.id": RUN_ID}
    resource_env = {"OTEL_RESOURCE_ATTRIBUTES": f"cicd.pipeline.name=release-prep,cicd.pipeline.run.id={RUN_ID}"}
    provider = TracerProvider(resource=Resource.create(attrs))
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=f"{ENDPOINT}/v1/traces")))
    tracer = provider.get_tracer("release-prep")
    with tracer.start_as_current_span("release-prep") as root:
        for name, prompt, tools in STEPS:
            with tracer.start_as_current_span(name, attributes={"cicd.pipeline.task.name": name}):
                carrier: dict[str, str] = {}
                inject(carrier)
                print(f"[{name}]", claude(prompt, tools, resource_env | {"TRACEPARENT": carrier["traceparent"]}), flush=True)
        print("trace id:", format(root.get_span_context().trace_id, "032x"), "run id:", RUN_ID)
    provider.shutdown()


{"split": split, "joined": joined}[sys.argv[1]]()
