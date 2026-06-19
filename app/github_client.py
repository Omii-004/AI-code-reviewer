import requests
import os

def post_pr_comment(owner, repo, pr_number, comment):
    token = os.getenv("GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "body": comment
    }

    response = requests.post(url, headers=headers, json=data)

    print("Comment status:", response.status_code)
    print(response.json())