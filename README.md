# Your First AI Agent

A real, working AI agent in one file. 107 lines of Python. No frameworks, no abstractions — just the loop that every agent in production actually runs.

## What you get

The complete agent loop — **perceive → decide → act → observe** — repeating until the model stops asking for tools. Plus one real tool (a safe calculator) wired end to end, so you see exactly how tool-calling works. Not pseudocode. Run it.

Language models are genuinely bad at arithmetic. This agent delegates that to Python instead of guessing. That's the entire idea of tools: **delegate what you're bad at**.

## Run it

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # from console.anthropic.com
python first_agent.py
```

About 30 seconds from clone to a working agent.

## The loop is the engine

Everything else in a production agent — memory, evals, multiple agents, guardrails — is built *around* this loop. Understand these 107 lines and you understand what every agent framework is actually doing for you.

Four things worth noticing in the code:

- **The assistant turn is appended verbatim.** The `tool_use` blocks are what the next request needs. Strip them and the loop breaks.
- **Every tool result goes back in a single user message.** One message, all results, in order.
- **There's a hard stop.** Ten turns max, so a misbehaving loop can't run forever. Production agents need this on day one, not day 100.
- **Never `eval()` model output.** The calculator uses a tiny AST-based evaluator — the model can ask for math, it can't ask for code execution.

## Go deeper

- **Free:** the full guided walkthrough of this code — [richchris.com/free](https://richchris.com/free)
- **$9:** [Deploy Your First AI Agent](https://richchris.com/guides) — tool schemas, memory, and a deployment path
- **$39:** Production AI Agents — multi-agent orchestration, retrieval, evals, observability, shipped with a downloadable code repo

## License

MIT — use it, fork it, ship it.
