import tempfile
import subprocess
import json
import os

def analyze_security(code: str):
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(code.encode())
            temp_path = temp.name

        # Run Bandit
        result = subprocess.run(
            ["bandit", "-f", "json", temp_path],
            capture_output=True,
            text=True
        )

        output = json.loads(result.stdout)

        issues = []
        for item in output.get("results", []):
            issues.append({
                "issue": item.get("issue_text"),
                "severity": item.get("issue_severity"),
                "line": item.get("line_number")
            })

        return {
            "issues": issues
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
