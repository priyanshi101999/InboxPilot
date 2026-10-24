# InboxPilot

## Where I'm at

Building this in phases, one at a time.

✓ Gmail agent: reads unread mail, summarizes, saves draft replies

Still to do:
- Calendar agent + a router that decides email vs calendar vs both
- Approval step, so nothing gets sent or created without me saying yes
- Evals + tracing (want a real accuracy number, not "seems to work")
- Retries and fallbacks for when Gmail/Calendar API is down
- Deploy it with a small UI and write up what went wrong along the way

Phase 1 is done and tested on 10 made-up emails (vague ones, all-caps,
forwarded chains, a prompt injection). Everything else is not built yet.

## What it does
- Reads unread inbox emails and summarizes them in a few sentences
- Says "unclear" when an email is vague, and flags emails it can't read
  (image-only emails, attachments) instead of guessing
- Saves threaded draft replies to Gmail, using the original sender's
  reply address (the model never chooses the recipient)
- Treats email text as untrusted data, so instructions inside an email
  aren't followed

## How it works
A hand-built ReAct loop in LangGraph: the model decides whether to call a
tool (list unread, read email, draft reply), reads the result, and repeats
until it can answer. The LLM sits behind one `get_llm()` function, so you
can switch between Gemini and Groq free tiers.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add a free Gemini or Groq key
3. Add `credentials.json` (Google Cloud OAuth client, type Desktop app)
4. `py main.py "Summarize my 10 most recent unread emails"`

See `DECISIONS.md` for design choices and bugs I hit along the way.