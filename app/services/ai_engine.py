import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def build_prompt(code: str) -> str:
    return f"""
You are a senior software engineer.

Analyze the code and return STRICT JSON only.

Format:
{{
  "bugs": [],
  "improvements": [],
  "time_complexity": "",
  "security": [],
  "refactored_code": ""
}}

Rules:
- Do NOT explain outside JSON
- Keep responses concise but meaningful

Code:
{code}
"""

def get_ai_review(code: str):
    prompt = build_prompt(code)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer. Output only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        extra_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Code Reviewer"
        }
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "error": "Invalid JSON from model",
            "raw": content
        }