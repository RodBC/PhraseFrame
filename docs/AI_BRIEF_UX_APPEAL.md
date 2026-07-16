# AI BRIEF — PhraseFrame evidence appendix

> **⚠️ START HERE instead:** [`AI_AGENT_PACK.md`](AI_AGENT_PACK.md) — controller with read order, decision tree, and Tasks N0–N11.  
> **This file is an appendix:** deep science + number bank for when a claim is challenged.  
> **Do not** begin implementation from this file alone.  
>  
> **Skeptic protocol:** (1) Measured in PhraseFrame? (2) RSVP vs lecture/memory transfer? (3) Relative vs absolute vs correlation? (4) Medical claim? If (1)=no → *mechanism-aligned literature*, never *our users gain X%*.  
> **Siblings:** `AI_CLAIM_MATRIX.md` · `AI_UI_COPY_PACK.md` · `UX_APPEAL_PLAN.md`

---

## 0. One-line product truth

PhraseFrame is a **focus + active-comprehension + spaced-review reading system** (phrase-RSVP core), **not** a speed-reading gimmick that promises 2–3× WPM with full understanding.

Positioning sentence (approved science direction):

> Keep your eyes on one focal point, move through meaning-sized phrases at a pace you control, check recall at stop points, and turn gaps into spaced flashcards—so attention stays on the text and what you understood can stick.

---

## 1. Roadmap status (is `nextsteps.md` “done”?)

### 1.1 Done locally (shippable demo loop)

| Layer | Status | Notes |
|---|---|---|
| v1 phrase-RSVP + TXT + MP4 + honest science UX | ✅ hosted demo | Core validated |
| v2 PDF + account + library + resume progress | ✅ local | Production E2E on Render Starter still pending |
| v3 stop points + 2–5 template questions + self-score + weak-passage flag + WPM suggest | ✅ local | Not LLM questions yet |
| v4 extractive summary + gap map + ≤4 flashcards + SM-2 + Review screen + Return to passage + Recall Moment | ✅ local | Generative summary / full longitudinal dashboard ❌ |
| Attention Loop + persistent Recall Moment | ✅ demo local | Score/summary/gaps stay until explicit action |
| Read → Check → Gaps → Cards → Review → Return | ✅ closed locally | Investor 5-min script in `nextsteps.md` |

### 1.2 Explicitly NOT done

1. Deploy v2–v4 E2E on Render Starter with persistent disk.  
2. Browser/mobile verification recorded; console-clean pass.  
3. LLM-generated questions / summaries / flashcards.  
4. Full longitudinal dashboard (beyond minimal pulse).  
5. PostgreSQL / S3-grade production storage (still SQLite + disk).  
6. Product-measured retention RCTs (no PhraseFrame clinical trial exists).

### 1.3 Implication for “enhance UX” planning

Do **not** invent a new v6 stack. Optimize and dramatize the **existing closed loop**, fix production readiness, and upgrade appeal/copy/numbers with honest science. Highest leverage: onboarding, calibration, Recall Moment clarity, Review habit loop, dashboard storytelling, and claim hygiene.

---

## 2. Feature inventory → user need → appeal → science grade

Legend for **Evidence grade**:

- **A** — Direct reading/RSVP evidence close to the feature.  
- **B** — Strong cognitive science (memory/attention) with clear transfer rationale.  
- **C** — Plausible mechanism; use soft language (“designed to…”, “studies of similar techniques…”).  
- **F** — Forbidden / contradicted by consensus; do not use.

| Feature (what exists) | User need | Compelling angle | Best numeric fuel | Grade | Caveat for skeptic AI |
|---|---|---|---|---|---|
| Fixed-focus phrase RSVP | Attention pulled by page clutter / phone / scanning | “One place to look; phrases come to you” | Eye-movement overhead often cited as ≤~10% of reading time (Rayner et al. framing)—so sell **focus**, not giant speed unlock | A/C | Do not claim RSVP alone doubles comprehension |
| Phrase/chunk size (not Spritz single-word) | Cognitive parsing load | “Meaning units, not random flashes” | Structured ~12-char / idea-unit segments beat random segments (Cocklin/Juola 1984/1995) | A | Optimal size is approximate; keep user control |
| WPM control + guidance ~350 | Fear of “too fast / too slow” | “Find the pace you can still explain” | Ricciardi 2018 (n≈209): RSVP ≈ page at **250–350 WPM**; worse at **400–450**; UI already warns above ~350 | A | 350 is guidance, not biology |
| Pause / back / restart | Regressions needed for hard text | “Real reading allows a second look” | Schotter et al. 2014: regressions support comprehension | A | RSVP must not trap users forward-only |
| Stop every N words + manual Check | Mind wandering while “reading” | “Prove you still got it before you go on” | Szpunar et al. 2013: interpolated tests → mind-wandering probes **~19%** vs **~39–41%** restudy/none (**≈ half**) | B | Lecture study, not RSVP; mechanism transfer is justified for checkpoints |
| Self-score Sure/Unsure/No idea | Metacognition | “Catch the illusion of knowing” | Roediger & Karpicke: restudy inflates confidence while delayed recall lags | B | Self-score ≠ verified accuracy |
| Honest 67% recall threshold in Recall Moment | Trust | “We don’t call partial recall mastery” | Product UX honesty (PRODUCT) | A (product) | Keep threshold visible in copy |
| Extractive summary of weak passage | Repair understanding | “Here’s what that stretch said—in 3–5 lines” | Supports re-encoding after failed retrieval; not a magic summary RCT | C | Do not call it “AI understanding” while extractive |
| Gap map | Know what failed | “See exactly what didn’t stick” | Diagnostic + germane load redirection | C | Template/heuristic today |
| Flashcards from weak stops (≤4) | Convert failure → practice | “Misses become review, not shame” | Testing effect + generation from failure | B | Quality of cards matters |
| Immediate first review | Close the loop same session | “Don’t wait to forget—lock it now” | Immediate retrieval after encoding strengthens retention path | B | Immediate ≠ spaced; both needed |
| SM-2 spaced schedule | Long-term retention | “Review right before you’d forget” | Cepeda et al. 2008: optimal spacing vs massed → up to **~64%** more recall / large *d*; gaps of **10–111%** relative lift depending on horizon | B | SM-2 is solid; FSRS is newer efficiency play (future) |
| Cross-doc Review screen | Habit / due work | “One inbox for what your books still owe you” | Habit + spacing adherence | C | Retention only if user returns |
| Return to passage (card → frame) | Re-anchor in context | “Jump back to the exact phrase that failed” | Context reinstatement aids memory | C | Strong UX differentiator vs naked Anki |
| Library pulse (pending reviews, avg recall, weak stops, last read) | Progress visibility | “See comprehension, not vanity WPM” | Aligns product metrics with science | A (product) | Don’t fake longitudinal graphs |
| Resume chapter/frame/WPM/phrase size | Continuity | “Tomorrow continues today” | Habit formation / completion | C | Core retention of *users*, not of text |
| MP4 export | Share / offline | Secondary | Niche | C | Not primary retention story |

---

## 3. Number bank (use these; do not invent new %)

### 3.1 Rules for using numbers in UX/copy

1. Prefer **relative literature lifts** with attribution: “In lab studies of [X]…”.  
2. Never say “PhraseFrame users improve understanding by 52%” unless PRODUCT-MEASURED.  
3. Prefer ranges + conditions (“at 1 week”, “vs rereading”, “when tests interrupt study”).  
4. Pair every speed number with a comprehension caveat.  
5. Prefer **composite outcome**: sustained WPM **with** recall ≥ product threshold (already product metric idea: WPM with >70% comprehension).

### 3.2 Headline numbers (sorted by marketing usefulness)

#### Retention / active review (strongest stack)

| Claim-ready number | Precise finding | Source | Safe copy shape |
|---|---|---|---|
| **+52% relative** delayed recall (61% vs 40%) | Repeated testing vs repeated studying of prose; 1-week free recall | Roediger & Karpicke (2006) Exp. 2 | “Practice recalling—not just rereading—can raise what you still remember a week later by about half in classic lab studies.” |
| **61% vs 40%** absolute | Same | Same | Use absolute when space allows; clearer than relative |
| Restudy wins at **5 min**, testing wins at **1 week** | Cross-over interaction | Same | Sell long-term memory, not “feels fluent now” |
| Learners often **mispredict**: restudy feels better | Metacognitive illusion | Same | Support self-score + delayed review UX |
| Optimal spacing vs cramming: **~64%** more recall (*d*≈1.1); recognition **~26%** | Fixed study time, best gap vs 0-day gap | Cepeda et al. (2008) | “Spacing reviews can beat cramming by large margins for the same study time.” |
| Horizon-specific lifts vs massed: **+10% / +59% / +111% / +77%** recall at RI 7/35/70/350 days | Same study | Cepeda et al. (2008) | Use one horizon at a time; don’t stack all four |
| Optimal gap ≈ **10–20%** of desired retention horizon (rough rule) | Same literature | Cepeda reviews | Educate why SM-2 stretches intervals |
| SM-2 targets habitual **~90%** retrievability class of systems | Spaced-repetition practice | SuperMemo/Anki tradition | “Aim to remember most cards when they come due”—not 100% forever |
| Practice testing + distributed practice = **high utility** (only two techniques at top tier) | 10-technique review | Dunlosky et al. 2013 PSPI | “Built around the two techniques psychologists rate highest.” |
| Spacing meta often summarized **47% vs 37%** recall (distributed vs massed) | 254 studies / 14k+ participants (as cited in SciAm summary of Dunlosky review) | Cepeda meta via Dunlosky communication | Use as secondary to Cepeda 2008’s ~64% optimal-gap figure |
| Self-explanation meta **g ≈ 0.55** | 64 studies / ~5917 learners | Bisra et al. 2018 | Support “explain what you read” / checkpoint answering |
| High vs low explainers **15.3 vs 2.8** elaborations per example; posttest **82% vs 46%** in classic contrast | Physics examples | Chi et al. 1989 | Illustrative, small-n classic—use in details, not hero |

#### Focus / mind wandering / checkpoints

| Claim-ready number | Precise finding | Source | Safe copy shape |
|---|---|---|---|
| Mind wandering ↔ comprehension **r ≈ −0.21** (−0.23 with probes) | Meta-analysis, 25 papers / 73 coeffs | Bonifacci et al. / Psychon Bull Rev 2022 | “More mind-wandering tracks with weaker comprehension—about a medium individual-difference effect.” |
| Effect size noted as ~**1/3 of remedial reading intervention** magnitude; ~**2/3 of a year** of primary RC growth (interpretive) | Same meta discussion | Same | Use carefully; interpretive, not PhraseFrame result |
| Interpolated tests: MW **19%** of probes vs **39–41%** | Online lecture + quizzes | Szpunar, Khan & Schacter (2013) PNAS | “Brief checks during learning cut reported mind-wandering roughly in half in a landmark lecture study.” |
| Note-taking on more slides: **17% vs 6%** | Same | Same | Optional secondary |
| Multitasking while reading: comprehension *g* ≈ **−0.28** overall; **−0.54** when pace fixed/time-limited; reading time *g* ≈ **+0.52** when self-paced | Meta-analysis | Clinton-Lisell (2021) | “Split attention makes reading slower or shallower—especially under time pressure.” |

#### Pace / RSVP / speed (honest, still compelling)

| Claim-ready number | Precise finding | Source | Safe copy shape |
|---|---|---|---|
| Adult silent reading ≈ **238 WPM** nonfiction / **260** fiction | Meta-analysis 190 studies | Brysbaert (2019) | Baseline for “normal pace” |
| Typical skilled range often cited **200–400 WPM** | Rayner et al. (2016) | Same | Don’t pretend 300 is elite |
| RSVP ≈ traditional at **250–350 WPM**; worse at **400–450** | n≈209 | Ricciardi / Di Nocera 2018 | Aligns with product 350 guidance |
| Modern RSVP apps often **fail to foster comprehension** at marketed speeds | Experimental | Acklin & Papesh (2017) | Competitive contrast: we refuse the lie |
| No reliable **2–3×** speed with full comprehension | Consensus review | Rayner et al. (2016) PSPI | Anti-claim; trust builder |
| Structured idea-unit RSVP segments > random equal-length segments | Comprehension advantage | Cocklin et al. 1984; Juola et al. 1995 | Differentiator vs word-flash apps |
| Subvocalization suppression **hurts** complex comprehension | Articulatory suppression literature + Rayner review | Multiple | **F** to claim “we kill inner speech so you understand more” |

### 3.3 What to tell users about “how much will my understanding improve?”

**Honest composite answer for planning AI (do not collapse into one fake %):**

1. **RSVP focus alone:** Expect **parity**, not magic—comprehension similar to page reading in the **250–350 WPM** band; risk of drop above **~400 WPM**. Selling point = **attention integrity + completion**, not +N% IQ.  
2. **Checkpoints / interpolated retrieval:** Literature-aligned expectation: large reduction in off-task thought during learning sessions (**~half** MW probes in Szpunar lecture paradigm) + better later memory when users actually retrieve. Phrase as **up to ~2× more on-task attention moments** in analogous settings—not as PhraseFrame RCT.  
3. **Testing vs rereading (1 week):** Classic prose result **61% vs 40%** idea-unit recall → about **+21 percentage points** absolute / **~+50% relative**. Best headline for Review/Check.  
4. **Spacing vs cramming (same study time):** Up to **~64% more recall** at optimal gap (Cepeda). Best headline for SM-2 flashcards.  
5. **Product target metric (recommended):** “Sustain **≥70% checkpoint recall** at your chosen WPM.” That is measurable in-app and science-aligned; better than promising a universal understanding boost.

**Recommended hero number stack for marketing (layered, not summed):**

```
Layer A — Focus: "Stay with the text" → cite MW r=-0.21 + interpolated-test 19% vs 40%
Layer B — Understand now: "Check before you continue" → checkpoints + 67% honesty threshold
Layer C — Remember later: "61% vs 40% at 1 week (testing vs rereading)" 
Layer D — Keep it: "Spacing can add ~64% recall vs cramming for the same study time"
Layer E — Pace: "Match ~238–350 WPM deep-work band; we warn you past ~350–400"
```

**Never add Layers A–D into “users gain 200% understanding.”** That is fraudulent stacking.

---

## 4. Feature-by-feature appeal copy blocks (ready to adapt)

### 4.1 Fixed focus + phrase pacing

- **Hook:** One focal point. Meaning-sized phrases. Your pace.  
- **Proof:** Structured RSVP segments outperform random cuts; regressions and speed control remain available because comprehension needs them.  
- **Number:** Calibrate near **250–350 WPM** for deep work; product warns near/above **350–400**.  
- **Anti-claim:** Not 500–1000 WPM with perfect memory.

### 4.2 Active checkpoints (Attention Loop / Check)

- **Hook:** Don’t finish a chapter you never encoded.  
- **Proof:** Interpolated testing cuts mind-wandering roughly in half in controlled lecture research (19% vs ~40%).  
- **UX emotion:** Mild productive friction > passive scroll trance.  
- **Number to surface in UI:** Last stop score; streak of stops ≥67%; suggested WPM delta.

### 4.3 Recall Moment (score + summary + gaps + cards)

- **Hook:** A single screen that answers: *Did I get it? What did it say? What’s missing? What do I practice?*  
- **Proof:** Retrieval practice + diagnostic feedback + re-study of failed material.  
- **Trust number:** **67%** threshold—honesty as brand.  
- **Anti-claim:** Templates ≠ AI tutor (until LLM ships). Say “guided recall,” not “AI grades your mind.”

### 4.4 Gap summarization (not-understood passages)

- **Hook:** Failure becomes a map, not a fog.  
- **Proof:** Re-exposure after failed retrieval is high-value study time (vs blind reread of whole chapter).  
- **Appeal:** “3–5 lines on the stretch that slipped” + jump back to frame.  
- **Upgrade path:** LLM summaries later; keep extractive honest until then.

### 4.5 Flashcards + SM-2 Review

- **Hook:** The book keeps a debt with you—and a schedule to pay it.  
- **Proof:** 61% vs 40% (test vs restudy, 1 week); spacing lifts up to ~64% vs massed.  
- **UX differentiator:** Cards born from *your* weak stops + **Return to passage**.  
- **Habit loop:** Due today → Got it / Again → next interval.

### 4.6 Pace keeping (intelligent pacing story)

- Sell **control**, not velocity: punctuation pauses, phrase size, stop every N words, WPM suggestion after weak scores.  
- Metric story: “Best pace = highest WPM you can hold with ≥70% recall,” not max slider.

### 4.7 Library / continuity

- Resume exact frame; show pending reviews + avg recall + weak stops.  
- Emotional promise: *You will finish books you start—and remember why they mattered.*

---

## 5. Competitive framing (use for appeal, not trash-talk)

| Competitor pattern | Their claim | Our counter |
|---|---|---|
| Spritz-style word flash | Eliminate eye movements → read 2–3× | Eye movements aren’t the main bottleneck; regressions matter; we keep phrases + controls |
| Classic speed courses | Kill subvocalization | Inner speech supports complex comprehension; we don’t sell mute reading |
| Generic PDF reader | Infinite scroll | Scroll enables multitasking; we enforce single-stream attention + checks |
| Standalone Anki | Manual card creation | We auto-mint cards from comprehension failures + deep-link to source frame |
| Highlight-only apps | Passive marks | Marks ≠ retrieval; we force recall |

---

## 6. Forbidden claim list (hard fails)

1. “Double/triple reading speed with full comprehension.”  
2. “Eliminate subvocalization to unlock understanding.”  
3. “Treats ADHD / cures attention disorders.”  
4. “RSVP alone improves retention by X%.”  
5. “Our users gain X% understanding” without PRODUCT-MEASURED data.  
6. “AI understands your book” while questions/summaries are template/extractive.  
7. Stacking independent study percentages into one mega-lift.  
8. Medical/clinical language.

---

## 7. Gaps to improve (fuel for the next UX plan)

Prioritize enhancements that make the **existing science story felt in the UI**, not greenfield features.

### 7.1 Experience gaps (likely high ROI)

1. **First-run value demo in <60s:** Show focus → check → card without long PDF. (`/?demo=1` exists—tighten emotional climax.)  
2. **Calibration ritual:** 60–90s at 250 / 300 / 350 with mini-check; recommend personal “deep pace.”  
3. **Recall Moment hierarchy:** Score → one-sentence verdict → summary → gaps → CTA Review / Continue (reduce cognitive pile-up).  
4. **Due Review as habit surface:** Badge, empty states, “2 minutes to protect yesterday’s chapter.”  
5. **Weak-stop storytelling:** Map of chapter with red pins; one-click Return.  
6. **Pace × comprehension chart (even sparkline):** WPM vs recall—product’s unique scientific dashboard.  
7. **Copy audit:** Replace residual “speed” vibes with “focus / recall / keep.”  
8. **Mobile layout polish** (pending verification in nextsteps).  
9. **Production E2E** so appeal isn’t undermined by data loss.  
10. **LLM upgrade later** for question quality—only after trust copy is solid.

### 7.2 Measurement gaps (so future claims can become PRODUCT-MEASURED)

Instrument (plan for):

- Checkpoint recall rate by WPM band.  
- % sessions with ≥1 Review after weak stop.  
- D+1 / D+7 resume rates.  
- Card retention proxy (SM-2 ease / again rate).  
- Time-to-first-value (seconds to first Check).  

Until then, all % in marketing stay literature-tagged.

---

## 8. Instructions to the planning AI (downstream prompt contract)

When asked to “make a plan to enhance UX / appeal,” you MUST:

1. **Doubt** every number; re-check grade A/B/C/F before putting it in UI copy.  
2. Assume **v2–v4 loop exists**; plan polish, narrative, habit, and production readiness before new verticals.  
3. Make appeal **multi-feature** (focus + pace + check + gaps + cards + review), not WPM-only.  
4. Propose **concrete UX changes** (screens, copy, empty states, metrics) tied to sections 2–4.  
5. Include a **claim matrix** in the plan: Claim → UI surface → Evidence grade → Exact citation → Allowed wording.  
6. Propose **one hero metric** users see: e.g. “Deep pace = max WPM with ≥70% recall (7-day rolling).”  
7. Offer **A/B copy variants** that differ in aggressiveness but never violate section 6.  
8. Separate **must-ship** (demo honesty, Review habit, calibration) from **nice** (LLM, FSRS, social).  
9. Keep Portuguese or English consistent with existing docs/UI unless user specifies.  
10. Output a phased plan (Now / Next / Later) with success metrics from `nextsteps.md` § Metrics.

---

## 9. Citation shortlist (canonical)

1. Rayner, Schotter, Masson, Potter & Treiman (2016). *Psych Science in the Public Interest* — speed-reading consensus.  
2. Schotter, Tran & Rayner (2014). *Psych Science* — regressions aid comprehension.  
3. Cocklin, Ward, Chen & Juola (1984); Juola et al. (1995). *Memory & Cognition* — structured RSVP segments.  
4. Ricciardi & Di Nocera (2018). *IJHFE* — RSVP speed vs inferential comprehension (~250–350 OK; 400–450 worse).  
5. Acklin & Papesh (2017). *Am J Psychol* — modern speed apps ≠ comprehension.  
6. Roediger & Karpicke (2006). *Psych Science* — testing effect 61% vs 40% at 1 week.  
7. Cepeda et al. (2008). *Psych Science* — spacing ridgeline; ~64% recall lift optimal vs massed.  
8. Szpunar, Khan & Schacter (2013). *PNAS* — interpolated tests; MW 19% vs ~40%.  
9. Bonifacci et al. (2022/2023). *Psychon Bull Rev* — MW–RC meta *r*≈−0.21.  
10. Clinton-Lisell (2021). *J Res Reading* — multitasking meta *g*≈−0.28 / −0.54.  
11. Brysbaert (2019). Meta-analysis — ~238 WPM nonfiction silent reading.  
12. Product: `docs/SCIENCE.md`, `docs/nextsteps.md`, UI guidance at ~350 WPM, Recall threshold 67%.

---

## 10. Condensed “truth pack” for a skeptical AI

```
PRODUCT: PhraseFrame = phrase-RSVP focus reader + checkpoints + gap summary + SM-2 cards + return-to-source
DONE: local closed loop Read→Check→Gaps→Cards→Review→Return; production E2E + LLM still open
SELL: attention integrity + verified recall + spaced retention
DO NOT SELL: 2× speed, kill subvocalization, medical focus cures
BEST NUMBERS:
  - Testing vs rereading @1wk: 61% vs 40% (~+50% relative)
  - Spacing vs massed: up to ~64% more recall (same study time)
  - Interpolated tests: MW ~19% vs ~40%
  - MW–comprehension: r≈−0.21
  - Multitasking: g≈−0.28 (worse under time pressure)
  - Deep RSVP band: ~250–350 WPM; warn ≥350–400
  - Adult baseline: ~238 WPM nonfiction
PRODUCT TARGET TO BUILD TOWARD: max WPM with ≥70% checkpoint recall (user-visible)
COPY TONE: honest, numeric, multi-feature, anti-gimmick
NEXT PLAN SHOULD: polish UX of existing loop + claim matrix + habit/Review + calibration + deploy
```

---

*End of brief. Consumer AI: doubt freely, but do not discard the grade-A/B citations without replacement evidence.*
