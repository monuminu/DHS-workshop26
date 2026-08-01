"""Workshop helpers: a single, backend-agnostic way to turn on tracing.

Mirrors :mod:`workshop_utils.clients`. One environment variable —
``TRACE_BACKEND`` — chooses where OpenTelemetry spans are sent. The notebook
body never changes: it calls :func:`setup_tracing`, then runs agents.

Agent Framework emits standard **OpenTelemetry GenAI** spans, so any OTLP
backend can read them. The workshop ships three ready-made choices:

===============  ==========================================================
``console``      Spans print to stdout. No install, no server. (default)
``phoenix``      `Arize Phoenix <https://github.com/Arize-ai/phoenix>`_ —
                 open source, runs locally, nothing leaves your machine.
``langfuse``     `Langfuse <https://langfuse.com>`_ Cloud (or self-hosted) —
                 hosted UI, needs a public/secret key pair.
``otlp``         Any other OTLP/HTTP collector (Jaeger, Aspire, App Insights
                 via a collector, Grafana Tempo, …).
``none``         Tracing off.
===============  ==========================================================

Usage (in the notebook)::

    from workshop_utils import setup_tracing
    setup_tracing()          # reads TRACE_BACKEND from .env
    setup_tracing("phoenix") # or force one explicitly

Running a backend locally:

* **Phoenix** — ``uvx phoenix serve`` (or ``docker run -p 6006:6006 -p 4317:4317
  arizephoenix/phoenix:latest``), then open http://localhost:6006.
  Installing Phoenix with ``uvx``/Docker keeps its dependencies out of the
  workshop virtualenv, which pins its own OpenTelemetry versions.
* **Langfuse** — sign up at https://cloud.langfuse.com, create a project, and
  copy the public/secret keys into your ``.env``.
"""

from __future__ import annotations

import base64
import os

from dotenv import load_dotenv

load_dotenv()

__all__ = ["setup_tracing", "current_trace_backend", "SUPPORTED_TRACE_BACKENDS"]

SUPPORTED_TRACE_BACKENDS = ("console", "phoenix", "langfuse", "otlp", "none")

# Where a locally-run Phoenix listens for OTLP/HTTP traces.
PHOENIX_DEFAULT_ENDPOINT = "http://localhost:6006"
LANGFUSE_DEFAULT_HOST = "https://cloud.langfuse.com"


def current_trace_backend() -> str:
    """Return the configured trace backend id, defaulting to ``console``."""
    return os.getenv("TRACE_BACKEND", "console").strip().lower()


def _otlp_http_exporter(endpoint: str, headers: dict[str, str] | None = None):
    """Build an OTLP/HTTP span exporter, with a friendly install hint."""
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    except ModuleNotFoundError as exc:  # pragma: no cover - install hint
        raise ModuleNotFoundError(
            "OTLP/HTTP exporter missing. Install with: "
            "uv pip install opentelemetry-exporter-otlp-proto-http"
        ) from exc
    return OTLPSpanExporter(endpoint=endpoint, headers=headers or {})


def setup_tracing(backend: str | None = None, *, enable_sensitive_data: bool = True) -> str:
    """Configure OpenTelemetry for the chosen backend and return its id.

    Args:
        backend: One of :data:`SUPPORTED_TRACE_BACKENDS`. Defaults to the
            ``TRACE_BACKEND`` environment variable, then ``console``.
        enable_sensitive_data: Include prompts and completions in spans. On by
            default because seeing the actual messages is the point of the
            exercise — turn it **off** for anything with real user data.

    Returns:
        The backend id that was configured.

    Raises:
        ValueError: for an unknown backend, or a backend missing its config.
    """
    backend = (backend or current_trace_backend()).strip().lower()
    from agent_framework.observability import configure_otel_providers

    # --- off ------------------------------------------------------------------
    if backend == "none":
        print("Tracing disabled (TRACE_BACKEND=none).")
        return backend

    # --- console: spans print inline, no server needed -------------------------
    if backend == "console":
        configure_otel_providers(
            enable_console_exporters=True,
            enable_sensitive_data=enable_sensitive_data,
        )
        print("Tracing → console. Spans will print below each agent run.")
        return backend

    # --- Phoenix: open source, runs locally -----------------------------------
    # `uvx phoenix serve` → UI on :6006, OTLP/HTTP on :6006/v1/traces.
    if backend == "phoenix":
        base = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", PHOENIX_DEFAULT_ENDPOINT).rstrip("/")
        headers = {}
        # Phoenix Cloud (and auth-enabled self-hosted) needs an API key.
        if api_key := os.getenv("PHOENIX_API_KEY"):
            headers["Authorization"] = f"Bearer {api_key}"
        configure_otel_providers(
            exporters=[_otlp_http_exporter(f"{base}/v1/traces", headers)],
            enable_sensitive_data=enable_sensitive_data,
        )
        print(f"Tracing → Phoenix at {base}. Open {base} to watch traces arrive.")
        return backend

    # --- Langfuse: hosted (cloud) or self-hosted -------------------------------
    # OTLP/HTTP only — Langfuse does not accept gRPC. Auth is HTTP Basic with
    # base64(public_key:secret_key).
    if backend == "langfuse":
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        if not (public_key and secret_key):
            raise ValueError(
                "TRACE_BACKEND=langfuse needs LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY. "
                "Create a project at https://cloud.langfuse.com and copy its keys into .env."
            )
        host = os.getenv("LANGFUSE_HOST", LANGFUSE_DEFAULT_HOST).rstrip("/")
        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        configure_otel_providers(
            exporters=[
                _otlp_http_exporter(
                    f"{host}/api/public/otel/v1/traces",
                    {"Authorization": f"Basic {auth}", "x-langfuse-ingestion-version": "4"},
                )
            ],
            enable_sensitive_data=enable_sensitive_data,
        )
        print(f"Tracing → Langfuse at {host}. Open it and look under Tracing → Traces.")
        return backend

    # --- any other OTLP/HTTP collector ----------------------------------------
    # Standard OTel env vars: OTEL_EXPORTER_OTLP_ENDPOINT (+ optional headers as
    # "k=v,k2=v2"). Works with Jaeger, Aspire, Tempo, an OTel Collector, etc.
    if backend == "otlp":
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not endpoint:
            raise ValueError("TRACE_BACKEND=otlp needs OTEL_EXPORTER_OTLP_ENDPOINT.")
        raw = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
        headers = dict(
            part.split("=", 1) for part in raw.split(",") if "=" in part
        )
        configure_otel_providers(
            exporters=[_otlp_http_exporter(f"{endpoint.rstrip('/')}/v1/traces", headers)],
            enable_sensitive_data=enable_sensitive_data,
        )
        print(f"Tracing → OTLP collector at {endpoint}.")
        return backend

    raise ValueError(
        f"Unknown TRACE_BACKEND={backend!r}. "
        f"Supported: {', '.join(SUPPORTED_TRACE_BACKENDS)}."
    )
