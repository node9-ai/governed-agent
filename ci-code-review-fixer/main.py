from fastapi import FastAPI, BackgroundTasks
from agent import execute_review_fix

app = FastAPI(title="Node9 CI-Code-Review-Fixer")

@app.post("/webhook")
async def github_event(background_tasks: BackgroundTasks, payload: dict):
    # This logic will parse the GitHub Webhook payload
    comment = payload.get("comment", {}).get("body", "")
    file_path = payload.get("comment", {}).get("path", "app.py")
    
    if "@node9-fixer" in comment:
        background_tasks.add_task(execute_review_fix, comment, file_path)
        return {"status": "Warden dispatched 🛡️"}
    
    return {"status": "No action needed"}
