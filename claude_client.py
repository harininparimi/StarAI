from anthropic import Anthropic, APIError
from config import (
    MODEL, MAX_OUTPUT_TOKENS, MAX_WEB_SEARCHES,
    PRIMARY_WEB_SEARCH_TOOL, FALLBACK_WEB_SEARCH_TOOL,
)
from utils import extract_json, extract_text


def _tool(tool_type: str) -> dict:
    return {
        "type": tool_type,
        "name": "web_search",
        "max_uses": MAX_WEB_SEARCHES,
        "user_location": {
            "type": "approximate",
            "city": "Dubai",
            "region": "Dubai",
            "country": "AE",
            "timezone": "Asia/Dubai",
        },
    }


def _call(client: Anthropic, prompt: str, tool_type: str):
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=messages,
        tools=[_tool(tool_type)],
    )

    if response.stop_reason == "pause_turn":
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            messages=messages + [
                {"role": "assistant", "content": response.content}
            ],
            tools=[_tool(tool_type)],
        )
    return response


def research_and_score(api_key: str, prompt: str) -> dict:
    client = Anthropic(api_key=api_key)

    try:
        response = _call(client, prompt, PRIMARY_WEB_SEARCH_TOOL)
    except APIError as exc:
        message = str(exc).lower()
        if not any(x in message for x in [
            "web_search_20260209", "unsupported", "invalid tool", "tool type"
        ]):
            raise
        response = _call(client, prompt, FALLBACK_WEB_SEARCH_TOOL)

    if response.stop_reason == "max_tokens":
        retry = prompt + """
RETRY REQUIREMENT:
Return no more than 3 leads.
Keep every descriptive field under 25 words.
Use no more than 4 source URLs per lead.
Return JSON only.
"""
        response = _call(client, retry, FALLBACK_WEB_SEARCH_TOOL)

    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            "The response reached the output limit twice. "
            "Use a narrower sector or company set."
        )

    text = extract_text(response)
    if not text:
        raise RuntimeError("Claude returned no final text output.")
    return extract_json(text)
