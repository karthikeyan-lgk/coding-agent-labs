# Coding agent labs

Runnable labs from the Observability Labs videos on tracing and monitoring AI coding agents
(Claude Code, Gemini CLI, Codex) with OpenTelemetry. One folder per video; each has its own README.

| Folder | Video |
| --- | --- |
| [claude-code-ci](claude-code-ci/) | [Claude Code in CI: Trace Every Headless Run with OpenTelemetry](https://www.youtube.com/watch?v=I__8dSsPuyE) |

Everything runs locally with Docker. Claude Code telemetry carries your email and account IDs; every lab's
Collector deletes them before anything is stored.
