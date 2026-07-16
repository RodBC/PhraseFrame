# PhraseFrame — AI AGENT PACK (START HERE)

```
ROLE: Implementation / planning agent for PhraseFrame web UX + scientific appeal.
MISSION: Polish the EXISTING Read→Check→Gaps→Cards→Review→Return loop so it feels
         inevitable, numeric, and trustworthy. Do NOT invent a new product.
OUTPUT: Code/UI changes OR a concrete task checklist — never vague strategy essays.
DOUBT: Every percentage. Prefer Safer wording. Never ship Grade F.
```

---

## 0. How to use this pack (mandatory)

### 0.1 Read order (do not skip)

| Step | File | Why |
|---|---|---|
| 1 | **This file** (`AI_AGENT_PACK.md`) | Rules, narrative, tasks, acceptance |
| 2 | `docs/nextsteps.md` § “O que já existe” + “Próxima ação” | What is already built vs open |
| 3 | `docs/AI_CLAIM_MATRIX.md` | Only when writing/editing user-visible claims |
| 4 | `docs/AI_UI_COPY_PACK.md` | Only when editing copy/DOM strings |
| 5 | `src/phraseframe/web/templates/index.html` + `app.js` + `styles.css` | Ground truth of UI |
| 6 | `docs/SCIENCE.md` | Hard product science constraints |
| 7 | `docs/AI_BRIEF_UX_APPEAL.md` | Deep evidence appendix (optional unless challenged) |
| 8 | `docs/UX_APPEAL_PLAN.md` | Phase backlog appendix (optional if this pack’s tasks suffice) |

### 0.2 Decision tree before every change

```
Is this change inside the existing loop (Read/Check/Gaps/Cards/Review/Return/Pace)?
  NO  → defer to Phase Later; do not implement unless user explicitly asks
  YES → continue

Does it add a user-visible NUMBER or scientific claim?
  YES → look up Claim ID in AI_CLAIM_MATRIX.md
        Grade F? → REJECT
        Grade C? → use Safer wording only + soft verbs (“designed to”, “studies of…”)
        Grade A/B? → prefer Safer; Max only in Science <details> with citation
        Implies “PhraseFrame users gain X%”? → REJECT unless PRODUCT-MEASURED
  NO  → implement with acceptance criteria below

Does it celebrate WPM > 350?
  YES → REJECT (warn instead; see web-reader rule)
  NO  → ok

Does it require LLM / new backend / new product vertical?
  YES → Phase Later only
  NO  → Phase Now / Next ok
```

### 0.3 Hard constraints (never violate)

1. Category = **focus + verified understanding + spaced keep**, NOT speed-reading.  
2. Core loop is **already built locally** — polish, don’t rebuild.  
3. Never: 2–3× speed with full comprehension; kill subvocalization; ADHD treatment; AI-understands-PDF while extractive/templates live; stacked mega-% (“52%+64%=better”).  
4. All lab % must be attributed: “In lab studies…” / “Classic experiments found…”.  
5. Product thresholds stay: weak stop **&lt;67%**; Deep Pace target **≥70%** recall.  
6. Preserve a11y: keyboard, focus-visible, `prefers-reduced-motion`, narrow screens.  
7. No remote fonts/trackers/CDNs.  
8. Do not log document text in analytics.

---

## 1. Product state (compressed truth)

| Item | State | Your job |
|---|---|---|
| Phrase-RSVP + pace + pause/back | ✅ | Keep; improve microcopy |
| PDF + account + resume | ✅ local | Don’t redesign auth; ensure Continue works |
| Checkpoints + self-score + weak stops | ✅ local | Improve hierarchy + copy |
| Extractive summary + gaps + ≤4 cards + SM-2 Review + Return | ✅ local | **Main appeal surface** |
| Attention Loop UI | ✅ demo | Make stages instructive |
| LLM questions/summaries | ❌ | Later |
| Full longitudinal dashboard | ❌ | Later |
| Production E2E Render + disk | ❌ | Trust-critical; do in parallel |
| PhraseFrame A/B % lifts | ❌ | Instrument only; don’t invent |

**North-star sentence (brand):**  
> Keep your eyes on one focal point, move through meaning-sized phrases at a pace you control, check recall at stop points, and turn gaps into spaced flashcards—so attention stays on the text and what you understood can stick.

**User-visible hero metric (build toward):**  
`Deep Pace = max WPM with rolling checkpoint recall ≥ 70%`  
Until coded: show WPM + Avg recall separately and teach the idea in copy.

---

## 2. Narrative → UI map (fit everything together)

Every screen must advance **one** stage. If copy doesn’t map, rewrite it.

```
FOCUS → CHECK → KEEP
  │        │       │
  │        │       └─ Review tab + SM-2 + Return to passage
  │        └─ Checkpoint → Recall Moment → Summary → Gaps → Cards CTA
  └─ Reader stage + WPM + phrase size + Attention Loop "Read"
```

| Stage | User need | DOM anchors | Must teach | Allowed claim IDs |
|---|---|---|---|---|
| Read | Attention / less scanning | `#reader-stage`, `#phrase`, Attention Loop | One focal point; phrases come to you | F1, F2 |
| Pace | Speed without self-deception | `#wpm`, `#speed-guidance` | ~238 baseline; 250–350 deep; warn ≥350–400 | P1–P3 |
| Check | Prove encoding | `#checkpoint`, `#manual-checkpoint-button` | Retrieval builds memory; 67% weak threshold | C1, C4, C5 |
| Gaps | Repair specifically | `#checkpoint-summary`, `#checkpoint-gaps` | Recap + what didn’t stick (not AI tutor) | G1–G3 |
| Cards | Convert failure → practice | `#checkpoint-cards-created`, Review CTA | Misses become due cards | R1, R6 |
| Review | Long-term keep | `#review-view`, `#review-tab` | 61% vs 40%; spacing vs cram | R1–R5 |
| Library | Habit / status | `#library-stats`, weak stops | Due / recall / weak / last read | P4 (future), C5 |

**Understanding answer (canonical — use in FAQ/Science; never collapse to one fake %):**

| Layer | Number | Feature |
|---|---|---|
| Focus during learning | MW probes **~19% vs ~40%** (Szpunar 2013) | Checkpoints |
| Encode / explain | Self-explanation **g≈0.55** (Bisra); illustrative Chi **15.3 vs 2.8** | Checkpoint answers |
| Remember @ 1 week | **61% vs 40%** idea units (Roediger & Karpicke 2006) | Check + Review |
| Keep / spacing | Up to **~64%** more recall vs massed (Cepeda 2008); testing+spacing = **high utility** (Dunlosky 2013) | SM-2 Review |
| Pace honesty | RSVP ≈ page at **250–350**; worse **400–450** (Ricciardi); adult **~238** (Brysbaert) | WPM UI |

---

## 3. Executable work (Phase Now) — do in order

Each task: **Files → Actions → Acceptance**. Stop when acceptance fails; fix before next task.

### Task N0 — Claim hygiene gate
- **Actions:** Skim §0.2–0.3. List any Grade F strings already in `index.html`; schedule removal in N2/N3.  
- **Accept:** No Grade F remains after N2/N3.

### Task N1 — Production trust (parallel OK)
- **Files:** hosting/deploy docs, env `PHRASEFRAME_DATA_DIR`  
- **Actions:** Deploy/verify upload → check → review → return → continue next day.  
- **Accept:** Signed-in progress + cards survive restart. Document in `HOSTING.md` if verified.

### Task N2 — Hero + meta teach the loop
- **Files:** `index.html`  
- **Actions:** Apply `AI_UI_COPY_PACK.md` § Meta + § Hero (**Safer** lead by default).  
- **Accept:** H1/lead mention focus + check + gaps/cards/keep; no 2× speed claim.

### Task N3 — Science section = 5 pillars + numbers
- **Files:** `index.html`, `styles.css`  
- **Actions:** Replace 3-card grid with 5 pillars from copy pack; expand `<details>` with testing/spacing citations.  
- **Accept:** Pillars cover Focus, Pace, Check, Gaps, Keep; details include 61/40 and 19/40; Rayner anti-hype preserved.

### Task N4 — Pace UI teaches Deep Pace band
- **Files:** `index.html`, `app.js` (`#speed-guidance` strings), `styles.css` if needed  
- **Actions:** Scale labels + guidance bands from copy pack; never celebrate >350.  
- **Accept:** At 400+ user sees skim-risk warning; ~238 mentioned once in deep band or science.

### Task N5 — Recall Moment hierarchy
- **Files:** `index.html` structure, `app.js` render order  
- **Actions:** Order = Score → Verdict → Summary → Gaps → Cards count → CTAs (`Review now` / `Return` / `Continue`). Apply checkpoint copy pack strings.  
- **Accept:** After submit, user can state in one glance: score, weak?, what to do next.

### Task N6 — Review habit surfaces
- **Files:** `app.js`, `index.html`, `styles.css`  
- **Actions:** Due count badge; empty state from copy pack; “Review {n} due” from library; post-weak-stop prefer Review CTA.  
- **Accept:** If due &gt; 0, Review tab shows count; empty state explains spacing (not failure).

### Task N7 — Library pulse clarity
- **Files:** `index.html` labels/title attrs, optional `app.js`  
- **Actions:** Helpers from copy pack; Avg recall implies ≥70% target.  
- **Accept:** Tooltips/helpers present; Due reviews clickable → Review tab.

### Task N8 — Attention Loop instructive
- **Files:** `index.html`, `app.js`, `styles.css`  
- **Actions:** Stage tooltips from copy pack; active stage visible; respect reduced-motion.  
- **Accept:** Hover/focus reveals what each stage means; stage tracks real flow.

### Task N9 — Mobile / checkpoint sheet
- **Files:** `styles.css`  
- **Actions:** Checkpoint usable full-width; Review actions thumb-reachable; Attention Loop doesn’t overflow.  
- **Accept:** ~390px width: check → submit → review CTA without horizontal scroll traps.

### Task N10 — Seed text + demo guide
- **Files:** `index.html` textarea + `#demo-guide`  
- **Actions:** Copy pack seed + demo steps.  
- **Accept:** First-run text teaches the loop without external docs.

### Task N11 — Instrumentation stubs (no PII/text)
- **Files:** backend/analytics only if exists; else note TODO in plan  
- **Actions:** Define events: `checkpoint_submit{wpm,score}`, `review_complete`, `resume_d1` — aggregate only.  
- **Accept:** Spec written or hooks added; no document body logged.

---

## 4. Phase Next / Later (do not start unless Phase Now done or user overrides)

| ID | When | What |
|---|---|---|
| X1 | After N10/N11 | Compute Deep Pace badge in library |
| X2 | Next | Chapter weak-stop map / pins story |
| X3 | Next | Review session end summary |
| L1 | Later | LLM questions/summaries (keep extractive fallback; never fake “AI grades you” before ship) |
| L2 | Later | Longitudinal dashboard |
| L3 | Later | FSRS optional |
| L4 | Later | PRODUCT-MEASURED A/B → only then “our users…” copy |

---

## 5. Copy selection algorithm

```
IF surface is Science <details> AND claim grade ∈ {A,B}:
  MAY use Max wording + DOI
ELSE IF surface is Hero / checkpoint / review empty / guidance:
  MUST use Safer wording from AI_CLAIM_MATRIX or AI_UI_COPY_PACK Safer
ELSE IF claim grade = C:
  MUST soft-verb; no hard %
ELSE IF claim grade = F:
  MUST NOT ship
ELSE IF claim grade = P (67%, 70%, Deep Pace):
  OK as product rules; do not call them lab findings
```

**Default hero lead:** Safer (copy pack).  
**Numeric hero lead:** only if user asks for aggressive A/B.

---

## 6. Definition of done (ship checklist)

```
[ ] Hero teaches FOCUS → CHECK → KEEP
[ ] Science has 5 pillars with numbers (pace, 19/40, 61/40, gaps, spacing)
[ ] Pace warns ≥350; does not celebrate 500
[ ] Recall Moment: score → verdict → summary → gaps → CTAs
[ ] Review badge + empty state + library Due → Review
[ ] Attention Loop tooltips present
[ ] No Grade F claims in UI
[ ] Mobile checkpoint usable
[ ] (Parallel) Production E2E resume works
```

---

## 7. Anti-patterns (if you catch yourself doing these, stop)

| Anti-pattern | Do instead |
|---|---|
| New feature vertical before polish | Finish Tasks N2–N10 |
| One mega-% for “understanding” | Use layered table §2 |
| Speed-first SEO | Comprehension-first meta |
| “AI summary” while extractive | “What that stretch said” |
| Rebuilding RSVP engine | Copy/CSS/`app.js` hierarchy only |
| Editing SCIENCE claims without matrix | Update matrix first |
| Long prose plan with no DOM anchors | Use Task format §3 |

---

## 8. Prompt templates (paste for sub-agents)

### 8.1 Implement Phase Now
```
Read docs/AI_AGENT_PACK.md sections 0–3 and 6.
Implement Tasks N2→N10 in order using docs/AI_UI_COPY_PACK.md.
Validate every new number against docs/AI_CLAIM_MATRIX.md grades.
Do not deploy LLM features. Warn, don’t celebrate, above 350 WPM.
Stop after Definition of Done checklist is green locally.
```

### 8.2 Copy-only pass
```
Read docs/AI_AGENT_PACK.md §5 and docs/AI_UI_COPY_PACK.md.
Update index.html (+ app.js guidance strings) only.
Prefer Safer wording. No Grade F. Keep existing behavior.
```

### 8.3 Skeptical review
```
Read docs/AI_AGENT_PACK.md §0.2–0.3 and docs/AI_CLAIM_MATRIX.md.
Audit index.html + app.js user-visible strings.
Output: table of [string | claim ID | grade | pass/fail | fix].
```

---

## 9. File map (what each doc is for)

| File | Type | Open when |
|---|---|---|
| `AI_AGENT_PACK.md` | **Controller** | Always first |
| `AI_UI_COPY_PACK.md` | Strings appendix | Editing UI text |
| `AI_CLAIM_MATRIX.md` | Policy appendix | Editing claims/numbers |
| `UX_APPEAL_PLAN.md` | Backlog appendix | Need Phase Next/Later detail |
| `AI_BRIEF_UX_APPEAL.md` | Evidence appendix | Claim challenged / need citations |
| `SCIENCE.md` | Product law | Changing scientific position |
| `nextsteps.md` | Roadmap truth | Checking build status |

---

## 10. One-screen truth pack (context-window emergency)

```
PRODUCT: phrase-RSVP focus reader + checkpoints + gap summary + SM-2 cards + return-to-frame
DONE LOCALLY: full loop; NOT DONE: prod E2E, LLM, full dashboard, measured user %
SELL: attention + verified recall + spaced keep
NUMBERS (lab-tagged only):
  61% vs 40% @1wk testing vs reread | ~64% spacing vs massed | MW 19% vs 40%
  deep pace ~250–350 WPM | baseline ~238 | warn ≥350–400 | weak <67% | target ≥70%
AUTHORITY: Dunlosky high utility = practice testing + distributed practice
UI JOB: teach FOCUS→CHECK→KEEP on hero, science×5, recall hierarchy, review habit
FORBIDDEN: 2× speed full comp, kill subvocalization, ADHD cure, fake AI tutor, stacked %
START TASKS: N2 hero → N3 science → N4 pace → N5 recall → N6 review → N7 library → N8 loop → N9 mobile
```

---

*End controller. Appendices: `AI_UI_COPY_PACK.md`, `AI_CLAIM_MATRIX.md`, `UX_APPEAL_PLAN.md`, `AI_BRIEF_UX_APPEAL.md`.*
