from app.services.ast_analyzer import analyze_ast

code = """
def add(a, b):
    return a + b

def complex():
    for i in range(5):
        for j in range(5):
            print(i, j)
"""

result = analyze_ast(code)
print(result)