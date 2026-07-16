# PhraseFrame — UX & Appeal Enhancement Plan (backlog appendix)

> **⚠️ START HERE:** [`AI_AGENT_PACK.md`](AI_AGENT_PACK.md) — executable Tasks N0–N11 + Definition of Done.  
> **This file:** expanded Now/Next/Later backlog and rationale. Prefer the Agent Pack for implementation order.  
> **Goal:** Polish the existing Read→Check→Gaps→Cards→Review loop; do not invent a new product.

---

## 0. Verdict: is `nextsteps.md` done?

| Layer | Status | Plan implication |
|---|---|---|
| v1–v3 local | ✅ Done | Do not rebuild; polish |
| v4 loop local (Recall Moment, extractive summary, ≤4 cards, SM-2, Review, Return) | ✅ Done | **Primary UX surface for appeal** |
| LLM questions/summaries, full longitudinal dashboard | ❌ Open | Phase Later |
| Production E2E (Render Starter + disk) | ❌ Open | Phase Now (trust breaker if skipped) |
| PhraseFrame-measured % lifts | ❌ None | All % in UI = **literature-tagged** until instrumented |

**Answer:** Feature roadmap for the core learning loop is **functionally done locally**. What is *not* done is **experience dramatization, habit UX, claim/science surfacing, mobile polish, and production continuity**. That is this plan’s scope.

---

## 1. Narrative the whole product must tell

**Category:** Focus + verified understanding + spaced keep.  
**Not:** Speed-reading app.

**User journey story (one sentence per stage):**

1. **Read** — One focal point; meaning-sized phrases; your pace.  
2. **Check** — Prove you encoded it before going on.  
3. **Gaps** — See what slipped (summary + gap list).  
4. **Cards** — Misses become practice, not shame.  
5. **Review** — Return on a schedule so memory survives the week.  
6. **Return** — Jump back to the exact frame that failed.

**Hero outcome (user-visible, product-measurable):**  
> **Deep Pace** = highest WPM you can sustain with **≥70% checkpoint recall** (rolling).

Until Deep Pace is coded, show the components separately (WPM + avg recall) and teach the idea in copy.

---

## 2. How much can understanding improve? (honest numeric stack)

**Rule:** Never say “PhraseFrame users gain X%.” Say “Lab studies of [technique] found…”

### 2.1 Layered answer (use in Science section + onboarding)

| Layer | What user feels | Best literature number | Feature that delivers it | Evidence grade |
|---|---|---|---|---|
| A Focus | “I’m actually here” | Mind-wandering during interpolated tests **~19%** vs **~39–41%** (≈ half) — Szpunar et al. 2013 | Checkpoints / Attention Loop | B (lecture→reading transfer) |
| B Encode | “I can explain it” | Self-explanation meta **g ≈ 0.55**; high vs low explainers **15.3 vs 2.8** explanations — Chi / Bisra | Checkpoint answers + “explain” reflection | B |
| C Remember (1 week) | “It stuck” | Testing vs rereading **61% vs 40%** idea units @ 1 week (~**+52% relative**) — Roediger & Karpicke 2006 | Check + Review | B |
| D Keep (spacing) | “I still have it later” | Optimal spacing vs massed: up to **~64%** more recall; distributed practice meta often cited **47% vs 37%** — Cepeda 2008 / Dunlosky review of spacing meta | SM-2 Review | B |
| E Pace | “I’m not lying to myself with WPM” | RSVP ≈ page at **250–350 WPM**; worse at **400–450** — Ricciardi 2018; adult baseline **~238 WPM** nonfiction — Brysbaert 2019 | Pace slider + guidance | A |

### 2.2 Single “understanding” headline (approved)

**Primary (absolute, clearest):**  
> “In classic studies, practicing recall after reading left people with **61%** of idea units a week later vs **40%** after rereading—the same time spent differently.”

**Secondary (focus):**  
> “Brief checks during learning cut reported mind-wandering roughly in half (**~19%** vs **~40%** of probes) in a landmark study.”

**Tertiary (authority):**  
> “Psychologists rate **practice testing** and **distributed practice** as the only two learning techniques with **high utility** across ages and materials (Dunlosky et al., 2013)—and PhraseFrame is built around both.”

### 2.3 Forbidden stacking

Do **not** add 52% + 64% + “2× focus” into “you’ll understand 3× better.” Present layers separately; let users feel the loop.

---

## 3. Phased plan

### Phase Now — Make the loop feel inevitable (1–2 weeks of focused work)

**Success:** Demo script completes in ≤5 min without explanation; every major feature has a number + CTA; Review badge is irresistible; no production data loss for signed-in users.

| ID | Work item | UX / UI adaptation | Appeal payload |
|---|---|---|---|
| N1 | **Production E2E** Render Starter + `PHRASEFRAME_DATA_DIR` | Invisible trust | Continuity is retention of *users* |
| N2 | **Hero rewrite** (`index.html` hero) | Numeric, multi-feature, anti-hype | See `AI_UI_COPY_PACK.md` §Hero |
| N3 | **Science grid → 5 pillars** | Expand from 3 cards to 5: Focus · Pace · Check · Gaps · Keep | Map each pillar to a feature |
| N4 | **Deep Pace education** | Under WPM slider: “Deep pace ≈ 250–350 for hard prose; we warn past ~350” + link to recall | Ricciardi / Brysbaert |
| N5 | **Recall Moment hierarchy** | Order: Score → Verdict line → Summary → Gaps → Cards count → CTAs (Review now / Return / Continue) | Reduce cognitive pile-up |
| N6 | **Review habit surfaces** | Tab badge always shows due count; empty state with “0 due — tomorrow protects yesterday”; post-weak-stop modal nudge | Spacing story |
| N7 | **Library pulse labels** | Rename/clarify: Due reviews · Avg recall · Weak stops · Last read; add tooltip with 61/40 or 67% threshold | Product metrics = science metrics |
| N8 | **Calibration ritual (lightweight)** | After Prepare: optional 45s “Find your deep pace” (3 phrases × 2 speeds + 1 question) | Personalization without LLM |
| N9 | **Mobile / a11y pass** | Attention Loop collapse; checkpoint full-screen sheet; Review thumb-zone CTAs | Habit on phone |
| N10 | **Instrumentation stubs** | Log (privacy-safe): WPM band × score; Review completion; D+1 resume | Path to PRODUCT-MEASURED claims |

### Phase Next — Make appeal stick and habit compound (2–4 weeks)

| ID | Work item | Why |
|---|---|---|
| X1 | **Deep Pace badge** in library (computed: max WPM with rolling recall ≥70%) | Hero metric becomes real |
| X2 | **Chapter weak-stop map** (pins on progress + list) | Visual storytelling for gaps |
| X3 | **Review session summary** (“3 cards · 2 Got it · next due in 1d”) | Dopamine without fake XP |
| X4 | **Science details drawer** with full citation list + “what we do / don’t claim” | Trust vs Spritz |
| X5 | **Onboarding demo text** rewritten around Attention Loop stages | First-run conversion |
| X6 | **Pace recommendation after weak stop** already exists—surface as “Suggested deep pace: N WPM” chip | Close the metacognition loop |
| X7 | **Card quality pass** (template questions → clearer fronts; answer = extractive span) | Retrieval only works if cards are answerable |

### Phase Later — Power without breaking honesty

| ID | Work item | Gate |
|---|---|---|
| L1 | LLM questions / summaries / cards | Never claim until live; keep extractive fallback |
| L2 | Full longitudinal dashboard (recall × WPM over weeks) | Needs instrumentation from N10 |
| L3 | FSRS instead of/in addition to SM-2 | Efficiency story (20–30% fewer reviews at same retention—Anki benchmarks); not retention magic |
| L4 | Offline / local processing option | Privacy segment |
| L5 | PRODUCT-MEASURED A/B: checkpoint on vs off → D+7 resume + again-rate | Only then upgrade copy from “lab studies” to “our users” |

---

## 4. Feature-specific UX adaptations (map to current UI)

### 4.1 Focus reader (`#reader-stage`)

- Keep focal guides; add microcopy under phrase: “Eyes stay here — phrases come to you.”  
- Progress track already has weak markers — label on first weak mark tooltip: “Weak stop — jump back from Review.”  
- Transport: elevate **Check** visually (primary secondary); demote MP4 to overflow/menu on narrow screens.

### 4.2 Pace (`#wpm`, `#speed-guidance`)

- Scale labels: Reflective (~220) · Deep work (~280–320) · Stretch (~350) · Skim risk (400+).  
- Guidance strings already warn >350 — add absolute baseline: “Adults average ~238 WPM on nonfiction (Brysbaert).”  
- Never celebrate 500.

### 4.3 Checkpoints (`#checkpoint`)

- Title → **“Recall check”** (active verb).  
- Intro: “Answer from memory. Checking is how memory is built—not just measured.”  
- After submit: if score ≥67%: “Solid encoding.” If <67%: “This stop is weak — summary + cards ready.”  
- Self-score buttons: keep Sure / Unsure / No idea; add one-line why (metacognition).

### 4.4 Gaps + summary (`#checkpoint-summary`, `#checkpoint-gaps`)

- Summary title → **“What that stretch said”**  
- Gaps title → **“What didn’t stick”**  
- Footer: “Gaps are not failure — they’re the shortest path to durable memory.”  
- CTA pair: **Review these cards** | **Reread this stretch** (Return).

### 4.5 Flashcards / Review (`#review-view`)

- Eyebrow already “SPACED REVIEW” — add: “High-utility technique (Dunlosky 2013).”  
- Card flip: front = question; back = answer + “From: {doc} · frame {n}” + **Return to passage**.  
- Got it / Again: sublabels “See later” / “See sooner” (spacing intuition).  
- Empty state: scientific, not sad.

### 4.6 Attention Loop (`#attention-loop`)

- Make stages clickable when available (jump to Review if cards due).  
- Active stage pulse animation (respect `prefers-reduced-motion`).  
- Persist completion checkmarks within session.

### 4.7 Library pulse (`#library-stats`)

- Avg recall → show as **“72% recall”** with helper “Target ≥70% at your pace.”  
- Due reviews → button that switches to Review tab.  
- Weak stops → expand panel by default after login if count > 0.

### 4.8 Science section (`.science`)

Replace 3-card grid with **5 pillars** + numbers (see copy pack). Expand `<details>` with testing/spacing citations, not only RSVP.

---

## 5. Measurement plan (so future claims upgrade)

| Metric | Definition | Why |
|---|---|---|
| Time-to-first-Check | Seconds from Prepare → first checkpoint submit | Activation |
| Checkpoint recall rate | Mean self-score / template score | Comprehension proxy |
| Deep Pace | Max WPM with rolling recall ≥0.70 | Hero KPI |
| Review conversion | Weak stop → ≥1 card reviewed same day | Loop closure |
| Again rate | % Again on first review | Card difficulty / quality |
| D+1 / D+7 resume | Continue within 1/7 days | Habit |
| WPM band × recall | Crosstab | Validates 350 guidance in *our* data |

Privacy: no document text in analytics; aggregate only.

---

## 6. Implementation order (for coding agents)

1. Copy/structure in `index.html` + `styles.css` (N2–N7, science grid) — no API change.  
2. Recall Moment DOM order + CTAs in `app.js` (N5).  
3. Review badge / empty states / due-as-button (N6–N7).  
4. Calibration optional flow (N8).  
5. Mobile CSS pass (N9).  
6. Deploy E2E (N1) in parallel.  
7. Instrumentation (N10).  
8. Deep Pace computation (X1).

Do **not** block UX polish on LLM.

---

## 7. Sibling AI assets

| File | Role |
|---|---|
| `docs/AI_BRIEF_UX_APPEAL.md` | Science + product truth (input) |
| `docs/AI_CLAIM_MATRIX.md` | Claim → surface → wording → grade → citation |
| `docs/AI_UI_COPY_PACK.md` | Drop-in strings mapped to DOM ids |
| `docs/UX_APPEAL_PLAN.md` | This plan |
| `docs/SCIENCE.md` | Update lightly when shipping new public claims |

---

## 8. Definition of done for this plan

- [ ] Hero + science section sell **all five** features with numbers  
- [ ] Recall Moment reads as a story, not a dump  
- [ ] Review tab is a first-class habit (badge, empty state, post-check nudge)  
- [ ] Pace UI teaches Deep Pace band with 238 / 350 / 400–450 figures  
- [ ] No forbidden claims in UI  
- [ ] Production E2E green for upload → check → review → return → continue next day  
- [ ] Claim matrix reviewed by a human before merge to marketing

---

*End plan. Next coding agent: implement Phase Now using `AI_UI_COPY_PACK.md` + `AI_CLAIM_MATRIX.md`.*
