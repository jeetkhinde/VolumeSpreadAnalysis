# A Custom GPT that teaches VSA

Everything needed to build a GPT that teaches *Master the Markets* in plain English
and draws charts when they help.

```bash
python3 gpt/build_knowledge.py    # regenerate the knowledge pack from the site data
```

## Setup, in order

**1. Create the GPT** — chatgpt.com → Explore GPTs → Create.

**2. Name and description**

> **Name:** Volume Spread Analysis Tutor
> **Description:** Learn to read volume and price spread the way Tom Williams taught
> it, in plain English, with charts drawn as you go.

**3. Instructions** — paste `INSTRUCTIONS.md` verbatim. It is 6,321 characters; the
field allows 8,000, so there is room to add your own preferences at the end.

**4. Capabilities** — this part matters:

| Capability | Setting | Why |
|---|---|---|
| **Code Interpreter & Data Analysis** | **ON** | This is how it draws charts. Without it there are no graphics. |
| Image generation (DALL·E) | **OFF** | It cannot draw a price bar correctly. It will produce a convincing picture that teaches the wrong thing. |
| Web browsing | Optional | Only useful if you want current market examples. |

Turning DALL·E **off** is deliberate. An image model asked for "a narrow spread
up-bar closing near its high on low volume" will return something that looks like a
chart but has the close in the wrong place. Matplotlib puts it exactly where the
data says. Wrong charts are worse than no charts when you are learning to read
them.

**5. Knowledge** — upload all seven files from `gpt/knowledge/`:

| File | Contents |
|---|---|
| `01-foundations.md` | Preamble, Introduction, Market Basics (chapters 1–27) |
| `02-trends.md` | Trends & Volume Spread Analysis (28–39) |
| `03-signals-in-context.md` | Anatomy of Bull & Bear Markets (40–56) |
| `04-trading-practice.md` | Becoming a Trader or Investor, appendix (57–68) |
| `05-glossary.md` | All 61 glossary entries |
| `06-signal-spec.md` | Precise reference for every named signal |
| `vsa_charts.py` | The chart helper Code Interpreter imports |

Each chapter carries its plain-English summary and takeaways first, then Williams'
own words, then the printed page range so the GPT can cite where a rule comes from.

**6. Conversation starters**

- Teach me VSA from the beginning, one idea at a time
- Show me the difference between a test and a failed test
- I saw a wide down-bar on huge volume that closed near its high — what is that?
- Which parts of this method can I actually code, and which need judgement?

## The two things that make it work

**`06-signal-spec.md` is the important file.** It states each signal as *bar shape +
volume + close position + required background*, and — more usefully — it marks
where Williams is vague. He says "after a rally" and "ultra-high volume" without
ever defining them. The instructions tell the GPT to admit that instead of
inventing a number and attributing it to him. That single rule is what keeps the
tutor honest.

**Charts come from matplotlib, not from an image model.** `vsa_charts.py` draws a
vertical price bar with a close tick and a volume histogram underneath, in the same
visual language as the reader site. `vsa_panels()` puts two to four side by side on
one shared scale, which is the most useful teaching picture in VSA — same bar, same
volume, only the close differs.

## Testing it

Ask these and check the answers:

1. *"What is a test?"* — should give the bar shape **and** say it only counts with a
   selling climax behind it or an existing uptrend. If it omits the background, the
   instructions are not being followed.
2. *"How high is 'ultra-high volume'?"* — should say the book never defines it, then
   offer a convention labelled as not Williams'.
3. *"Show me an up-thrust."* — should produce a matplotlib chart, not a DALL·E image.
4. *"Is this a buy signal?"* with one bar — should refuse to name a signal without
   background and explain why.

## Note on the source

The book is © 1993–2009 Tom Williams / TradeGuider Systems and carries an
all-rights-reserved notice. A **private** GPT that only you use is a personal
reading aid. **Publishing it** — link-sharing or the GPT Store — distributes the
full text to others, which is a different thing entirely. Keep it private unless
you have cleared that with TradeGuider.
