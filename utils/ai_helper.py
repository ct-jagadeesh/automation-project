# utils/ai_helper.py
import os
import traceback

# Attempt to detect the SDK style (old vs new)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Helper to build a safe, informative fallback
def _fallback_message(e=None):
    base = (
        "AI analysis unavailable.\n"
        "- If you want AI analysis, install the OpenAI Python SDK and set OPENAI_API_KEY.\n"
        "  For the new SDK (recommended): pip install openai\n"
        "  Or pin older SDK: pip install 'openai==0.28.0'\n\n"
        "Fallback analysis:\n"
        "- Root cause: Likely an assertion or selector mismatch.\n"
        "- Recommended fix: Check screenshot and page HTML, adjust selectors/waits.\n"
        "- Bug report: Title: Test failure; Steps: run test; Expected: success; Actual: failure; See screenshot.\n"
    )
    if e:
        return base + "\nSDK error:\n" + str(e) + "\n" + traceback.format_exc()
    return base

def analyze_failure(error_message: str, html_snippet: str | None = None) -> str:
    """
    Try to call OpenAI to analyze a failure.
    Supports both old (pre-1.0) and new (>=1.0) openai python SDKs.
    Returns string (AI analysis or fallback).
    """
    prompt = f"""You are a senior QA Automation engineer.
Analyze the test failure below and produce:
1) Root cause (short)
2) Recommended fix (short)
3) Bug report (Title, Steps to reproduce, Expected, Actual)

Error message:
{error_message}

HTML snippet:
{html_snippet if html_snippet else '<no html provided>'}
"""

    # If API key missing, return helpful fallback
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY not set in environment.\n\n" + _fallback_message()

    # Try to import openai and detect SDK version style
    try:
        import openai
    except Exception as e:
        return _fallback_message(e)

    # 1) New SDK style (openai>=1.0.0) -> from openai import OpenAI; client = OpenAI()
    try:
        # detect new-style SDK
        if hasattr(openai, "OpenAI"):
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY) if getattr(openai, "OpenAI").__init__.__code__.co_argcount > 1 else openai.OpenAI()
            except Exception:
                # safe fallback to client without passing api_key if not needed
                client = openai.OpenAI()

            # call chat completions with new API
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert QA automation engineer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.1,
            )
            # new SDK stores text in resp.choices[0].message.content
            # but to be robust, try multiple paths
            try:
                return resp.choices[0].message.content.strip()
            except Exception:
                try:
                    return resp.choices[0].message["content"].strip()
                except Exception:
                    return str(resp)
    except Exception as e_new:
        # continue to try old SDK approach
        new_err = e_new

    # 2) Old SDK style (openai<1.0) -> openai.ChatCompletion.create(...)
    try:
        # ensure api key set
        try:
            openai.api_key = OPENAI_API_KEY
        except Exception:
            pass

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert QA automation engineer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.1,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e_old:
        # return combined diagnostics
        return _fallback_message(e_old) + "\n\nNew-SDK-error:\n" + (str(new_err) if 'new_err' in locals() else "none")
