from fastapi import APIRouter
from app.models.schema import CodeRequest
from app.services.ast_analyzer import analyze_ast
from app.services.ai_engine import get_ai_review
from app.services.complexity import analyze_complexity
from app.services.security import analyze_security
from app.services.scorer import score_code

router = APIRouter()

@router.post("/review")
def review_code(request: CodeRequest):
    code = request.code

    ast_result = analyze_ast(code)
    complexity_result = analyze_complexity(code)
    security_result = analyze_security(code)
    ai_result = get_ai_review(code)

    score_result = score_code(
        ast_result,
        complexity_result,
        security_result,
        ai_result
    )

    return {
        "score": score_result,
        "ast_analysis": ast_result,
        "complexity": complexity_result,
        "security": security_result,
        "ai_review": ai_result
    }