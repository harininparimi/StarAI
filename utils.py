import json
import re


def extract_text(response) -> str:
    return "\n".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
        and getattr(block, "text", "").strip()
    ).strip()


def extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise RuntimeError("Claude did not return valid JSON.")
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError as exc:
            raise RuntimeError("Claude returned malformed JSON.") from exc
