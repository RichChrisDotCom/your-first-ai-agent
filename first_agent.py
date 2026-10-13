"""
first_agent.py — a real, working AI agent in one file.

A free sample from Rich Chris (richchris.com).
  Go deeper:  the $9 "Deploy Your First AI Agent" guide.
  Go to prod: the $39 "Production AI Agents" flagship — the multi-agent
              pattern, retrieval, evals, observability + a downloadable code repo.

Setup (about 30 seconds):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."     # from console.anthropic.com
    python first_agent.py
"""
import ast
import json
import operator

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-sonnet-4-6"      # Sonnet is the right call for a first agent: fast + cheap

# --- A TOOL ---------------------------------------------------------------
# To the MODEL, a tool is just three things: a name, a description, and a
# JSON schema of its arguments. To YOUR code, it's a plain Python function
# that you choose to run when the model asks for it.
#
# We give the model a calculator because language models are genuinely bad at
# arithmetic — this is the cleanest example of "delegate what you're bad at."

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow}


def _eval(node):
    """A tiny, SAFE math evaluator. Never run eval() on model output."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand)
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    return str(_eval(ast.parse(expression, mode="eval").body))


TOOLS = [{
    "name": "calculator",
    "description": "Evaluate an arithmetic expression. Use this instead of "
                   "guessing at any calculation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "e.g. '2 ** 10 * 3'"}
        },
        "required": ["expression"],
    },
}]


# --- THE AGENT LOOP -------------------------------------------------------
# perceive -> decide -> act -> observe, repeating until the model stops
# asking for tools. This loop is the whole engine. Everything else in a
# production agent (memory, evals, multiple agents) is built around it.

def run(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    for _ in range(10):  # a hard stop so a misbehaving loop can't run forever
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system="You are a precise assistant. Use tools instead of guessing.",
            tools=TOOLS,
            messages=messages,
        )

        # Append the assistant turn VERBATIM. response.content carries the
        # tool_use blocks the next request needs — keep them.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # end_turn: the model is done and gave a final answer.
            return "".join(b.text for b in response.content if b.type == "text")

        # The model asked for one or more tools. YOUR code runs them, then
        # returns EVERY result in a SINGLE following user message.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({json.dumps(block.input)})")
                output = calculator(**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})

    return "[stopped: too many turns without a final answer]"


if __name__ == "__main__":
    print(run("What is (2 ** 10) * 3, then subtract 7? Show your steps."))
