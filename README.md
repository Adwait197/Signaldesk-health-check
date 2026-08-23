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

Track 1, the Fictional Domain Packet, using
`sample-data/product_usage_events.csv`.

I picked it over bringing my own dataset for a simple reason. This file has
problems planted in it on purpose, and someone already knows what they are.
Working with a messy file where I can be checked seemed like a better test than
picking a clean one I control.

---

## What I Built

Three tabs.

**Health check.** The main piece is a divergence detector. For every workflow
and source it fits a trend line to the model's own confidence score, and to
four human signals: completion, acceptance, user rating and minutes saved. If
confidence trends up while human signals trend down, it gets flagged and ranked
by severity.

A trend line across a whole week can smooth out a single bad day, so there is
a second check underneath. It compares the most recent day against the average
of the three days before it. Slow drift and sudden breaks are different
problems and one check will not catch both.

Below the findings is a scorecard where every column carries a plain-English
trust label: Trusted, Directional, or Do not trust as quality.

**Data quality.** A log of every row the tool changed or removed, with the
reason written next to it, plus a table showing which days are missing rows.

**What this data cannot answer.** A written explanation of why the August 4
prompt change cannot be evaluated with this export, and what would be needed to
evaluate it properly.

### A note on why this is not a dashboard

I nearly built a grid of charts, one per metric per workflow. I did not,
because the teammate asked what to look at next, and a grid of charts makes
them find the answer themselves. So the tool does the analysis and reports a
verdict, and charts only appear to explain a finding it has already made. Any
workflow that is fine gets one green line saying so, not four charts proving
it.

### What it found

**1. Support's Reply draft broke on August 7.** Against the three days before
it:

| | Baseline (Aug 4-6) | Aug 7 |
|---|---|---|
| Minutes saved | 4.1 | 1.5 (−63%) |
| User rating | 4.17 | 2.10 (−50%) |
| Accepted per session | 0.65 | 0.27 (−59%) |
| Flag rate | 13% | 40% (+209%) |
| **Model confidence** | **0.87** | **0.91 (+5%)** |

Everything a human touches collapsed. The model's confidence in itself went up,
to its highest value of the week.

The flag rate on its own does not prove anything, because the export note says
the review policy changed that day, and a stricter policy would naturally flag
more. What makes this a real problem is that user rating and minutes saved fell
at the same time, and a policy cannot make a person rate an output worse.

**2. Feedback clustering gets worse as it gets used more.** I did not spot this
by eye. The detector found it.

| Date | Sessions | Completion | Confidence |
|---|---|---|---|
| Aug 1 | 12 | 75% | 0.59 |
| Aug 3 | 18 | 67% | 0.61 |
| Aug 5 | 24 | 62% | 0.64 |
| Aug 7 | 31 | 58% | 0.67 |

Volume up, completion down, confidence up, every single day. This looks more
like a size limit or a timeout on bigger uploads than a model quality problem,
which would make it fixable.

**3. The most useful workflow right now is Lead summary via email.** 66% of
sessions end in an accepted output, a 7% flag rate which is half of Support's,
a 4.22 rating, and 8.5 minutes saved per run. The caveat is that it only has
six days of data instead of seven, because the demo rows were removed from
August 5. So it is both the best performer and the one with the thinnest
evidence.

**4. The metric to trust least is `median_confidence`,** and it is not close.
The workflow with the highest confidence (Support, 0.86) has the worst flag
rate. The workflow with the lowest confidence (Feedback clustering, 0.56) saves
by far the most time. The relationship is closer to backwards than useful.

---

## Who It Is For

The person who owns SignalDesk, and whoever runs the weekly review.

I built it for five minutes on a Monday morning. Open it, see if anything is
flagged, decide what to look into. It is not something anyone should have open
all day. If nothing is flagged, closing the tab is the correct outcome.

That is also why the tabs are in the order they are: what needs attention, then
whether the data can be believed, then what still cannot be answered.

---

## Data Or Source Used

`sample-data/product_usage_events.csv` from the challenge repo. 41 rows,
7 days (Aug 1 to Aug 7, 2026), 3 workflows across 3 teams and 3 input sources.
No external data. 39 rows survive cleaning. The file is committed so the app
runs offline.

---

## Assumptions I Made

- **Sources are never averaged together.** In every workflow, the `manual`
  source scores lower than the automated one on confidence, acceptance and
  minutes saved. Combining them gives a number that describes neither, and if
  the mix between them shifts the combined number moves on its own.
- **All rates are session-weighted.** A plain average of daily percentages
  lets a 5-session day count as much as a 75-session day.
- **Both denominators are reported.** `accepted_per_completed` asks whether the
  model does good work. `accepted_per_session` asks whether the tool actually
  helps. For Feedback clustering these are 68% and 44%, and the gap between
  them is itself the finding: a third of attempts never produce anything.
- **Minutes saved is credited only to accepted outputs.** Counting every
  session would assume a rejected output cost nothing to produce.
- **Demo traffic is removed entirely, not just deduplicated.**
- **A missing value is missing, not zero.** A blank rating does not mean
  somebody gave it a zero.
- **A rising flag rate is treated as ambiguous unless something else supports
  it**, since it can mean worse output, a stricter policy, or more careful
  reviewers.
- **Incomplete days are reported, not dropped.** A day can be missing rows
  while the rows it does have are perfectly valid.

---

## Data Issues Or Caveats I Noticed

All of these appear in the app's Data quality tab.

**1. A duplicate export row.** August 5, Sales/email, an exact copy of the row
above it.

**2. That same row is demo-account traffic.** 140 sessions, 0.95 confidence,
4.9 rating, all far outside the range of anything else in the file. Removing
the duplicate is the obvious fix and it is not enough, because the copy that
survives is still not real usage. A demo run is someone showing the tool off.
Nothing gets rejected because there is no real task to fail at. Left in, that
one row raises Lead summary's weekly acceptance from 61% to 66% and adds about
1,400 minutes to the time saved estimate.

I removed both copies. That leaves August 5 with no Sales/email row at all,
which is a real cost, and the coverage table flags it. I would rather have a
visible gap than a number that flatters the product.

**3. Team written as `product` instead of `Product`** on August 2. To me they
are the same team. To a groupby they are two different teams, and Product's
numbers would split across two buckets with one of them holding a single day.

**4. `median_confidence` contains the literal text `n/a`** on August 5. This
one is worth flagging for a reason beyond the value itself. pandas treats `n/a`
as missing by default, so the bad value disappears before anyone notices it
existed, and the column still loads as clean numbers. That worked out here. If
the cell had said `unknown` or `-`, the whole column would have loaded as text
and every average would have been wrong or crashed. So the tool reads the file
as raw text first, logs what it finds, and converts afterwards.

**5. A blank `user_rating`** on August 1.

**6. August 7 only has 4 rows instead of 6.** Two manual rows are simply not
there. Anyone computing a daily total will see August 7 crash from 217 sessions
to 134 and report a disaster that is mostly missing rows. The individual
workflow rows for that day are still fine, which matters, because one of them
is the most important row in the file.

**7. August 1 and 2 are a Saturday and a Sunday.** This is the one I think is
easiest to miss and does the most damage.

Sessions climb across the week (143, 161, 174, 189, 217) and the obvious read
is that the tool is catching on. A large part of that is the working week
starting. People do not use internal tools much on weekends.

It gets worse when you try to evaluate the prompt change on August 4, because
the before window is Saturday, Sunday, Monday and the after window is Tuesday
onwards. There is a weekend sitting inside the before period. Any before and
after comparison here is partly measuring the calendar.

**8. Two separate changes inside seven days.** A prompt change on the 4th and a
review policy change on the 7th, with the demo spike between them.

### Limits of the tool itself

The trend check needs at least three days and is being asked to read a
seven-day window, which is thin. It cannot tell a real decline from an unlucky
week. It is a prompt to go and look, not evidence.

---

## What I Would Do Next With More Time

**First, and before anything else: tag every session with the prompt version
that produced it.** The team's actual question is whether the change helped,
and right now that is unanswerable. No amount of analysis fixes a missing
column.

After that:

- **Handle the weekday problem properly.** Compare like weekdays across at
  least two full weeks before reading any trend as real.
- **Get a distinct user count.** `sessions` are runs, not people. Every volume
  number in here could be a handful of enthusiastic users, and nothing in this
  file can rule that out.
- **Look into Feedback clustering's completion rate.** It falls from 75% to
  58% as uploads grow from 12 to 31 sessions. That pattern points at a size
  limit or a timeout, which is an engineering fix rather than a model problem.
- **Split the flag column in two.** A policy flag and a user flag are different
  events sharing one column. Splitting them would have made August 7 readable
  straight away.
- **Add a confidence calibration view.** Group sessions by their confidence
  score and chart the actual acceptance rate in each group. If the line is
  flat, confidence is decorative and should come off every dashboard the team
  has.
- **Move the cleaning rules into dbt tests** if this export ever becomes a real
  table, so the quarantine log is produced by the pipeline instead of
  recomputed by this app every time.

### What I deliberately did not build

Trend charts for every metric, a date range filter, and a per-workflow
drill-down. All three were straightforward and none of them would have changed
a decision anyone makes on Monday morning. The packet asked for one small
useful artifact, so I spent the time on the judgment instead.
