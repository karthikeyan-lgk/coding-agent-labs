# Coding agent labs

Runnable labs from the Observability Labs videos on tracing and monitoring AI coding agents
(Claude Code, Gemini CLI, Codex) with OpenTelemetry. One folder per video; each has its own README.

| Folder | Video |
| --- | --- |
| [claude-code-ci](claude-code-ci/) | [Claude Code in CI: Trace Every Headless Run with OpenTelemetry](https://www.youtube.com/watch?v=I__8dSsPuyE) |
| [usage-limits](usage-limits/) | [Claude Isn't Counting Your Words (How to Save Tokens in Claude Code)](https://www.youtube.com/watch?v=EaB4RY5l5ko) |
| [background-agents](background-agents/) | [Claude Code Read 52,000 Tokens to Write 4 Words](https://www.youtube.com/watch?v=W1q4JKqgd2A) |
| [graphify](graphify/) | [Graphify’s 71x Claim: Tested with 160 Claude Code Runs](https://www.youtube.com/watch?v=qugfWfvr6rA) |
| [video-builds](video-builds/) | [I Built a 3D Short with Only One Text File](https://www.youtube.com/watch?v=xGFiqQWwP-w) and [Claude Code Animation: HyperFrames vs Remotion, Same Video, Measured](https://www.youtube.com/watch?v=NIcNbLtOnuM) |
| [fable-vs-opus](fable-vs-opus/) | [Fable 5.2 vs Opus 5.5 in Claude Code: Same 5 Prompts, Measured](https://www.youtube.com/watch?v=CeH4KlnmQtY) and [How to Use Claude Code for Free: I Tested 4 Free Models (Real Numbers)](https://www.youtube.com/watch?v=9CluUS52Fdg) |

Everything runs locally with Docker. Claude Code telemetry carries your email and account IDs; every lab's
Collector deletes them before anything is stored.
