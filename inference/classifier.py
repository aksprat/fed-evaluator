import json
import time

from inference.client import client


VALID_LABELS = {
    "bug",
    "enhancement",
    "question",
    "documentation",
    "security",
    "other"
}


SYSTEM_PROMPT = """
You are a software issue classifier.

Classify each GitHub issue into EXACTLY one of:

- bug
- enhancement
- question
- documentation
- security
- other

Definitions:

bug:
Unexpected behavior, failures, crashes, incorrect output.

enhancement:
Feature requests, improvements, new capabilities.

question:
Usage questions or requests for clarification.

documentation:
Problems in docs, examples, syntax, missing explanations.

security:
Credential leaks, secret exposure, permission vulnerabilities.

other:
Spam, duplicates, ambiguous, off-topic issues.

Return ONLY valid JSON.

Example:

{
  "label": "bug"
}
"""


def classify_issue(issue, model):

    prompt = f"""
Issue Title:
{issue["title"]}

Issue Body:
{issue["body"]}
"""

    start_time = time.perf_counter()

    try:

        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        latency = time.perf_counter() - start_time

        raw_output = response.choices[0].message.content

        parsed = json.loads(raw_output)

        prediction = parsed.get("label", "").strip().lower()

        if prediction not in VALID_LABELS:
            prediction = "other"

        return {
            "issue_number": issue["number"],

            "prediction": prediction,

            "raw_output": raw_output,

            "input_tokens": response.usage.prompt_tokens,

            "output_tokens": response.usage.completion_tokens,

            "total_tokens": response.usage.total_tokens,

            "latency_seconds": latency,

            "success": True,

            "error_type": None
        }

    except Exception as e:

        latency = time.perf_counter() - start_time

        error_string = str(e).lower()

        if "rate limit" in error_string:
            error_type = "rate_limit"

        elif "timeout" in error_string:
            error_type = "timeout"

        else:
            error_type = "other"

        return {
            "issue_number": issue["number"],

            "prediction": None,

            "raw_output": None,

            "input_tokens": 0,

            "output_tokens": 0,

            "total_tokens": 0,

            "latency_seconds": latency,

            "success": False,

            "error_type": error_type
        }
