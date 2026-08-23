# AI Collaboration Note

## Did You Use AI?

Yes, from start to finish. Mostly Claude, plus Copilot for autocomplete
while editing. I use both most days and I did not change how I work for this.

## How You Used It

Roughly in the order it happened.

I read the CSV myself first, starting with the notes column, because that is a person telling you something. That gave me the duplicate row, the 140-session spike, the missing confidence value, and Aug 7 having four rows where every other day had six.

Then I used AI as a second reader, it suggested a checklist — column types, category labels, value ranges, group coverage — which I ran in code. That caught two things I missed: product written lowercase, which silently splits a groupby, and that pandas converts the text n/a to a null automatically, so the bad value vanishes before anyone sees it.

Then I argued through scope. I described what the packet ruled out and worked through options.AI then drafted the Streamlit layout and boilerplate. I decided the structure: separate cleaning, metrics and detection modules, plus a quarantine log showing every change on screen.

I also used it as a sounding board on the detector design. I went back and
forth on whether to compare the first day to the last day, or fit a line
through the whole week. I went with the line, because the first day is a
Saturday and the last day is the policy change day, so comparing those two
endpoints would have let the two strangest days in the file define the entire
trend.

## One Prompt, Workflow, Or Moment That Helped

The prompt was checking the day to start off.Before analyzing anything, I made sure which weekday each date fell on. August 1 and 2, 2026 fall on Saturday and Sunday.

This completely altered my approach to the entire dataset. The sessions rise
every day and the natural conclusion would be that the use of the product is
growing, or the prompt change on August 4 took effect. Part of that growth is
simply due to the fact that a new working week starts. As well, since the prompt
change happens on the 4th, the 'before' time frame includes weekends, thus,
when comparing 'before' and 'after', part of the analysis reflects the calendar
and not the prompt.

There is no information about this in the packet itself and the notes column
does not contain any clues about this either. This is the result of the
habit of figuring out what a date column really means before drawing a trend
on top of it. It became the first item in the "What this data cannot answer"
tab in the tool.

## One Thing You Verified Or Decided Yourself

**Decided.** The duplicate entry on August 5 also comes from demo-account traffic.
The natural thing would have been to remove the duplicate entry and continue. I did not believe that was good enough since the duplicate that remains is not genuine and every figure on it seems too good to be true. Both entries were therefore removed.

This is a cost. There will now be no Sales/email entry for August 5 making it an incomplete day. I opted for the gap rather than the inflated figure and ensured the tool made this fact known through the interface.

**Verified, and found the code was wrong.** The detector rates workflows according to
the severity level. Lead summary has been rated Medium, which is the same
category as workflows which were failing.

This is where I felt uneasy. Lead summary was the most efficient workflow among
all in the dataset; therefore, it being on the same category with Support
workflow raised my doubt regarding the rule rather than the workflow itself.

When I checked the figures which corresponded to the labels, I saw that
signals in the Lead summary have decreased for less than 3%, which is just
above the threshold for noise. I set the minimum size of the fall for severity,
and Lead summary got rightly labeled as Watch.

I am including this because it is the kind of thing that is easy to miss. The
code ran, the output looked reasonable, and nothing failed. It was only wrong
if you knew the data well enough to disagree with it.

That is roughly my rule of thumb. AI output is a draft. Anything a reader might
act on gets checked against the source before it ships, and if the output
disagrees with what I know about the data, I assume the code is wrong before I
assume I am.
