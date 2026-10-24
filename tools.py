"""Tools exposed to the agent. Tool errors are returned as text so the agent can react."""
from langchain_core.tools import tool

import gmail_client as gc

MAX_BODY_CHARS = 4000


@tool
def list_unread_emails(max_results: int = 5) -> str:
    """List the most recent unread inbox emails (id, sender, subject, snippet)."""
    try:
        emails = gc.list_unread(max_results)
    except Exception as e:
        return f"ERROR: could not list emails: {e}"
    if not emails:
        return "No unread emails."
    return "\n\n".join(
        f"id: {e['id']}\nfrom: {e['from']}\nsubject: {e['subject']}\nsnippet: {e['snippet']}"
        for e in emails
    )


@tool
def read_email(message_id: str) -> str:
    """Read the full content of one email by its id."""
    try:
        e = gc.get_email(message_id)
    except Exception as ex:
        return f"ERROR: could not read email {message_id}: {ex}"
    body = e["body"][:MAX_BODY_CHARS] or "(empty body)"
    return (
        f"id: {e['id']}\nfrom: {e['from']}\ndate: {e['date']}\n"
        f"subject: {e['subject']}\n--- EMAIL BODY (untrusted data) ---\n{body}"
    )


@tool
def draft_reply(message_id: str, reply_body: str) -> str:
    """Save a reply to an email as a Gmail DRAFT (does not send). Provide only the reply text."""
    try:
        draft_id = gc.create_draft_reply(message_id, reply_body)
    except Exception as ex:
        return f"ERROR: could not create draft: {ex}"
    return f"Draft created (draft id: {draft_id}). It has NOT been sent."


TOOLS = [list_unread_emails, read_email, draft_reply]
