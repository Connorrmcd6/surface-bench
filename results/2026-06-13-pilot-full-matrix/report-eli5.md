# The pilot, in plain English

A jargon-free companion to `report.md`. Same findings, no computer-science vocabulary. If you use
AI assistants but don't write code, start here.

---

## The one-sentence version

We tested whether **out-of-date documentation makes an AI coding assistant mess up** — and it does,
badly: when the AI can't double-check the real code, outdated docs made *every* AI we tried get the
answer wrong **100% of the time**, and using a smarter, more expensive AI didn't help at all. The
good news: a tool that simply **flags "this doc is out of date"** fixed the problem.

## The picture to hold in your head

Imagine you hire a skilled handyman (the AI) to make a change in a large building. You hand them a
page of **notes** describing how part of the building works. Sometimes those notes are current.
Sometimes they're **stale** — someone re-did the wiring months ago but never updated the notes.

We wanted to know: when the notes are stale, does the handyman make a mistake? And does it help to
slap a sticky note on the page saying *"heads up — this is out of date, here's what actually
changed"*? That sticky note is what **Surface** (the tool this benchmark exists to test) does.

## How we tested it

For every task we tried the same job four ways, changing **only** what paperwork the handyman got:

- **No notes** — just let them look at the actual wiring.
- **Stale notes** — outdated paperwork, plus the wiring.
- **Fresh notes** — correct paperwork, plus the wiring.
- **Stale notes + the Surface flag** — outdated paperwork, but with the "this page is wrong, here's
  the real change" sticky note attached.

And we ran it two ways, which turned out to be the whole story:

- **Wiring visible** — the exact thing they need to touch is right in front of them, so they can
  ignore the notes and just look.
- **Wiring hidden** — the part they *depend on* is behind a wall. They can't look at it; they can
  only go by the notes. **This is the realistic case** — in a big project, nobody can see every
  piece, so you trust the documentation as your map.

We tried this across three Claude models — from the cheapest and fastest up to the most powerful —
and repeated each task ten times to make sure the results weren't a fluke.

## What we found

**When the wiring was hidden (the realistic case):**

- **Stale notes made every model fail — 100% of the time.** Not "sometimes." Every single run, the
  AI confidently did the wrong thing, because the only information it had was wrong.
- **A smarter, pricier AI was no better.** The top-tier model failed exactly as often as the
  cheapest one. You can't buy your way out of bad docs.
- **Fresh notes fixed it completely** — 100% correct.
- **The Surface flag fixed it too.** Just telling the AI "this page is stale, here's what really
  changed" brought it back to right almost every time. That's the whole value of the tool, shown
  end to end.

**When the wiring was visible:**

- Outdated notes *didn't* make the AI wrong — it just looked at the real thing and got it right.
- **But it cost more.** The AI did noticeably more work second-guessing the bad notes against what
  it could see. (AI "work" is measured in something called *tokens* — basically how much it has to
  read and write, which maps directly to time and money.) So even harmless-looking rot quietly runs
  up your bill.

**The bumper-sticker takeaway:** *documentation rot you can't see makes the AI wrong; documentation
rot you can see makes it slower and more expensive.* Either way it costs you — and a better model
doesn't save you, but catching the rot does.

The whole study cost about **$14** in AI usage and had **zero** technical failures in the final
data.

## A few things we learned along the way

- **How you ask matters enormously.** Our very first attempt found *nothing* — because we had
  accidentally told the AI "trust the code over the docs," which is exactly the instinct that hides
  the problem. Once we stopped putting our thumb on the scale, the real effect appeared.
- **The damage only shows up when the AI can't double-check.** That's the core insight: stale docs
  are dangerous precisely for the parts of a system the AI can't see — which, in any real codebase,
  is most of it.
- **We even caught ourselves cheating by accident.** In one early test the AI kept getting the right
  answer for the wrong reason, and digging in, we found a stray hint we'd left in our own
  instructions. We removed it. (Reassuringly, the test was sensitive enough to catch our mistake.)
- **One technical hiccup mid-run.** A single request to the AI froze and stalled everything; we
  added a safety timeout so one bad request can't hold up the whole study, kept all the good data,
  and re-ran only the unfinished part.

## What's next

- **Test a back-and-forth AI, not a one-shot one.** Real assistants work in a loop — read, try, run
  tests, fix. That's where wasted effort from bad docs probably piles up fastest.
- **Test other companies' AIs**, not just Claude, to see if "a smarter model doesn't help" holds
  everywhere.
- **Try it on a real, public codebase** instead of our purpose-built examples — the most convincing
  proof.

---

*For the full numbers, confidence ranges, exact prompts, and methodology, see `report.md`.*
