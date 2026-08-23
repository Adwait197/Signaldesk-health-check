#the  dictionary

import numpy as np
import pandas as pd

TRUSTED = "Trusted"
DIRECTIONAL = "Directional"
DO_NOT_TRUST = "Do not trust as quality"

TRUST = {
    "sessions": (TRUSTED,
        "A count of workflow runs. Reliable, but these are runs, not people. "
        "One enthusiastic user can move it."),
    "completion_rate": (TRUSTED,
        "Reached a final output. Says nothing about whether the output was "
        "good, only that the workflow did not stall."),
    "accepted_per_completed": (DIRECTIONAL,
        "Of the runs that finished, how many were accepted without major "
        "rework. The closest thing here to a quality signal, and still rough."),
    "accepted_per_session": (DIRECTIONAL,
        "Of all runs started, how many ended in an accepted output. Use this "
        "for end-to-end usefulness rather than model output alone."),
    "flag_rate": (DIRECTIONAL,
        "Ambiguous by definition. A rise can mean worse output, a stricter "
        "policy, or more careful reviewers. Never read it alone."),
    "avg_minutes_saved": (DIRECTIONAL,
        "A self-reported estimate. Fine for comparing workflows to each "
        "other, not for adding into a savings figure for a budget."),
    "user_rating": (DIRECTIONAL,
        "Human judgement, which is what we want, but unweighted, and one day "
        "is missing it entirely."),
    "median_confidence": (DO_NOT_TRUST,
        "Model-reported confidence. It measures how sure the model sounds, "
        "not whether it was right. Here it rises while human signals fall."),
}

#the rates

def add_rates(df):
    """Attach rate columns. Denominators are named, never implied."""
    out = df.copy()
    out["completion_rate"] = out["completed"] / out["sessions"]
    out["accepted_per_completed"] = out["accepted_output"] / out["completed"]
    out["accepted_per_session"] = out["accepted_output"] / out["sessions"]
    out["flag_rate"] = out["flagged_for_review"] / out["sessions"]
    return out

#weighted averaging

def _weighted(values, weights):
    """Session-weighted mean that ignores missing values."""
    v = pd.Series(values, dtype="float64")
    w = pd.Series(weights, dtype="float64")
    ok = v.notna() & w.notna() & (w > 0)
    if not ok.any():
        return np.nan
    return float((v[ok] * w[ok]).sum() / w[ok].sum())

#the rollup

def summarise(df, by=("team", "workflow", "source")):
    """Roll up to any grain, weighting by sessions."""
    by = list(by)
    rows = []
    for keys, g in df.groupby(by, dropna=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rec = dict(zip(by, keys))
        rec["days"] = g["date"].nunique()
        rec["sessions"] = int(g["sessions"].sum())
        rec["completion_rate"] = g["completed"].sum() / g["sessions"].sum()
        rec["accepted_per_completed"] = g["accepted_output"].sum() / g["completed"].sum()
        rec["accepted_per_session"] = g["accepted_output"].sum() / g["sessions"].sum()
        rec["flag_rate"] = g["flagged_for_review"].sum() / g["sessions"].sum()
        rec["avg_minutes_saved"] = _weighted(g["avg_minutes_saved"], g["sessions"])
        rec["user_rating"] = _weighted(g["user_rating"], g["sessions"])
        rec["median_confidence"] = _weighted(g["median_confidence"], g["sessions"])
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("sessions", ascending=False)

