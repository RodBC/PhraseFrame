# AI UI COPY PACK — PhraseFrame (strings appendix)

> **⚠️ START HERE:** [`AI_AGENT_PACK.md`](AI_AGENT_PACK.md) Tasks N2–N10.  
> **This file:** drop-in strings mapped to `src/phraseframe/web/templates/index.html` (+ `app.js` guidance).  
> Validate numbers via `AI_CLAIM_MATRIX.md`. Prefer **Safer**; **Max** only in Science `<details>` with citations.

---

## Meta

| Element | Current | Replace with |
|---|---|---|
| `<title>` | PhraseFrame — Read with focus | PhraseFrame — Focus, check, remember |
| `meta description` | Phrase-paced reading with honest, comprehension-first controls. | Phrase-paced reading with recall checks, gap summaries, and spaced flashcards—built for understanding that lasts. |
| `footer` | PhraseFrame POC · comprehension before speed | PhraseFrame · focus → check → keep · comprehension before speed |

---

## Hero (`.hero`)

**Eyebrow**
```
FOCUS → CHECK → KEEP
```

**H1**
```
Read with focus. Check what stuck. Keep it.
```

**Lead (safer, recommended)**
```
One focal point. Meaning-sized phrases at your pace. Honest recall checks.
When a stretch slips, you get a short summary, a gap list, and flashcards on a schedule—
without pretending speed removes the work of understanding.
```

**Lead (max numeric, for A/B)**
```
Stay with the text, check from memory, and review on a schedule.
Lab studies of recall practice found 61% idea-unit memory a week later versus 40% after rereading—
and brief checks during learning cut mind-wandering probes roughly in half (~19% vs ~40%).
PhraseFrame turns that science into a reading loop you can actually finish.
```

**Optional CTA row (new markup if needed)**
- Primary: `Start a 5-minute loop`
- Secondary: `See the evidence`

---

## Demo guide (`#demo-guide`)

**Title**
```
Your first five-minute loop
```

**Body**
```
1) Prepare a short text · 2) Read to a checkpoint · 3) Answer from memory
4) Open gaps + cards · 5) Review once · 6) Return to the weak stretch
That’s the whole product—focus, proof, repair, keep.
```

**Dismiss**
```
Let’s go
```

---

## Attention Loop (`#attention-loop`)

Keep stage labels; add `title` tooltips:

| Stage | Tooltip |
|---|---|
| Read | One focal point; phrases come to you |
| Check | Answer from memory—retrieval builds retention |
| Gaps | Summary + what didn’t stick |
| Cards | Misses become practice |
| Review | Spaced schedule so memory survives the week |

**Session complete microcopy (new)**
```
Loop closed. Due cards will call you back.
```

---

## Library pulse (`#library-stats`)

| dt (label) | Helper / title attribute |
|---|---|
| Due reviews | Cards waiting—spaced practice beats cramming for the same study time |
| Avg. recall | Target ≥70% at your pace (Deep Pace idea) |
| Weak stops | Stops below 67%—jump back and repair |
| Last read | Continuity: tomorrow continues today |

**Due reviews as button text when count > 0**
```
Review {n} due
```

---

## Pace controls (`#wpm`, `#speed-guidance`, scale)

**Range scale (replace Reflective / Fast)**
```
~220 reflect · ~300 deep · ~350 stretch · 400+ skim risk
```

**Guidance by band (logic already in `app.js`—replace strings)**

| WPM | Guidance |
|---|---|
| ≤250 | Reflective pace. Close to careful study; strong for dense argument. |
| 251–320 | Deep-work band. Near typical adult nonfiction (~238 WPM average) up through brisk comprehension. |
| 321–350 | Stretch pace. Still in the band where RSVP studies often match page reading—watch your recall score. |
| 351–400 | Caution. Research often finds thinner comprehension as you enter the 350–400+ zone. Prefer first passes. |
| >400 | Skim risk. Studies commonly show clearer losses around 400–450 WPM. Slow down for anything you need to keep. |

**Checkbox label `#stop-checkpoints`**
```
Pause for recall checks (recommended)
```

**`#stop-every-words` label**
```
Check every
```

**Prepare button**
```
Prepare focus reader
```

---

## Reader stage

**Empty phrase**
```
Prepare the reader—then keep your eyes here
```

**New microcopy under `#phrase` (add `<p class="focus-hint">`)**
```
Eyes stay here. Phrases come to you.
```

**Check button title**
```
Pause for a recall check
```

---

## Checkpoint (`#checkpoint`)

**Title**
```
Recall check
```

**Intro**
```
Answer briefly from memory before continuing.
Checking is how memory is built—not only how it’s measured.
```

**`#checkpoint-recall-threshold`**
```
Below 67% we mark this stop as weak and prepare a repair path.
```

**Verdict lines (new, driven by score in `app.js`)**

| Condition | Text |
|---|---|
| ≥67% | Solid encoding. You can continue—or review cards to lock it further. |
| <67% | Weak stop. Here’s what the stretch said, what slipped, and cards to practice. |

**Summary section**

| Element | Text |
|---|---|
| `#checkpoint-summary-title` | What that stretch said |
| helper (optional) | Short extractive recap—not a substitute for reading |

**Gaps section**

| Element | Text |
|---|---|
| `#checkpoint-gaps-title` | What didn’t stick |
| footer (new) | Gaps are the shortest path to durable memory—not a report card. |

**Cards created (`#checkpoint-cards-created`)**
```
{n} review card(s) ready — first review can start now
```

**Primary actions (preferred order)**
1. `Review now`  
2. `Return to passage`  
3. `Continue reading`

---

## Review view (`#review-view`)

**Eyebrow**
```
SPACED REVIEW · HIGH-UTILITY PRACTICE
```

**Title** — keep `Review`

**Lead**
```
Due cards from every book in your library.
Practice testing and spaced practice are the two techniques
psychologists rate highest for durable learning—this screen is both.
```

**Signed-out status**
```
Sign in to load your review queue and protect what you checked.
```

**Empty queue**
```
Nothing due right now.
That’s the point of spacing—come back when a card is almost forgettable.
Meanwhile, a recall check while reading mints the next cards.
```

**Got it / Again sublabels (new small text)**
```
Got it · see later
Again · see sooner
```

**Return to passage button**
```
Return to passage
```

**Session end**
```
Session clear. Next review lands on the schedule—not on cramming night.
```

---

## Science section (`.science`) — full rewrite

**Eyebrow**
```
THE EVIDENCE, WITHOUT THE HYPE
```

**H2**
```
Understanding compounds when focus, checking, and spacing work together.
```

### Five pillars (replace 3-card grid)

| # | Title | Body |
|---|---|---|
| 01 | One focal point | Phrase-RSVP reduces scanning so attention stays on meaning—not on hunting the next line. |
| 02 | Pace you can explain | Deep work often lives near 250–350 WPM. Adults average ~238 WPM on nonfiction; we warn you as you stretch past ~350. |
| 03 | Active recall checks | Brief tests during learning cut mind-wandering probes roughly in half in landmark research (~19% vs ~40%). Checking builds memory. |
| 04 | Repair the gaps | When a stop is weak, you get a short passage recap and a gap list—so repair is specific, not a blind reread. |
| 05 | Keep with flashcards | Recall practice beat rereading at one week in classic studies (61% vs 40% idea units). Spaced review can add large gains vs cramming for the same study time. |

### `<details>` body (safer)

```
RSVP can calm the eyes and enforce a pace, but it does not delete the time language needs.
Regressions, pauses, and slower speeds remain tools—not failures.

What we lean on instead of speed myths:
• Practice testing and distributed practice — high utility (Dunlosky et al., 2013)
• Testing vs rereading — 61% vs 40% idea-unit recall at 1 week (Roediger & Karpicke, 2006)
• Interpolated tests — mind-wandering ~19% vs ~40% of probes (Szpunar et al., 2013)
• RSVP comprehension — often similar to page reading at 250–350 WPM; weaker at 400–450 (Ricciardi, 2018)

We do not promise 2–3× speed with full comprehension, silent “subvocalization hacks,”
or medical treatment of attention disorders.
```

### Citation links (add)

- Rayner et al. 2016 (keep)  
- Schotter et al. 2014 (keep)  
- Juola et al. 1995 (keep)  
- Roediger & Karpicke 2006 — `https://doi.org/10.1111/j.1467-9280.2006.01693.x`  
- Cepeda et al. 2008 — `https://doi.org/10.1111/j.1467-9280.2008.02209.x`  
- Szpunar et al. 2013 — `https://doi.org/10.1073/pnas.1221764110`  
- Dunlosky et al. 2013 — `https://doi.org/10.1177/1529100612453266`  
- Ricciardi 2018 — existing style DOI  
- Brysbaert 2019 — `https://doi.org/10.1016/j.jml.2019.104047`

---

## Default source textarea (seed text)

Replace with a shorter loop-teaching seed:

```
Attention is limited. A crowded page asks your eyes to choose; PhraseFrame offers one short idea at a time.

Read a few phrases. When a recall check appears, answer from memory—even if you feel unsure.
A weak stop is useful: you’ll see what the stretch said, what slipped, and cards to practice later.

The best pace is not the largest number. It is the fastest speed at which you can still explain what you read—
often near everyday nonfiction rates, with honesty when you stretch past about 350 words per minute.
```

---

## Understanding FAQ blurb (for future modal / README)

**Q: By how much will my understanding improve?**  
**A (canonical):**
```
It depends which part of the loop you use:

• Focus + sane pace: aim for comprehension parity with careful reading in the ~250–350 WPM band—
  not a magic multiplier.
• Recall checks: similar techniques cut mind-wandering during learning roughly in half in lab work
  (~19% vs ~40% of probes) and force encoding you can explain.
• Review vs reread: classic studies found 61% vs 40% idea-unit memory after a week
  when people practiced recall instead of rereading.
• Spaced cards: optimal spacing has produced up to ~64% more recall than cramming
  for the same study time in large experiments.

PhraseFrame wires these together. We will not invent a single “+X% understanding” number
for our users until we measure it in-product.
```

---

## A/B variants (hero only)

| Variant | H1 | Use when |
|---|---|---|
| A Trust | Read with focus. Prove you understood. | Default / skeptics |
| B Loop | Focus. Check. Keep. | Feature completeness |
| C Numeric | Remember more of what you finish. | Retention-led acquisition |

Do not A/B test Grade F claims.

---

*Implement with `UX_APPEAL_PLAN.md` Phase Now. Keep `web-reader` rule: warn, don’t celebrate, above 350 WPM.*
