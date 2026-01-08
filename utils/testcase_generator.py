# utils/testcase_generator.py
import os
import re
import traceback
from urllib.parse import urlparse

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def _sanitize_filename(s: str) -> str:
    return re.sub(r'[^0-9a-zA-Z_-]', '_', s)

def _fallback_generator(url: str, description: str | None = None) -> dict:
    """Return a safe fallback (non-AI) set of test cases + test code."""
    host = urlparse(url).netloc or "site"
    title = f"Basic smoke tests for {host}"
    steps = [
        f"Open {url}",
        "Check page loads (status/visible body)",
        "If there's a login form: fill username/password and submit",
        "If there's a search box: type a sample query and assert results",
        "Take screenshot on any failure"
    ]
    test_code = f'''from playwright.sync_api import sync_playwright

def test_generated_smoke():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("{url}", timeout=60000)
        # TODO: adjust selectors based on the site
        # Example: assert page.locator("body").count() > 0
        assert page.content() is not None
        print("Generated test executed (fallback).")
        browser.close()
'''
    return {"title": title, "steps": steps, "test_code": test_code}

# Try to call OpenAI (supports both new & old SDKs if installed)
def generate_with_openai(url: str, description: str | None = None, model: str = "gpt-4o-mini") -> dict:
    prompt = f"""
You are an expert QA automation engineer. Produce:
1) A short title for automated tests for the site: {url}
2) A small list (3-6) of specific test cases with short descriptions (Steps and Expected result).
3) A Playwright (Python) test skeleton that implements one of the basic tests (use simple selectors, add TODO comments where unsure).
Return JSON with keys: title, steps (array of strings), test_code (string).
URL: {url}
Description: {description if description else '<none>'}
"""
    # if no API key, bail out early
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    try:
        import openai
    except Exception as e:
        raise RuntimeError(f"OpenAI SDK not installed: {e}")

    # New SDK style
    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role":"system","content":"You are an expert QA automation engineer."},
                    {"role":"user","content":prompt}
                ],
                max_tokens=800,
                temperature=0.0
            )
            # try to extract textual content
            try:
                content = resp.choices[0].message.content
            except Exception:
                content = str(resp)
        else:
            # old SDK
            openai.api_key = OPENAI_API_KEY
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role":"system","content":"You are an expert QA automation engineer."},
                    {"role":"user","content":prompt}
                ],
                max_tokens=800,
                temperature=0.0
            )
            content = resp["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"OpenAI call failed: {e}")

    # Try to parse AI response heuristically:
    # If the model returned JSON-like content, try to find the blocks.
    # Otherwise, wrap the full text into a single test_code comment and return minimal structure.
    try:
        # naive attempt: if the response contains ```python block, extract it as test_code
        test_code = ""
        if "```python" in content:
            # grab last python fenced block
            parts = content.split("```python")
            test_code = parts[-1].split("```")[0].strip()
        else:
            # try to find lines that look like code (starting with "from playwright" or "with sync_playwright")
            m = re.search(r"(from playwright[\s\S]*$)", content, re.IGNORECASE)
            if m:
                test_code = m.group(1).strip()
            else:
                # fallback: put full content into a test file comment
                test_code = f'"""\\nAI output:\\n{content}\\n"""\\n\\n# TODO: Convert AI output into executable Playwright code.'
        # For steps, try to pull bullet lists
        steps = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("-") or line.startswith("1.") or line.startswith("•") or line.startswith("*"):
                steps.append(line.lstrip("-*0123456789. ").strip())
            if len(steps) >= 6:
                break
        if not steps:
            steps = ["Open the page", "Check main elements are visible", "Take screenshot on failure"]
        title = f"Auto-generated tests for {url}"
        return {"title": title, "steps": steps, "test_code": test_code}
    except Exception as e:
        raise RuntimeError(f"Failed to parse AI response: {e}")

def generate_test_file(url: str, description: str | None = None, out_dir: str = "tests") -> str:
    """
    Generate test file using AI if available, otherwise fallback.
    Returns path to the generated file.
    """
    os.makedirs(out_dir, exist_ok=True)
    host = urlparse(url).netloc or "site"
    filename = f"test_generated_from_{_sanitize_filename(host)}.py"
    out_path = os.path.join(out_dir, filename)

    # Try AI path first
    try:
        payload = generate_with_openai(url, description)
    except Exception as e:
        # on any failure, use fallback
        payload = _fallback_generator(url, description)
        # include a note in test code
        payload["test_code"] = "# NOTE: AI not available or failed. Using fallback test skeleton.\n" + payload["test_code"]

    # Write the test file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated test file\n")
        f.write(f"# Title: {payload.get('title')}\n\n")
        # write steps as comments
        f.write("# Test cases / steps:\n")
        for s in payload.get("steps", []):
            f.write(f"# - {s}\n")
        f.write("\n")
        f.write(payload.get("test_code", ""))
    return out_path
