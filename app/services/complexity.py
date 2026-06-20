from radon.complexity import cc_visit, cc_rank

def analyze_complexity(code: str):
    try:
        results = cc_visit(code)
    except Exception as e:
        return {"error": str(e)}

    functions = []

    for item in results:
        functions.append({
            "name": item.name,
            "complexity": item.complexity,
            "rank": cc_rank(item.complexity)
        })

    return {
        "functions": functions
    }
