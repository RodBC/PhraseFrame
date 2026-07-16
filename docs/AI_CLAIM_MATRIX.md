# AI CLAIM MATRIX — PhraseFrame (policy appendix)

> **⚠️ START HERE:** [`AI_AGENT_PACK.md`](AI_AGENT_PACK.md) §0.2 (decision tree) + §5 (copy selection).  
> **This file:** lookup table when adding/editing user-visible claims. Doubt every row. Prefer A/B. Never ship F. Never upgrade C to “proven in PhraseFrame.”  
> **Columns:** Claim ID · Surface · Max · Safer · Number · Source · Grade · Risk · Forbidden twin  
> **Grades:** A = RSVP/reading-close · B = cog-sci transfer · C = soft only · F = ban · P = product rule (67%/70%), not a lab %

---

## Focus / RSVP

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| F1 | Hero, science pillar 01, `#reader-stage` microcopy | “One focal point cuts the chaos of a crowded page.” | “Phrases arrive at one place—so your eyes stop hunting.” | — (mechanism) | Potter/Juola RSVP tradition; Rayner 2016 context | A/C | Overclaiming attention treatment | “Cures ADHD” |
| F2 | Science details | “Structured idea units beat random RSVP cuts.” | “Classic RSVP work found structured short segments more readable than arbitrary ones.” | ~12-char / idea-unit advantage | Cocklin et al. 1984; Juola et al. 1995 | A | Segment size is approximate | “Any chunking = better comprehension” |
| F3 | Science details | “Eye movements aren’t the main bottleneck—so we don’t sell 3× speed.” | “Freeing eye movements helps focus; language processing still takes time.” | Eye movements often framed as small share of time | Rayner et al. 2016 | A | — | “Eliminate saccades → 1000 WPM” |

## Pace keeping

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| P1 | `#speed-guidance`, science pillar 02 | “Deep work lives near **250–350 WPM**.” | “In one large RSVP study, comprehension held with traditional reading at 250–350 WPM and fell at 400–450.” | 250–350 OK; 400–450 worse | Ricciardi & Di Nocera 2018 (n≈209) | A | Not a hard biological cliff | “350 WPM is everyone’s optimum” |
| P2 | Pace scale labels | “Adults average **~238 WPM** on nonfiction.” | “Meta-analysis puts silent nonfiction near 238 WPM—so 300 is already brisk.” | 238 / 260 fiction | Brysbaert 2019 | A | Task/definition variance | “You’re slow if under 300” |
| P3 | `#speed-guidance` >350 | “Above ~350, meaning often thins.” | “At this pace, studies often find lower comprehension. Use for a first pass, not deep study.” | ~350 guidance (product) | Product + Ricciardi | A/P | — | Celebrate 500 |
| P4 | Deep Pace badge (future) | “Your Deep Pace: **N WPM** at ≥70% recall.” | Same | ≥70% threshold | Product metric | P | Needs instrumentation | Claim lab-proven Deep Pace |

## Active check / Attention Loop

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| C1 | `#checkpoint` intro, science pillar 03 | “Checks can cut mind-wandering roughly in **half**.” | “In a landmark lecture study, brief tests dropped mind-wandering probes to **~19%** vs **~40%** without them.” | 19% vs 39–41% | Szpunar, Khan & Schacter 2013 PNAS | B | Lecture ≠ RSVP reading | “PhraseFrame halves your MW” |
| C2 | Science details | “Mind-wandering tracks with weaker comprehension.” | “A meta-analysis finds MW and reading comprehension correlate about **r = −0.21**.” | r≈−0.21 | Bonifacci et al. 2022/23 | B | Correlation ≠ causation | “We eliminate mind-wandering” |
| C3 | Multitasking aside (optional) | “Split attention makes reading less efficient.” | “Meta-analysis: multitasking while reading hurts comprehension (*g*≈−0.28), worse under time pressure (*g*≈−0.54).” | −0.28 / −0.54 | Clinton-Lisell 2021 | B | — | “App blocks all distraction” |
| C4 | Checkpoint CTA | “Answer from memory—checking builds memory.” | “Retrieval practice is learning, not just assessment.” | — | Roediger & Karpicke; Dunlosky high utility | B | — | Instant mastery guarantee |
| C5 | `#checkpoint-recall-threshold` | “Below **67%**, we mark the stop weak.” | Same | 67% | Product | P | Arbitrary but honest | Pretend 67% is clinical cut-score |
| C6 | Reflection / explain prompt | “Explaining what you read strengthens understanding.” | “Self-explanation shows a medium learning benefit (meta **g≈0.55**); strong explainers generate far more elaborations (**~15 vs ~3** per example in classic work).” | g≈0.55; 15.3 vs 2.8 | Bisra et al. 2018; Chi et al. 1989 | B | Physics/examples origin | “Typing one sentence = g=0.55 for you” |

## Gaps + summarization of not-understood

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| G1 | `#checkpoint-summary-title` | “Here’s what that stretch said.” | “A short extractive recap of the passage you just checked.” | 3–5 sentences (product) | Product extractive | P/C | Not generative AI | “AI understood the book” |
| G2 | `#checkpoint-gaps-title` | “See exactly what didn’t stick.” | “Gaps turn fog into a short repair list.” | — | Impasse / errorful generation framing | C | Heuristic gaps | “We diagnosed your cognition” |
| G3 | Gap footer | “A miss + feedback can beat passive rereading.” | “Generating an answer—even wrong—then seeing feedback can strengthen correct encoding (errorful generation research).” | — | Potts & Shanks 2014; Bjork desirable difficulties | B/C | Conditions matter | “Wrong answers are always better” |
| G4 | Dunlosky contrast | “Highlighting & rereading are low-utility; we push testing instead.” | “A major review rated rereading and highlighting **low utility**, while practice testing and distributed practice are **high utility**.” | High vs low utility ratings | Dunlosky et al. 2013 PSPI | B | Summarization alone also often low/moderate—our summary is *after* failed retrieval, not instead of testing | “Summaries alone make you expert” |

## Flashcards + spaced Review

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| R1 | Review eyebrow, science pillar 05 | “Practice testing is a **high-utility** learning technique.” | “Dunlosky et al. (2013) gave practice testing their top utility rating across ages and materials.” | High utility | Dunlosky et al. 2013 | B | — | “Flashcards = automatic A+” |
| R2 | Science / Review empty state | “Recall practice beat rereading a week later: **61% vs 40%**.” | “In classic prose experiments, repeated testing yielded **61%** idea-unit recall at 1 week vs **40%** after repeated study.” | 61% vs 40% (~+52% relative) | Roediger & Karpicke 2006 Exp. 2 | B | Free recall ≠ our self-score cards | “You’ll hit 61% in PhraseFrame” |
| R3 | Review onboarding | “Spacing can beat cramming for the same study time.” | “Optimal spaced review produced up to **~64%** more recall than massed review in a large spacing study.” | ~64%; also 47% vs 37% in spacing meta often cited | Cepeda et al. 2008; Dunlosky/SciAm summary of spacing meta | B | Horizon-dependent | Stack with R2 into “126% better” |
| R4 | Got it / Again sublabels | “We’ll show this later / sooner.” | “Spaced repetition schedules the next look near when you’d forget.” | ~90% target class (SRS culture) | SM-2 tradition | C/P | SM-2 ≠ measured 90% in-app | “Never forget anything” |
| R5 | Return to passage | “Jump to the exact phrase that failed.” | “Revisit the source frame—context helps repair.” | — | Context reinstatement (general) | C | — | — |
| R6 | Immediate first review | “Lock it before you leave the chapter.” | “First review happens now; later reviews follow the schedule.” | — | Retrieval + spacing combo | B | — | Immediate review alone = long-term fix |

## Composite / brand

| ID | Surface | Max wording | Safer wording | Number | Source | Grade | Risk | Forbidden twin |
|---|---|---|---|---|---|---|---|---|
| B1 | Hero | “Read → check → repair → remember.” | “A reading-to-recall loop—not a speed gimmick.” | — | Product | P | — | “2× faster understanding” |
| B2 | Understanding FAQ | “Understanding gains depend on the loop you run.” | Use layered A–E answer from `UX_APPEAL_PLAN.md` §2 | Multiple | Multiple | — | Stacking | Single mega-% |
| B3 | Footer / meta description | “Comprehension before speed.” | Same | — | Product | P | — | Speed-first SEO bait |

---

## Quick reject list (Grade F)

1. Double/triple speed with full comprehension.  
2. Eliminate subvocalization to unlock understanding.  
3. Treats ADHD / clinical attention claims.  
4. “PhraseFrame users improve understanding by X%” without PRODUCT-MEASURED data.  
5. “AI grades/understands your PDF” while templates/extractive are live.  
6. Additive stacking of independent study % into one user promise.

---

## Citation keys (short)

- RAYNER2016, SCHOTTER2014, JUOLA1995, COCKLIN1984  
- RICCIARDI2018, ACKLIN2017, BRYSBAERT2019  
- ROEDIGER2006, CEPEDA2008, DUNLOSKY2013  
- SZPUNAR2013, BONIFACCI2022, CLINTON2021  
- CHI1989, BISRA2018, POTTS2014  

Full DOIs live in `docs/SCIENCE.md` and `docs/AI_BRIEF_UX_APPEAL.md`.
