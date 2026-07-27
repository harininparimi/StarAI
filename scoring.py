import pandas as pd
from config import MAX_LEADS

SCORE_COLUMNS = {
    "corporate_scale": "Corporate Scale",
    "ai_digital_signal": "AI / Digital Signal",
    "learning_signal": "Learning Signal",
    "training_fit": "Training Fit",
    "decision_maker_accessibility": "Decision-Maker Accessibility",
    "trigger_recency": "Trigger Recency",
    "source_quality": "Source Quality",
    "strategic_value": "Strategic Value",
}

ALLOWED_SCORES = {
    "corporate_scale": {0, 8, 15, 20},
    "ai_digital_signal": {0, 8, 15, 20},
    "learning_signal": {0, 5, 10, 15},
    "training_fit": {0, 5, 10, 15},
    "decision_maker_accessibility": {0, 4, 7, 10},
    "trigger_recency": {0, 3, 7, 10},
    "source_quality": {0, 1, 3, 5},
    "strategic_value": {0, 2, 4, 5},
}


def classify(total: int) -> tuple[str, str]:
    if total >= 85:
        return "Tier A+", "Priority human review"
    if total >= 75:
        return "Tier A", "Proceed to human review"
    if total >= 65:
        return "Tier B", "Proceed after evidence check"
    if total >= 50:
        return "Tier C", "Further research required"
    return "Reject", "Do not prioritize"


def build_results_table(payload: dict) -> pd.DataFrame:
    leads = payload.get("leads")
    if not isinstance(leads, list) or not leads:
        raise RuntimeError("No supported corporate leads were returned.")

    rows = []
    for lead in leads[:MAX_LEADS]:
        raw = lead.get("scores", {})
        scores, errors = {}, []

        for field, allowed in ALLOWED_SCORES.items():
            value = raw.get(field, 0)
            if isinstance(value, bool) or not isinstance(value, int):
                errors.append(f"{field}: non-integer")
                value = 0
            if value not in allowed:
                errors.append(f"{field}: invalid anchor {value}")
                value = 0
            scores[field] = value

        total = sum(scores.values())
        tier, recommendation = classify(total)

        urls = lead.get("source_urls", [])
        if not isinstance(urls, list):
            urls = []
        urls = [
            str(u).strip() for u in urls
            if str(u).strip().startswith(("http://", "https://"))
        ]

        profile = str(
            lead.get("decision_maker_profile_url", "Not Available")
        ).strip()
        if profile != "Not Available" and not profile.startswith(
            ("http://", "https://")
        ):
            profile = "Not Available"

        row = {
            "Company": str(lead.get("company", "Not Available")),
            "Sector": str(lead.get("sector", "Not Available")),
            "Location": str(lead.get("location", "Not Available")),
            "Company Scale Evidence": str(
                lead.get("company_scale_evidence", "Not Available")
            ),
            "AI / Digital Signal": str(
                lead.get("ai_or_digital_signal", "Not Available")
            ),
            "Learning Signal": str(
                lead.get("learning_signal", "Not Available")
            ),
            "Recommended Training Opportunity": str(
                lead.get("recommended_training_opportunity", "Not Available")
            ),
            "Recommended Audiences": str(
                lead.get("recommended_audiences", "Not Available")
            ),
            "Trigger Event": str(
                lead.get("trigger_event", "Not Available")
            ),
            "Decision-Maker Name": str(
                lead.get("decision_maker_name", "Not Available")
            ),
            "Decision-Maker Title": str(
                lead.get("decision_maker_title", "Not Available")
            ),
            "Decision-Maker Public Profile": profile,
            "Public Company Contact Route": str(
                lead.get("public_company_contact_route", "Not Available")
            ),
        }

        for field, label in SCORE_COLUMNS.items():
            row[label] = scores[field]

        row.update({
            "Total Score": total,
            "Tier": tier,
            "Recommendation": recommendation,
            "Source URLs": " | ".join(urls[:6]),
            "Validation": "Valid" if not errors else "; ".join(errors),
        })
        rows.append(row)

    df = pd.DataFrame(rows)
    df = (
        df.drop_duplicates(subset=["Company"], keep="first")
          .sort_values(["Total Score", "Company"], ascending=[False, True])
          .reset_index(drop=True)
    )
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df
