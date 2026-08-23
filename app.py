#setup

from pathlib import Path
import pandas as pd
import streamlit as st

from signaldesk.clean import clean
from signaldesk.metrics import (TRUST, TRUSTED, DIRECTIONAL, DO_NOT_TRUST,
                                add_rates, summarise)
from signaldesk.detect import find_divergence, daily_break
from signaldesk.charts import divergence_frame

DATA = Path(__file__).parent / "sample-data" / "product_usage_events.csv"
st.set_page_config(page_title="SignalDesk Health Check", layout="wide")


@st.cache_data
def load():
    df, log, cov = clean(DATA)
    return add_rates(df), log, cov


df, quarantine, coverage = load()

st.title("SignalDesk Weekly Health Check")
st.caption(
    f"{df['date'].min():%b %d} to {df['date'].max():%b %d, %Y} · "
    f"{len(df)} usable rows · {int(df['sessions'].sum())} sessions · "
    f"{len(quarantine)} data issues logged"
)

tab1, tab2, tab3 = st.tabs(
    ["Health check", "Data quality", "What this data cannot answer"])

#tab 1, the findings

with tab1:
    st.subheader("Where the model's self-report disagrees with its users")
    st.write(
        "Each workflow is checked for one thing: model confidence trending up "
        "while human signals trend down. That gap means confidence has stopped "
        "tracking whether the output was actually useful."
    )

    findings = find_divergence(df)
    icon = {"High": "🔴", "Medium": "🟠", "Low": "🟡",
            "Watch": "⚪", "No divergence": "🟢", "Not enough data": "⚫"}

    for f in findings:
        st.markdown(
            f"**{icon[f['severity']]} {f['severity']} — {f['workflow']} · "
            f"{f['source']}**  \n"
            f"{f['summary']}  \n"
            f"<span style='opacity:.6;font-size:.85rem'>{f['team']} · "
            f"{f['sessions']} sessions over {f['days']} days</span>",
            unsafe_allow_html=True)
        if f["falling"]:
            st.markdown("  \n".join(
                f"&nbsp;&nbsp;↓ {label} {chg:+.0%}" for label, chg in f["falling"]),
                unsafe_allow_html=True)
        st.divider()

#the chart, attached to the top finding

    top = findings[0]
    if top["severity"] in ("High", "Medium"):
        st.subheader(f"Why {top['workflow']} · {top['source']} is flagged")
        st.write(
            "Both lines start at zero on day one. If the AI's self-rating "
            "were tracking reality, they would move together."
        )
        st.line_chart(divergence_frame(df, top["team"], top["workflow"],
                                       top["source"]))
        st.caption("Percent change from each measure's own starting value.")

#the daily break

    breaks = daily_break(df)
    if breaks:
        st.subheader("Single days that broke from their own baseline")
        for b in breaks:
            st.error(
                f"**{b['workflow']} · {b['source']} · {b['date']:%b %d}**  \n"
                f"Export note: *{b['note']}*")
            cols = st.columns(len(b["moves"]) + 1)
            for c, (k, v) in zip(cols, sorted(b["moves"].items(),
                                              key=lambda x: x[1])):
                c.metric(k, f"{v:+.0%}")
            cols[-1].metric("model confidence",
                            f"{b['confidence_move']:+.0%}")

#scorecard and trust badges

    st.subheader("Workflow scorecard")
    st.caption("Session-weighted. Sources kept apart because they are not comparable.")
    st.dataframe(
        summarise(df)[["workflow", "source", "sessions", "completion_rate",
                       "accepted_per_completed", "accepted_per_session",
                       "flag_rate", "avg_minutes_saved", "user_rating",
                       "median_confidence"]]
        .style.format({"completion_rate": "{:.0%}",
                       "accepted_per_completed": "{:.0%}",
                       "accepted_per_session": "{:.0%}",
                       "flag_rate": "{:.0%}", "avg_minutes_saved": "{:.1f}",
                       "user_rating": "{:.2f}", "median_confidence": "{:.2f}"}),
        use_container_width=True, hide_index=True)

    st.subheader("What each column is worth")
    colour = {TRUSTED: "🟢", DIRECTIONAL: "🟠", DO_NOT_TRUST: "🔴"}
    for metric, (tier, why) in TRUST.items():
        st.markdown(f"{colour[tier]} **`{metric}`** — *{tier}*  \n"
                    f"<span style='opacity:.7;font-size:.85rem'>{why}</span>",
                    unsafe_allow_html=True)

#tabs 2 and 3

with tab2:
    st.subheader("Everything this tool changed about the raw export")
    st.write("Nothing is dropped silently. If you disagree with a decision "
             "here, the row is named and the reasoning is on screen.")
    st.dataframe(quarantine, use_container_width=True, hide_index=True)

    st.subheader("Day coverage")
    st.write("Two days are missing rows. Day-level totals for those dates are "
             "not comparable. Individual workflow rows on those days are fine.")
    st.dataframe(coverage.assign(date=coverage["date"].dt.strftime("%Y-%m-%d")),
                 use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Did the August 4 prompt change help?")
    st.error("This data cannot answer that. Any number you compute will mislead.")
    st.markdown("""
1. **The before period is a weekend.** August 1 and 2 are Saturday and Sunday.
   Volume climbing after August 3 is largely the working week starting.
2. **The after period contains two other events** — a demo-account spike on the
   5th and a review policy change on the 7th.
3. **Three days on each side** is too few to separate a real effect from an
   ordinary week.

**To answer it properly:** tag each session with the prompt version that
produced it, hold one team on the old prompt, and compare like weekdays across
at least two full weeks.
""")

    st.subheader("Open questions for the team")
    st.markdown("""
- Which prompt version produced each session?
- Did the August 7 policy change apply to all of Support, or one queue?
- Is `avg_minutes_saved` reported by the user or estimated by the system?
- Feedback clustering's completion falls 75% → 58% as volume grows 12 → 31.
  Size limit, or timeout?
- How many distinct users are behind these sessions?
""")