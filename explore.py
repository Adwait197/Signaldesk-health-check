# Scratch file used to explore the raw data and find issues before building
# the app. Kept as a record of how each data problem was found.

''' import pandas as pd

df = pd.read_csv("sample-data/product_usage_events.csv")

print("--- Q1: what is one row? ---")
print("rows:", len(df))
print(df[["date", "team", "workflow", "source"]].drop_duplicates().shape[0],
      "unique date+team+workflow+source combos")

print("\n--- Q2: column types ---")
print(df.dtypes)

print("\n--- Q3: missing values ---")
print(df.isna().sum()[df.isna().sum() > 0])

print("\n--- Q5: category labels ---")
for col in ["team", "workflow", "source"]:
    print(col, "->", sorted(df[col].unique()))

print("\n--- Q6: ranges ---")
print(df[["sessions", "median_confidence", "user_rating"]].describe().round(2))

print("\n--- Q7: rows per date ---")
print(df.groupby("date").size())

print("\n--- Q8: what are these dates? ---")
dates = pd.to_datetime(df["date"])
print(df.assign(day=dates.dt.day_name())
        .groupby(["date", "day"])["sessions"].sum()) '''


import pandas as pd
from signaldesk.clean import clean

pd.set_option("display.width", 200)
df, log, coverage = clean("sample-data/product_usage_events.csv")

print("rows: 41 ->", len(df))
print("\n--- QUARANTINE LOG ---")
print(log.to_string(index=False))
print("\n--- COVERAGE ---")
print(coverage.to_string(index=False)) 

from signaldesk.metrics import add_rates, summarise

df = add_rates(df)
print("\n--- SCORECARD ---")
print(summarise(df).round(3).to_string(index=False))

from signaldesk.detect import find_divergence

print("\n--- DIVERGENCE ---")
for f in find_divergence(df):
    print(f"[{f['severity']}] {f['workflow']} / {f['source']} "
          f"({f['sessions']} sessions)")
    print(f"    {f['summary']}")

    from signaldesk.detect import daily_break

print("\n--- DAILY BREAKS ---")
for b in daily_break(df):
    print(f"{b['workflow']} / {b['source']} on {b['date']:%b %d}  — note: {b['note']}")
    for k, v in sorted(b["moves"].items(), key=lambda x: x[1]):
        print(f"    {k}: {v:+.0%}")
    print(f"    model confidence: {b['confidence_move']:+.0%}")