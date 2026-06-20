from fastapi import APIRouter, Request, BackgroundTasks
import requests
import os

# analyzers
from app.services.ast_analyzer import analyze_ast
from app.services.complexity import analyze_complexity
from app.services.security import analyze_security
from app.services.ai_engine import get_ai_review
from app.services.scorer import score_code

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise Exception("GITHUB_TOKEN is missing")

def format_ai_review(review: dict) -> str:
    if not isinstance(review, dict):
        return "AI response unavailable or invalid."

    bugs = review.get("bugs", [])
    improvements = review.get("improvements", [])
    security = review.get("security", [])
    complexity = review.get("time_complexity", "N/A")

    def fmt(items):
        return "\n".join(f"- {i}" for i in items) if items else "No issues found."

    return f"""
🔴 **Issues**
{fmt(bugs)}

⚡ **Improvements**
{fmt(improvements)}

🔐 **Security**
{fmt(security)}

📊 **Complexity**
{complexity}
"""

def process_pr(payload):
    try:
        print("Incoming event:", payload.get("action"))

        if payload.get("action") != "opened":
            return

        pr = payload.get("pull_request")
        if not pr:
            return

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        files_url = pr["url"] + "/files"
        files_response = requests.get(files_url, headers=headers)

        if files_response.status_code != 200:
            print("Failed to fetch files:", files_response.text)
            return

        files = files_response.json()
        comments = []

        for file in files:
            filename = file["filename"]

            if not filename.endswith(".py"):
                continue

            code_res = requests.get(file["raw_url"])
            if code_res.status_code != 200:
                continue

            code = code_res.text

            # analyzers
            ast_result = analyze_ast(code)
            complexity_result = analyze_complexity(code)
            security_result = analyze_security(code)

            ai_result = get_ai_review(code) if len(code.strip()) < 5000 else {}

            # scoring
            score = score_code(
                ast_result,
                complexity_result,
                security_result,
                ai_result
            )

            issues = score.get("reasons", [])
            issues_text = "\n".join(f"- {r}" for r in issues) if issues else "No major issues found."

            formatted_ai = format_ai_review(ai_result)

            comments.append(
                f"""### 📄 `{filename}`

**Score:** {score.get('score')} ({score.get('verdict')})

{formatted_ai}

🧾 **Summary Issues**
{issues_text}
"""
            )

        if not comments:
            comments.append("No Python files to review.")

        # Post PR comment
        res = requests.post(
            pr["comments_url"],
            headers=headers,
            json={"body": "\n\n".join(comments)}
        )

        print("Comment status:", res.status_code)

    except Exception as e:
        print("Error in process_pr:", str(e))


# WEBHOOK
@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    event = request.headers.get("X-GitHub-Event")

    if event != "pull_request":
        return {"status": "ignored"}

    payload = await request.json()

    background_tasks.add_task(process_pr, payload)

    return {"status": "processing"}