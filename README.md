# SignalDesk Weekly Health Check

A small Streamlit tool that answers about SignalDesk's AI workflows.

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Track Chosen 

Track 1, Fictional Domain Packet.

## What I Built

 A Streamlit health check that flags workflows where model confidence trends up while human signals (completion, acceptance, rating, minutes saved) trend down. A second check compares the latest day against its own 3-day baseline, since a weekly trend line smooths out sudden breaks. Three tabs: flagged findings, a quarantine log of every row I changed, and what this data cannot answer.

Findings: Support/Reply draft broke Aug 7, minutes saved −63%, rating −50%, flags +209%, while confidence rose to its weekly high of 0.91. Feedback clustering degrades with scale: completion 75%→58% as sessions grow 12→31. Best performer is Lead summary/email (66% accepted per session, 7% flag rate). Least trustworthy metric is median_confidence.

## Who It Is For

The SignalDesk owner and the team, in their weekly review.
It takes five minutes: open it, see what is flagged, pick what to look into
that week. The owner gets a short list to act on instead of a dashboard to
read. The team gets a plain answer on which numbers they can trust.


## Data Source

sample-data/product_usage_events.csv  41 rows, 7 days. 39 survive cleaning.

## Assumptions

- **Sources are never averaged together.** In every workflow, `manual` runs
  score lower than the automated source. Combining them gives a number that
  describes neither.
- **Rates are session-weighted.** A plain average of daily percentages would
  let a 5-session day count as much as a 75-session day.
- **Both denominators are reported.** `accepted_per_completed` asks if the
  model does good work; `accepted_per_session` asks if the tool actually
  helps. Feedback clustering is 68% by one and 44% by the other, and that gap
  is the finding.
- **Missing is not zero.** A blank rating means nobody rated it, not that
  somebody gave it a zero.
- **Rising flags are ambiguous on their own.** More flags can mean worse
  output, a stricter policy, or more careful reviewers.


## Issues Noticed

- **A duplicate row**, and that same row is demo-account traffic. Deleting the
  duplicate is not enough, since the copy left behind is still fake usage. I
  removed both, which costs Aug 5 its Sales/email row. I chose the visible gap
  over a flattering number.
- **`product` written instead of `Product`.** To a groupby these are two
  different teams.
- **The text `n/a` in a numeric column.** pandas turns it into a null
  automatically, so the bad value disappears before anyone notices.
- **Aug 7 has four rows instead of six.** Day totals for Aug 7 are not
  comparable, though the individual rows are fine.
- **Aug 1 and 2 are a weekend.** The session "growth" across the week is partly
  the working week starting, and the Aug 4 prompt comparison has a weekend
  sitting in its before-window.


## **What I Would Do Next:**

- **Compare like weekdays across two full weeks** before reading any trend as
  real, so the weekend stops distorting the picture.
- **Get a distinct user count.** Sessions are runs, not people. Every volume
  number here could be a handful of enthusiastic users.
- **Investigate Feedback clustering's completion rate.** Falling 75% to 58% as
  uploads grow points at a size limit or timeout, which is an engineering fix
  rather than a model problem.
- **Split the flag column in two.** A policy flag and a user flag are different
  events sharing one column, which is why Aug 7 was hard to read.
- **Tag every session with the prompt version that produced it.** Without it,
  "did the Aug 4 change help?" stays unanswerable. No amount of analysis fixes
  a missing column.








