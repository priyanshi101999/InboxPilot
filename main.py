"""CLI: python main.py "summarize my unread emails"  (or run with no args for a chat loop)"""
import sys

from llm import text_of
from agent import build_graph


def run(graph, user_input: str, history: list) -> list:
    history = history + [("user", user_input)]
    final = None
    for step in graph.stream({"messages": history}, stream_mode="values"):
        msg = step["messages"][-1]
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"  [tool] {call['name']}({call['args']})")
        final = step["messages"]
    print("\n" + text_of(final[-1]) + "\n")
    return final


if __name__ == "__main__":
    graph = build_graph()
    if len(sys.argv) > 1:
        run(graph, " ".join(sys.argv[1:]), [])
    else:
        history: list = []
        print("Email agent. Ctrl+C to quit. Try: 'summarize my unread emails'")
        while True:
            history = run(graph, input("you> "), history)
