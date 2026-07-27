from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

MODEL = "claude-sonnet-5"
MAX_LEADS = 5
MAX_OUTPUT_TOKENS = 12000
MAX_WEB_SEARCHES = 10

PRIMARY_WEB_SEARCH_TOOL = "web_search_20260209"
FALLBACK_WEB_SEARCH_TOOL = "web_search_20250305"

SUPPORTED_KNOWLEDGE_EXTENSIONS = {
    ".docx", ".xlsx", ".txt", ".md", ".csv"
}
