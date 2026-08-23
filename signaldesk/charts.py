import pandas as pd


def divergence_frame(df, team, workflow, source):
    """Both series as % change from their own day-1 value."""
    g = df[(df["team"] == team) &
           (df["workflow"] == workflow) &
           (df["source"] == source)].sort_values("date")

    out = pd.DataFrame({"date": g["date"]})
    for col, label in [("median_confidence", "Model confidence (AI's own rating)"),
                       ("accepted_per_session", "Accepted outputs (what humans did)"),
                       ("user_rating", "User rating (what humans said)")]:
        s = pd.to_numeric(g[col], errors="coerce")
        base = s.dropna().iloc[0] if s.notna().any() else None
        out[label] = (s / base - 1) * 100 if base else None
    return out.set_index("date")

