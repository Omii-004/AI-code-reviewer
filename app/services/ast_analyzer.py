import ast

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.issues = []

    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name,
            "args": len(node.args.args),
            "lines": len(node.body)
        }

        # Detect long functions
        if len(node.body) > 20:
            self.issues.append(f"Function '{node.name}' is too long")

        self.functions.append(func_info)

        self.generic_visit(node)

    def visit_Assign(self, node):
        # Detect possible unused variables (basic heuristic)
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            if var_name.startswith("_"):
                self.issues.append(f"Variable '{var_name}' might be unused")

        self.generic_visit(node)

    def visit_For(self, node):
        # Detect nested loops
        for child in node.body:
            if isinstance(child, ast.For):
                self.issues.append("Nested loop detected (O(n^2) risk)")
                break

        self.generic_visit(node)


def analyze_ast(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "syntax_error": str(e)
        }

    visitor = CodeVisitor()
    visitor.visit(tree)

    return {
        "functions": visitor.functions,
        "issues": visitor.issues
    }
