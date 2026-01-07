import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_failure(error_message, html_snippet=None):
    """
    Uses OpenAI to analyze test failure and return:
    - Root cause
    - Suggested fix
    - Bug report format
    """
    prompt = f"""
You are a senior QA Automation Engineer.
Analyze the test failure below and produce:

1. Root Cause (why it failed)
2. Recommended Fix (what to change)
3. Bug Report (Title, Steps, Expected, Actual)

Error Message:
{error_message}

HTML Snippet:
{html_snippet}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert automation engineer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI analysis failed: {e}"
