from fastapi import APIRouter, Request
import requests
import os

# ✅ move imports to top (better performance)
from app.services.ast_analyzer import analyze_ast
from app.services.complexity import analyze_complexity
from app.services.security import analyze_security
from app.services.ai_engine import get_ai_review
from app.services.scorer import score_code

router = APIRouter()


@router.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    print("Incoming event:", payload.get("action"))

    # ✅ Only handle PR opened
    if payload.get("action") != "opened":
        return {"status": "ignored"}

    pr = payload.get("pull_request")
    if not pr:
        return {"status": "no pr data"}

    # ✅ Load token at runtime (important fix)
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # Repo info
    owner = payload["repository"]["owner"]["login"]
    repo = payload["repository"]["name"]

    # Get files in PR
    files_url = pr["url"] + "/files"

    files_response = requests.get(files_url, headers=headers)

    if files_response.status_code != 200:
        return {
            "error": "failed to fetch files",
            "details": files_response.text
        }

    files = files_response.json()

    comments = []

    for file in files:
        # ✅ Only Python and JavaScript files
        if not (file["filename"].endswith(".py") or file["filename"].endswith(".js")):
            continue

        raw_url = file["raw_url"]

        code_res = requests.get(raw_url)

        # ✅ safe fetch
        if code_res.status_code != 200:
            continue

        code = code_res.text

        # 🔍 Run analyzers
        ast_result = analyze_ast(code)
        complexity_result = analyze_complexity(code)
        security_result = analyze_security(code)
        ai_result = get_ai_review(code)

        score = score_code(
            ast_result,
            complexity_result,
            security_result,
            ai_result
        )

        # ✅ safe issues formatting
        issues = score.get("reasons", [])
        issues_text = "\n".join(f"- {r}" for r in issues) if issues else "No major issues found."

        comments.append(
            f"""### 🤖 AI Review for `{file['filename']}`

**Score:** {score['score']} ({score['verdict']})

**Issues:**
{issues_text}
"""
        )

    # ✅ handle empty case
    if not comments:
        comments.append("✅ No Python files to review.")

    # 📝 Post comment
    comment_url = pr["comments_url"]

    res = requests.post(
        comment_url,
        headers=headers,
        json={"body": "\n\n".join(comments)}
    )

    print("Comment status:", res.status_code)

    return {
        "status": "done",
        "comment_status": res.status_code
    }