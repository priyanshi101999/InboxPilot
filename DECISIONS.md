# InboxPilot decision log

**Oct 13** - Going with LangGraph. Phase 2 needs a router and an approval step,
and I figured I'd need to control the graph myself.

**Oct 13** - No paid API, so Gemini free tier. Put it behind get_llm() in
case I have to switch.

**Oct 16** - Wrote the graph by hand instead of using the prebuilt agent.
Lost about half a day: my tool node returned a string and LangGraph
threw "Expected dict". Now I know every node returns {"messages": [...]}.

**Oct 18** - Agent can only create drafts, no send. Recipient comes from the
original email in code, not from the model, so an email can't say
"reply to attacker@x.com".

**Oct 19** - Gemini quota gone on every model I tried. Moved dev runs to
flash-lite. Vague email test ("go with the second one") failed: model wrote
"approving the second option". Added an example to the prompt.

## Things that broke
- Body was None. I built `body` before calling walk(). Dumb ordering bug.
- Myntra email (image only) got a confident summary of nothing.
- Draft showed up alone until I fixed threadId.