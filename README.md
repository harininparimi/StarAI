# StarAI Corporate AI Training Opportunity Agent

StarAI is a research-only lead intelligence application for StarNet
Technologies' customized corporate AI training services in Dubai and the UAE.

## Deploy

1. Create a GitHub repository such as `StarAI`.
2. Upload all files and folders from this package.
3. Connect the repository to Streamlit Community Cloud.
4. Select `app.py`.
5. Add these Streamlit secrets:

```toml
ANTHROPIC_API_KEY = "your-real-api-key"
APP_PASSWORD = "your-pilot-password"
```

6. Deploy.

## Test prompt

Identify and score up to five large corporate AI training opportunities in
Dubai. Prioritize recent AI, digital-transformation, future-skills, and
leadership-development signals. Identify verified public decision-makers where
available.

## Governance

StarAI does not call, email, message, post, connect, follow, comment, or submit
forms. It does not guess private contact details. Human review is mandatory.


## Web-search compatibility

This final version intentionally does not pass `user_location` to Anthropic
web search. Dubai and UAE targeting is controlled through the StarAI prompt.
This avoids the `Country code AE is not supported` API error.
