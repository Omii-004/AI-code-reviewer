def score_code(ast_data, complexity_data, security_data, ai_data):
    score = 100
    reasons = []

    # Security penalties 
    for issue in security_data.get("issues", []):
        severity = issue.get("severity", "LOW")

        if severity == "HIGH":
            score -= 20
            reasons.append("High severity security issue")
        elif severity == "MEDIUM":
            score -= 10
            reasons.append("Medium severity security issue")
        else:
            score -= 5

    # Complexity penalties
    for func in complexity_data.get("functions", []):
        c = func.get("complexity", 0)

        if c > 10:
            score -= 15
            reasons.append(f"High complexity in {func['name']}")
        elif c > 5:
            score -= 8

    # AST issues
    for issue in ast_data.get("issues", []):
        score -= 5
        reasons.append(issue)

    # AI bugs
    for bug in ai_data.get("bugs", []):
        score -= 7
        reasons.append(bug)

    # Clamp score
    score = max(score, 0)

    # Verdict
    if score > 80:
        verdict = "GOOD"
    elif score > 50:
        verdict = "NEEDS IMPROVEMENT"
    else:
        verdict = "RISKY"

    return {
        "score": score,
        "verdict": verdict,
        "reasons": reasons[:5] #reasons count
    }