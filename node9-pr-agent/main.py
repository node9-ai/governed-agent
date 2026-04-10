"""
FastAPI webhook receiver for the CI code review agent.

Triggered by GitHub PR comments containing "@node9-fixer".

Run locally:
  uvicorn main:app --reload

Deploy:
  docker build -t ci-code-review-fixer .
  docker run -p 8000:8000 --env-file .env ci-code-review-fixer
"""
import hashlib
import hmac
import os

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

from agent import execute_review_fix

app = FastAPI(title="node9 CI Code Review Fixer")

WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")


def _verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature (X-Hub-Signature-256)."""
    if not WEBHOOK_SECRET:
        return True  # skip verification if secret not configured
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")


@app.post("/webhook")
async def github_event(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=""),
):
    payload_bytes = await request.body()

    if WEBHOOK_SECRET and not _verify_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    # PR review comments mentioning @node9-fixer
    if x_github_event == "pull_request_review_comment":
        comment = payload.get("comment", {}).get("body", "")
        if "@node9-fixer" in comment:
            background_tasks.add_task(execute_review_fix)
            return {"status": "node9 dispatched 🛡️"}

    # Issue comments on PRs mentioning @node9-fixer
    if x_github_event == "issue_comment":
        comment = payload.get("comment", {}).get("body", "")
        is_pr = "pull_request" in payload.get("issue", {})
        if "@node9-fixer" in comment and is_pr:
            background_tasks.add_task(execute_review_fix)
            return {"status": "node9 dispatched 🛡️"}

    return {"status": "no action needed"}


@app.get("/health")
async def health():
    return {"ok": True}
