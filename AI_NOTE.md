# AI Collaboration Note

## Did You Use AI?

Yes, heavily, from start to finish. Mostly Claude, plus Copilot for autocomplete
while editing. I use both most days and I did not change how I work for this.

## How You Used It

Roughly in the order it happened.

I started by reading the packet and the CSV myself. 41 rows is small enough to
read line by line, so I did that first, and then went through it again with AI
help as a second pass. I wanted a check that was not looking for the same
things I was.

Then I argued through scope. I described what the packet ruled out (not a big
BI project, do not trust confidence, one small artifact) and worked through
options. Two got thrown out for being too broad: a full comparison dashboard
across all workflows, and a metric dictionary with no actual analysis behind
it.

For the build, AI wrote most of the first draft of the Streamlit layout and the
boilerplate in the three modules. That is the part I type slowest and care
about least.

I also used it as a sounding board on the detector design. I went back and
forth on whether to compare the first day to the last day, or fit a line
through the whole week. I went with the line, because the first day is a
Saturday and the last day is the policy change day, so comparing those two
endpoints would have let the two strangest days in the file define the entire
trend.

Where I did not use it: deciding what to build, deciding what to do with the
demo rows, and the date check below.

## One Prompt, Workflow, Or Moment That Helped

It was not a clever prompt. It was asking a boring question early.

Before doing any analysis I checked what day of the week each date actually
fell on. August 1 and 2, 2026 are a Saturday and a Sunday.

That changed how I read the whole file. Sessions climb steadily across the week
and the obvious conclusion is that adoption is growing, or that the August 4
prompt change worked. A good part of that climb is just the working week
starting. And because the prompt change lands on the 4th, the before window
contains a weekend, so any before and after comparison is partly measuring the
calendar rather than the prompt.

Nothing in the packet points at this and the notes column does not mention it.
It came from a habit of checking what a date column literally is before
drawing a trend on top of it. It is now the first thing in the tool's "what
this data cannot answer" tab.

## One Thing You Verified Or Decided Yourself

Two, one of each.

**Decided.** The duplicated row on August 5 is also demo-account traffic. The
obvious move is to delete the duplicate and carry on. I decided that was not
enough, because the copy that survives is still not real usage, and every
number on it is suspiciously perfect. I removed both.

That decision costs something. August 5 ends up with no Sales/email row at all,
so that day is incomplete. I chose the visible gap over the flattering number,
and made the tool announce the gap on screen rather than quietly having one.

**Verified, and found the code was wrong.** The detector ranks each workflow by
severity. It came back with Lead summary marked Medium, the same tier as
workflows that were genuinely falling apart.

That did not sit right with me. Lead summary was the best performer in the
whole dataset by every measure I had looked at, so seeing it in the same
bracket as Support made me suspicious of the rule rather than the workflow.

When I printed the actual numbers behind the labels, Lead summary's signals had
fallen by less than 3%, barely above the noise threshold. Support's had fallen
by 41%. Both were labelled Medium because the rule counted how many signals
were falling and paid almost no attention to how far. I added a minimum size
before a fall counts toward severity, and Lead summary correctly dropped to
Watch.

I am including this because it is the kind of thing that is easy to miss. The
code ran, the output looked reasonable, and nothing failed. It was only wrong
if you knew the data well enough to disagree with it.

That is roughly my rule of thumb. AI output is a draft. Anything a reader might
act on gets checked against the source before it ships, and if the output
disagrees with what I know about the data, I assume the code is wrong before I
assume I am.
