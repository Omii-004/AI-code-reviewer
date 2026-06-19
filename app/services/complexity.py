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

#Test
if __name__ == "__main__":
    code = """
def simple(a, b):
    return a + b


def medium(n):
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i
    return total


def complex(n):
    result = 0
    for i in range(n):
        for j in range(n):
            if i % 2 == 0:
                if j % 3 == 0:
                    result += i * j
                else:
                    result -= j
    return result
"""