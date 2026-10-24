"""Gmail API wrapper: OAuth, read unread, draft reply. No send capability on purpose."""
import base64
import os
import re
from email.message import EmailMessage

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# readonly = read mail; compose = create drafts. (compose technically also allows
# sending, so we simply never expose a send function.)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
TOKEN_FILE = "token.json"
CREDS_FILE = "credentials.json"

_service = None


def _load_credentials() -> Credentials:
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            # Refresh token revoked/expired (happens every 7 days while the
            # OAuth app is in "Testing" mode). Fall through to a fresh login.
            os.remove(TOKEN_FILE)
            creds = None
        else:
            _save(creds)
            return creds

    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    _save(creds)
    return creds


def _save(creds: Credentials) -> None:
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def get_service():
    global _service
    if _service is None:
        _service = build("gmail", "v1", credentials=_load_credentials())
    return _service


# ---------- parsing helpers ----------

def _header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def _extract_body(payload: dict) -> str:
    """Prefer text/plain; fall back to stripped text/html."""
    plain, html = [], []

    def walk(part):
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data")
        if data and mime == "text/plain":
            plain.append(_decode(data))
        elif data and mime == "text/html":
            html.append(_strip_html(_decode(data)))
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    return "\n".join(plain).strip() or "\n".join(html).strip()


def _to_dict(msg: dict) -> dict:
    h = msg["payload"].get("headers", [])
    return {
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "from": _header(h, "From"),
        "reply_to": _header(h, "Reply-To") or _header(h, "From"),
        "subject": _header(h, "Subject") or "(no subject)",
        "date": _header(h, "Date"),
        "message_id": _header(h, "Message-ID"),
        "snippet": msg.get("snippet", ""),
        "body": _extract_body(msg["payload"]),
    }


# ---------- public API ----------

def list_unread(max_results: int = 5) -> list[dict]:
    svc = get_service()
    res = svc.users().messages().list(
        userId="me", q="is:unread in:inbox", maxResults=max_results
    ).execute()
    out = []
    for m in res.get("messages", []):
        full = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
        out.append(_to_dict(full))
    return out


def get_email(message_id: str) -> dict:
    full = get_service().users().messages().get(userId="me", id=message_id, format="full").execute()
    return _to_dict(full)


def create_draft_reply(message_id: str, body: str) -> str:
    """Create a threaded draft reply. Returns the draft id. Never sends."""
    orig = get_email(message_id)
    msg = EmailMessage()
    msg["To"] = orig["reply_to"]
    subj = orig["subject"]
    msg["Subject"] = subj if subj.lower().startswith("re:") else f"Re: {subj}"
    if orig["message_id"]:
        msg["In-Reply-To"] = orig["message_id"]
        msg["References"] = orig["message_id"]
    msg.set_content(body)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = get_service().users().drafts().create(
        userId="me", body={"message": {"raw": raw, "threadId": orig["thread_id"]}}
    ).execute()
    return draft["id"]
