#Setup

import pandas as pd

GRAIN = ["team", "workflow", "source"]

NUMERIC_COLS = [
    "sessions", "completed", "accepted_output", "flagged_for_review",
    "avg_minutes_saved", "median_confidence", "user_rating",
]


def _log(entries, date, key, issue, action):
    entries.append({"date": str(date)[:10], "row": key,
                    "issue": issue, "action": action})


def load_raw(path):
    # keep_default_na=False stops pandas from silently converting "n/a".
    # dtype=str reads everything as text so we can SEE the bad values first.
    return pd.read_csv(path, keep_default_na=False, dtype=str)

#numbers

def clean(path):
    raw = load_raw(path)
    log = []
    df = raw.copy()

    # --- Team casing: 'product' vs 'Product' ---
    bad_case = df["team"] != df["team"].str.strip().str.title()
    for _, r in df[bad_case].iterrows():
        _log(log, r["date"], f"{r['team']} / {r['workflow']}",
             f"Team cased as '{r['team']}'", "Normalised to title case")
    df["team"] = df["team"].str.strip().str.title()
    for c in ["workflow", "source", "notes"]:
        df[c] = df[c].str.strip()

    # --- Text hiding in numeric columns ---
    for col in NUMERIC_COLS:
        coerced = pd.to_numeric(df[col], errors="coerce")
        broke = coerced.isna() & (df[col].str.strip() != "")
        for _, r in df[broke].iterrows():
            _log(log, r["date"], f"{r['team']} / {r['source']}",
                 f"{col} contained the text '{r[col]}'",
                 "Set to missing; excluded from that metric only")
        for _, r in df[df[col].str.strip() == ""].iterrows():
            _log(log, r["date"], f"{r['team']} / {r['source']}",
                 f"{col} is blank", "Set to missing; NOT treated as zero")
        df[col] = coerced

    df["date"] = pd.to_datetime(df["date"])

    #duplicates and demo traffic

        # --- Exact duplicates ---
    # Compare on everything EXCEPT notes, because notes is where the
    # exporter recorded that one copy was a duplicate.
    compare_cols = [c for c in df.columns if c != "notes"]
    dupes = df.duplicated(subset=compare_cols, keep="first")
    for _, r in df[dupes].iterrows():
        _log(log, r["date"].date(), f"{r['team']} / {r['source']}",
             "Exact duplicate of an earlier row", "Removed the second copy")
    df = df[~dupes].copy()

    # --- Demo traffic: dedupe is NOT enough, the row itself is fake ---
    demo = df["notes"].str.contains("demo account", case=False, na=False)
    for _, r in df[demo].iterrows():
        _log(log, r["date"].date(), f"{r['team']} / {r['source']}",
             f"Demo-account traffic ({int(r['sessions'])} sessions, "
             f"rating {r['user_rating']})", "Excluded from all metrics")
    df = df[~demo].copy()

    df["day_name"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek >= 5

    #coverage check

    coverage = _coverage(df, log)
    log_df = pd.DataFrame(log).sort_values("date").reset_index(drop=True)
    return df.reset_index(drop=True), log_df, coverage


def _coverage(df, log):
    """Which days are missing rows they should have."""
    expected = set(map(tuple, df[GRAIN].drop_duplicates().values))
    rows = []
    for date, g in df.groupby("date"):
        present = set(map(tuple, g[GRAIN].values))
        missing = sorted(expected - present)
        rows.append({"date": date, "day_name": date.day_name(),
                     "expected": len(expected), "present": len(present),
                     "missing": ", ".join(" / ".join(m) for m in missing) or "-",
                     "complete": len(missing) == 0})
        for m in missing:
            _log(log, date.date(), " / ".join(m),
                 "No row for this workflow on this day",
                 "Day-level totals for this date are not comparable")
    return pd.DataFrame(rows)