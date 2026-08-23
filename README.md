# SignalDesk Weekly Health Check

A small Streamlit tool that answers one question about SignalDesk's AI
workflows: **is the model getting more confident while the people using it get
less happy?**

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Track Chosen 

Track 1, Fictional Domain Packet.

## What I Built

 A Streamlit health check that flags workflows where model confidence trends up while human signals (completion, acceptance, rating, minutes saved) trend down. A second check compares the latest day against its own 3-day baseline, since a weekly trend line smooths out sudden breaks. Three tabs: flagged findings, a quarantine log of every row I changed, and what this data cannot answer.

Findings: Support/Reply draft broke Aug 7 — minutes saved −63%, rating −50%, flags +209%, while confidence rose to its weekly high of 0.91. Feedback clustering degrades with scale: completion 75%→58% as sessions grow 12→31. Best performer is Lead summary/email (66% accepted per session, 7% flag rate). Least trustworthy metric is median_confidence.

## Who It Is For

The team, for five minutes on a Monday. If nothing is flagged, closing the tab is the right outcome.That is also why the tabs are in the order they are: what needs attention, then whether the data can be believed, then what still cannot be answered.



## Data Source

sample-data/product_usage_events.csv — 41 rows, 7 days. 39 survive cleaning.

## Assumptions

Sources never averaged (manual scores lower everywhere). Rates session-weighted. 

Both denominators are reported. accepted_per_completed asks whether the model does good work. accepted_per_session asks whether the tool actually helps.— Feedback clustering is 68% accepted-per-completed but 44% accepted-per-session, and that gap is the finding. Demo traffic is removed entirely, not just deduplicated.
A missing value is missing, not zero. A blank rating does not mean somebody gave it a zero. Rising flags treated as ambiguous.

## Issues Noticed

Duplicate row; that row is also demo traffic (removing both costs Aug 5 its Sales/email row — I chose the gap over a flattering number); product vs Product; n/a text in a numeric column that pandas silently hides; blank rating; Aug 7 missing two rows; Aug 1–2 are a weekend, so the session "growth" is partly the working week starting and the Aug 4 prompt comparison has a weekend in its before-window.

## Next

Tag sessions with prompt version — without it, "did the change help?" stays unanswerable. Then distinct user counts, and Feedback clustering's timeout.










