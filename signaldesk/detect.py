# Setup

import numpy as np
import pandas as pd

# Human signals. For all of these, DOWN is bad.
HUMAN_SIGNALS = [
    ("completion_rate", "completion"),
    ("accepted_per_completed", "acceptance of completed runs"),
    ("user_rating", "user rating"),
    ("avg_minutes_saved", "minutes saved"),
]

# Minimum move before we call it a move rather than noise.
THRESHOLD = 0.02

#the trend function

def _trend(dates, values):
    """Relative change across a fitted straight line."""
    s = pd.Series(values, dtype="float64")
    ok = s.notna()
    if ok.sum() < 3:
        return None
    x = pd.to_numeric(pd.Series(dates)[ok]).values.astype("float64")
    x = (x - x.min()) / 8.64e13   # nanoseconds -> days
    y = s[ok].values
    if np.ptp(x) == 0:
        return None
    slope, intercept = np.polyfit(x, y, 1)
    start = intercept
    end = slope * x.max() + intercept
    if start == 0 or not np.isfinite(start):
        return None
    return float((end - start) / abs(start))

#the detector

def find_divergence(df):
    """Score every workflow/source for confidence-vs-human divergence."""
    findings = []

    for (team, workflow, source), g in df.groupby(["team", "workflow", "source"]):
        g = g.sort_values("date")

        if g["date"].nunique() < 3:
            findings.append({
                "team": team, "workflow": workflow, "source": source,
                "severity": "Not enough data", "confidence_change": None,
                "falling": [], "sessions": int(g["sessions"].sum()),
                "days": int(g["date"].nunique()),
                "summary": "Fewer than three days of data. No trend read.",
            })
            continue

        conf = _trend(g["date"], g["median_confidence"])
        falling = []
        for col, label in HUMAN_SIGNALS:
            t = _trend(g["date"], g[col])
            if t is not None and t <= -THRESHOLD:
                falling.append((label, t))

        diverging = conf is not None and conf >= THRESHOLD and len(falling) > 0

        if not diverging:
            severity = "No divergence"
            summary = "Model confidence and human signals are moving together."
        else:
            worst = min(t for _, t in falling)
            material = [t for _, t in falling if t <= -0.05]
            if len(material) >= 3 or worst <= -0.20:
                severity = "High"
            elif len(material) >= 1 and worst <= -0.10:
                severity = "Medium"
            elif material:
                severity = "Low"
            else:
                severity = "Watch"
            names = ", ".join(label for label, _ in falling)
            summary = f"Model confidence rose {conf:+.0%} while {names} fell."

        findings.append({
            "team": team, "workflow": workflow, "source": source,
            "severity": severity, "confidence_change": conf,
            "falling": falling, "sessions": int(g["sessions"].sum()),
            "days": int(g["date"].nunique()), "summary": summary,
        })

    order = {"High": 0, "Medium": 1, "Low": 2, "Watch": 3,
             "No divergence": 4, "Not enough data": 5}
    findings.sort(key=lambda f: (order[f["severity"]], -f["sessions"]))
    return findings

def daily_break(df, lookback=3, min_sessions=10):
    """Catch a single day that broke away from its own recent baseline."""
    breaks = []
    for (team, workflow, source), g in df.groupby(["team", "workflow", "source"]):
        g = g.sort_values("date")
        if len(g) < lookback + 1:
            continue
        last, prior = g.iloc[-1], g.iloc[-(lookback + 1):-1]
        if last["sessions"] < min_sessions:
            continue

        moves = {}
        for col, label in HUMAN_SIGNALS + [("flag_rate", "flag rate")]:
            base = prior[col].mean()
            if pd.isna(base) or base == 0 or pd.isna(last[col]):
                continue
            moves[label] = float((last[col] - base) / abs(base))

        cbase, cnow = prior["median_confidence"].mean(), last["median_confidence"]
        conf_move = (float((cnow - cbase) / abs(cbase))
                     if pd.notna(cbase) and cbase != 0 and pd.notna(cnow) else None)

        bad = {k: v for k, v in moves.items()
               if k != "flag rate" and v <= -0.15}
        if bad:
            breaks.append({"team": team, "workflow": workflow, "source": source,
                           "date": last["date"], "note": str(last["notes"]),
                           "confidence_move": conf_move, "moves": moves,
                           "sessions": int(last["sessions"])})
    return sorted(breaks, key=lambda b: min(b["moves"].values()))