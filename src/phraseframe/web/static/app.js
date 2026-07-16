const elements = {
  text: document.querySelector("#source-text"),
  file: document.querySelector("#file-input"),
  words: document.querySelector("#word-count"),
  estimate: document.querySelector("#duration-estimate"),
  error: document.querySelector("#source-error"),
  signInBanner: document.querySelector("#sign-in-banner"),
  wpm: document.querySelector("#wpm"),
  wpmOutput: document.querySelector("#wpm-output"),
  guidance: document.querySelector("#speed-guidance"),
  chunkSize: document.querySelector("#chunk-size"),
  preview: document.querySelector("#preview-minute"),
  stopCheckpoints: document.querySelector("#stop-checkpoints"),
  stopEveryWords: document.querySelector("#stop-every-words"),
  prepare: document.querySelector("#prepare-button"),
  resume: document.querySelector("#resume-button"),
  stage: document.querySelector("#reader-stage"),
  phraseShell: document.querySelector(".phrase-shell"),
  phrase: document.querySelector("#phrase"),
  frameCounter: document.querySelector("#frame-counter"),
  timeCounter: document.querySelector("#time-counter"),
  progress: document.querySelector("#progress-bar"),
  play: document.querySelector("#play-button"),
  previous: document.querySelector("#previous-button"),
  next: document.querySelector("#next-button"),
  restart: document.querySelector("#restart-button"),
  fullscreen: document.querySelector("#fullscreen-button"),
  export: document.querySelector("#export-button"),
  exportStatus: document.querySelector("#export-status"),
  reflection: document.querySelector("#reflection"),
  checkpoint: document.querySelector("#checkpoint"),
  checkpointQuestions: document.querySelector("#checkpoint-questions"),
  checkpointFeedback: document.querySelector("#checkpoint-feedback"),
  checkpointSummary: document.querySelector("#checkpoint-summary"),
  checkpointSummaryText: document.querySelector("#checkpoint-summary-text"),
  checkpointGaps: document.querySelector("#checkpoint-gaps"),
  checkpointGapsList: document.querySelector("#checkpoint-gaps-list"),
  checkpointRecall: document.querySelector("#checkpoint-recall"),
  checkpointRecallScore: document.querySelector("#checkpoint-recall-score"),
  checkpointRecallVerdict: document.querySelector("#checkpoint-recall-verdict"),
  checkpointGuestHint: document.querySelector("#checkpoint-guest-hint"),
  checkpointCardsCreated: document.querySelector("#checkpoint-cards-created"),
  checkpointActions: document.querySelector("#checkpoint-actions"),
  checkpointContinue: document.querySelector("#checkpoint-continue"),
  chapterRow: document.querySelector("#chapter-row"),
  chapterSelect: document.querySelector("#chapter-select"),
  authForm: document.querySelector("#auth-form"),
  authEmail: document.querySelector("#auth-email"),
  authPassword: document.querySelector("#auth-password"),
  authError: document.querySelector("#auth-error"),
  registerButton: document.querySelector("#register-button"),
  accountStatus: document.querySelector("#account-status"),
  accountEmail: document.querySelector("#account-email"),
  logoutButton: document.querySelector("#logout-button"),
  libraryPanel: document.querySelector("#library-panel"),
  libraryList: document.querySelector("#library-list"),
  refreshLibrary: document.querySelector("#refresh-library-button"),
  libraryPendingReviews: document.querySelector("#library-pending-reviews"),
  libraryAverageComprehension: document.querySelector("#library-average-comprehension"),
  libraryDeepPace: document.querySelector("#library-deep-pace"),
  libraryWeakStops: document.querySelector("#library-weak-stops"),
  libraryLastRead: document.querySelector("#library-last-read"),
  continueBanner: document.querySelector("#continue-banner"),
  continueDocumentTitle: document.querySelector("#continue-document-title"),
  continueDocumentButton: document.querySelector("#continue-document-button"),
  viewTabs: document.querySelector("#view-tabs"),
  readTab: document.querySelector("#read-tab"),
  reviewTab: document.querySelector("#review-tab"),
  reviewTabCount: document.querySelector("#review-tab-count"),
  readerView: document.querySelector("#reader-view"),
  reviewView: document.querySelector("#review-view"),
  reviewPanel: document.querySelector("#review-panel"),
  reviewCard: document.querySelector("#review-card"),
  reviewDocumentTitle: document.querySelector("#review-document-title"),
  reviewFront: document.querySelector("#review-front"),
  reviewBack: document.querySelector("#review-back"),
  reviewActions: document.querySelector("#review-actions"),
  reviewList: document.querySelector("#review-list"),
  reviewStatus: document.querySelector("#review-status"),
  reviewSourceLocation: document.querySelector("#review-source-location"),
  reviewSessionSummary: document.querySelector("#review-session-summary"),
  refreshReview: document.querySelector("#refresh-review-button"),
  weakStopsPanel: document.querySelector("#weak-stops-panel"),
  weakStopsList: document.querySelector("#weak-stops-list"),
  progressTrack: document.querySelector("#progress-track"),
  weakFrameMarkers: document.querySelector("#weak-frame-markers"),
  manualCheckpoint: document.querySelector("#manual-checkpoint-button"),
  attentionLoop: document.querySelector("#attention-loop"),
  demoGuide: document.querySelector("#demo-guide"),
  demoGuideDismiss: document.querySelector("#demo-guide-dismiss"),
  heroStartLoop: document.querySelector("#hero-start-loop"),
  timelineStaleWarning: document.querySelector("#timeline-stale-warning"),
  sourcePanelToggle: document.querySelector("#source-panel-toggle"),
  attentionLoopComplete: document.querySelector("#attention-loop-complete"),
};

const state = {
  timeline: null,
  stopFrames: new Set(),
  index: 0,
  playing: false,
  timer: null,
  token: localStorage.getItem("phraseframe_token"),
  email: localStorage.getItem("phraseframe_email"),
  documentId: null,
  chapters: [],
  chapterIndex: 0,
  guestFile: null,
  pendingProgress: null,
  progressTimer: null,
  lastSavedProgress: null,
  lastCheckpointFrame: 0,
  activeCheckpointId: null,
  checkpointPhase: null,
  lastRecallResult: null,
  libraryHasDocuments: false,
  libraryDocuments: [],
  weakFrames: [],
  reviewCards: [],
  reviewIndex: 0,
  reviewRevealed: false,
  reviewSessionGraded: 0,
  reviewSessionAgain: 0,
  activeView: "read",
  previewQuestions: null,
  timelineSignature: null,
  reducedMotionReading: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
};

function authHeaders() {
  return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

function countWords(text) {
  return (text.match(/[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu) || []).length;
}

function formatTime(milliseconds) {
  const totalSeconds = Math.round(milliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  return `${minutes}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function setView(view) {
  const nextView = view === "review" ? "review" : "read";
  state.activeView = nextView;
  const reviewing = nextView === "review";
  elements.readerView.hidden = reviewing;
  elements.reviewView.hidden = !reviewing;
  elements.readTab.classList.toggle("active", !reviewing);
  elements.reviewTab.classList.toggle("active", reviewing);
  elements.readTab.setAttribute("aria-selected", String(!reviewing));
  elements.reviewTab.setAttribute("aria-selected", String(reviewing));
  elements.readTab.tabIndex = reviewing ? -1 : 0;
  elements.reviewTab.tabIndex = reviewing ? 0 : -1;
  updateAttentionLoop();
  if (reviewing) refreshReview().catch(() => {});
}

function updateAttentionLoop() {
  if (!elements.attentionLoop) return;
  const inLoop = Boolean(state.timeline?.frames.length) && (state.token || state.checkpointPhase);
  elements.attentionLoop.hidden = !inLoop;
  let activeStage = "read";
  if (state.activeView === "review") {
    activeStage = "review";
  } else if (state.checkpointPhase === "questions") {
    activeStage = "check";
  } else if (state.checkpointPhase === "results") {
    const result = state.lastRecallResult;
    if (result?.gapsCount > 0) activeStage = "gaps";
    else if (result?.flashcards_added > 0) activeStage = "cards";
    else activeStage = "check";
  }
  const stages = ["read", "check", "gaps", "cards", "review"];
  const activeIndex = stages.indexOf(activeStage);
  for (const item of elements.attentionLoop.querySelectorAll("[data-stage]")) {
    const itemIndex = stages.indexOf(item.dataset.stage);
    item.classList.toggle("active", itemIndex === activeIndex);
    item.classList.toggle("complete", itemIndex < activeIndex);
    if (itemIndex === activeIndex) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  }
  if (elements.attentionLoopComplete) {
    const loopClosed = state.activeView === "review" && state.reviewIndex >= state.reviewCards.length && state.reviewSessionGraded > 0;
    elements.attentionLoopComplete.hidden = !loopClosed;
  }
}

function requestBody() {
  const targetWords = Number(elements.chunkSize.value);
  const body = {
    text: elements.text.value,
    wpm: Number(elements.wpm.value),
    target_words: targetWords,
    max_words: Math.min(targetWords + 2, 10),
    max_characters: 42,
    preview_seconds: elements.preview.checked ? 60 : null,
  };
  if (elements.stopCheckpoints.checked) {
    body.stop_every_words = Number(elements.stopEveryWords.value);
  }
  return body;
}

function updateSourceMeta() {
  const words = countWords(elements.text.value);
  const wpm = Number(elements.wpm.value);
  elements.words.textContent = `${words} word${words === 1 ? "" : "s"}`;
  elements.estimate.textContent = words ? `about ${formatTime((words / wpm) * 60_000)}` : "—";
}

function updatePaceGuidance() {
  const wpm = Number(elements.wpm.value);
  elements.wpmOutput.textContent = `${wpm} WPM`;
  elements.guidance.classList.toggle("warning", wpm > 350);
  if (wpm <= 250) {
    elements.guidance.textContent = "Reflective pace. Close to careful study; strong for dense argument.";
  } else if (wpm <= 320) {
    elements.guidance.textContent = "Deep-work band. Near typical adult nonfiction (~238 WPM average) up through brisk comprehension.";
  } else if (wpm <= 350) {
    elements.guidance.textContent = "Stretch pace. Still in the band where RSVP studies often match page reading—watch your self-check score.";
  } else if (wpm <= 400) {
    elements.guidance.textContent = "Caution. Research often finds thinner comprehension as you enter the 350–400+ zone. Prefer first passes.";
  } else {
    elements.guidance.textContent = "Skim risk. Studies commonly show clearer losses around 400–450 WPM. Slow down for anything you need to keep.";
  }
  markTimelineStale();
  updateSourceMeta();
}

function currentTimelineSignature() {
  return JSON.stringify(requestBody());
}

function markTimelineStale() {
  if (!elements.timelineStaleWarning) return;
  const stale = state.timeline && state.timelineSignature !== currentTimelineSignature();
  elements.timelineStaleWarning.hidden = !stale;
}

function announceLive(message) {
  const live = document.createElement("div");
  live.className = "sr-only";
  live.setAttribute("role", "status");
  live.setAttribute("aria-live", "polite");
  live.textContent = message;
  document.body.append(live);
  setTimeout(() => live.remove(), 1200);
}

async function apiError(response) {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg).join(" ");
    }
    return "The request could not be completed.";
  } catch {
    return "The request could not be completed.";
  }
}

function showAuthError(message) {
  elements.authError.textContent = message;
  elements.authError.hidden = false;
}

function clearAuthError() {
  elements.authError.hidden = true;
  elements.authError.textContent = "";
}

function validateAuthInput() {
  const email = elements.authEmail.value.trim();
  const password = elements.authPassword.value;
  if (!email || !email.includes("@")) {
    return "Enter a valid email address.";
  }
  if (password.length < 8) {
    return "Passwords must be at least 8 characters.";
  }
  return null;
}

function stop() {
  state.playing = false;
  clearTimeout(state.timer);
  state.timer = null;
  updatePlayControl();
  scheduleProgressSave();
}

function phraseAvailableWidth() {
  const shell = elements.phraseShell ?? elements.stage;
  return Math.max(0, shell.clientWidth);
}

function fitPhraseOnOneLine() {
  elements.phrase.style.removeProperty("font-size");
  const availableWidth = phraseAvailableWidth();
  elements.phrase.style.maxWidth = `${availableWidth}px`;

  let fontSize = Number.parseFloat(getComputedStyle(elements.phrase).fontSize);
  const minimum = window.matchMedia("(max-width: 640px)").matches ? 11 : 12;

  while (elements.phrase.scrollWidth > availableWidth && fontSize > minimum) {
    fontSize -= 1;
    elements.phrase.style.fontSize = `${fontSize}px`;
  }
}

function hideCheckpoint() {
  elements.checkpoint.hidden = true;
  elements.checkpointQuestions.replaceChildren();
  elements.checkpointFeedback.hidden = true;
  elements.checkpointFeedback.textContent = "";
  elements.checkpointSummary.hidden = true;
  elements.checkpointSummaryText.textContent = "";
  elements.checkpointGaps.hidden = true;
  elements.checkpointGapsList.replaceChildren();
  elements.checkpointRecall.hidden = true;
  elements.checkpointRecallScore.textContent = "";
  if (elements.checkpointRecallVerdict) elements.checkpointRecallVerdict.textContent = "";
  if (elements.checkpointGuestHint) elements.checkpointGuestHint.hidden = true;
  elements.checkpointCardsCreated.hidden = true;
  elements.checkpointCardsCreated.textContent = "";
  elements.checkpointActions.hidden = true;
  elements.checkpointActions.replaceChildren();
  elements.checkpointQuestions.hidden = false;
  elements.checkpointContinue.textContent = "Submit answers";
  state.activeCheckpointId = null;
  state.checkpointPhase = null;
  state.lastRecallResult = null;
  updateAttentionLoop();
}

function gapReason(reason) {
  const labels = {
    empty_answer: "No answer was provided.",
    no_idea: "Marked as “No idea”.",
    unsure: "Marked as uncertain.",
    low_confidence: "Confidence was low.",
  };
  return labels[reason] ?? String(reason ?? "Needs another look").replaceAll("_", " ");
}

function renderCheckpointResults(payload) {
  const summary = typeof payload.summary === "string" ? payload.summary.trim() : "";
  elements.checkpointSummary.hidden = !summary;
  elements.checkpointSummaryText.textContent = summary;

  const gaps = Array.isArray(payload.gaps) ? payload.gaps : [];
  elements.checkpointGapsList.replaceChildren();
  for (const gap of gaps) {
    const item = document.createElement("li");
    const question = document.createElement("strong");
    question.textContent = gap.question_text || gap.question || `Question ${gap.question_id ?? ""}`;
    const reason = document.createElement("span");
    reason.textContent = gapReason(gap.reason);
    item.append(question, reason);
    elements.checkpointGapsList.append(item);
  }
  elements.checkpointGaps.hidden = gaps.length === 0;
}

function renderRecallMoment(payload) {
  const score = Number(payload.score);
  const scorePercent = Number.isFinite(score) ? Math.round(score * 100) : 0;
  elements.checkpointRecall.hidden = false;
  elements.checkpointRecall.classList.toggle("weak", Boolean(payload.weak));
  elements.checkpointRecallScore.textContent = `${scorePercent}% self-check score`;
  if (elements.checkpointRecallVerdict) {
    elements.checkpointRecallVerdict.textContent = payload.weak
      ? "Weak stop. Here’s what the stretch said, what slipped, and cards to practice."
      : "Solid encoding. You can continue—or review cards to lock it further.";
  }
  const cardsCreated = Number(payload.flashcards_added) || 0;
  elements.checkpointCardsCreated.textContent = cardsCreated
    ? `${cardsCreated} review card${cardsCreated === 1 ? "" : "s"} ready — first review can start now`
    : "";
  elements.checkpointCardsCreated.hidden = cardsCreated === 0;
  if (elements.checkpointGuestHint) {
    elements.checkpointGuestHint.hidden = Boolean(state.token);
  }
  state.lastRecallResult = {
    score,
    weak: Boolean(payload.weak),
    flashcards_added: cardsCreated,
    gapsCount: Array.isArray(payload.gaps) ? payload.gaps.length : 0,
  };
  state.checkpointPhase = "results";
  elements.checkpointQuestions.hidden = true;
  elements.checkpointContinue.textContent = "Continue reading";
  updateAttentionLoop();
}

function confidenceSelect(questionId) {
  const select = document.createElement("select");
  select.dataset.questionId = questionId;
  select.setAttribute("aria-label", "How confident are you in this answer?");
  for (const option of [
    { value: "sure", label: "Sure" },
    { value: "unsure", label: "Unsure" },
    { value: "no_idea", label: "No idea" },
  ]) {
    const item = document.createElement("option");
    item.value = option.value;
    item.textContent = option.label;
    select.append(item);
  }
  select.value = "unsure";
  return select;
}

async function showCheckpoint() {
  if (!state.timeline?.frames.length) return;
  elements.reflection.hidden = true;
  elements.checkpoint.hidden = false;
  state.checkpointPhase = "questions";
  state.lastRecallResult = null;
  elements.checkpointQuestions.hidden = false;
  elements.checkpointContinue.textContent = "Submit answers";
  elements.checkpointFeedback.hidden = true;
  elements.checkpointRecall.hidden = true;
  elements.checkpointSummary.hidden = true;
  elements.checkpointGaps.hidden = true;
  if (elements.checkpointGuestHint) {
    elements.checkpointGuestHint.hidden = Boolean(state.token);
  }
  elements.checkpointQuestions.textContent = "Preparing questions…";
  updateAttentionLoop();
  try {
    if (state.documentId && state.token) {
      const response = await fetch(`/api/documents/${state.documentId}/checkpoints`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          frame_index: state.index,
          chapter_index: state.chapterIndex,
        }),
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json();
      state.activeCheckpointId = payload.checkpoint_id;
      state.previewQuestions = null;
      renderCheckpointQuestions(payload.questions);
      return;
    }
    const response = await fetch("/api/checkpoints/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: elements.text.value,
        frame_index: state.index,
        wpm: Number(elements.wpm.value),
        target_words: Number(elements.chunkSize.value),
      }),
    });
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    state.activeCheckpointId = payload.checkpoint_id;
    state.previewQuestions = payload.questions;
    renderCheckpointQuestions(payload.questions);
  } catch (error) {
    elements.checkpointQuestions.textContent = error.message;
  }
}

function renderCheckpointQuestions(questions) {
  elements.checkpointQuestions.replaceChildren();
  for (const question of questions) {
    const label = document.createElement("label");
    label.className = "checkpoint-question";
    const prompt = document.createElement("span");
    prompt.textContent = question.text;
    const input = document.createElement("textarea");
    input.rows = 2;
    input.dataset.questionId = question.id;
    input.setAttribute("aria-label", question.text);
    label.append(prompt, input, confidenceSelect(question.id));
    elements.checkpointQuestions.append(label);
  }
}

async function submitCheckpoint() {
  if (!state.activeCheckpointId) {
    hideCheckpoint();
    return;
  }
  const answers = [...elements.checkpointQuestions.querySelectorAll("textarea")].map(
    (input) => {
      const confidence = elements.checkpointQuestions.querySelector(
        `select[data-question-id="${input.dataset.questionId}"]`,
      );
      return {
        text: input.value.trim(),
        confidence: confidence?.value ?? "unsure",
      };
    },
  );
  if (!answers.some((answer) => answer.text)) {
    elements.checkpointFeedback.textContent = "Answer at least one question before continuing.";
    elements.checkpointFeedback.hidden = false;
    return false;
  }

  let payload;
  if (state.documentId && state.token) {
    const response = await fetch(`/api/documents/${state.documentId}/checkpoints`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        frame_index: state.index,
        chapter_index: state.chapterIndex,
        checkpoint_id: state.activeCheckpointId,
        answers,
      }),
    });
    if (!response.ok) {
      elements.checkpointFeedback.textContent = await apiError(response);
      elements.checkpointFeedback.hidden = false;
      return false;
    }
    payload = await response.json();
  } else {
    const response = await fetch("/api/checkpoints/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: elements.text.value,
        frame_index: state.index,
        wpm: Number(elements.wpm.value),
        target_words: Number(elements.chunkSize.value),
        answers,
        questions: state.previewQuestions,
      }),
    });
    if (!response.ok) {
      elements.checkpointFeedback.textContent = await apiError(response);
      elements.checkpointFeedback.hidden = false;
      return false;
    }
    payload = await response.json();
  }

  let feedbackText = payload.feedback || "Checkpoint saved.";
  if (payload.sign_in_hint) feedbackText += ` ${payload.sign_in_hint}`;
  if (payload.weak && payload.wpm_adjust) {
    feedbackText += ` Consider slowing by ${Math.abs(payload.wpm_adjust)} WPM.`;
  }
  if (payload.flashcards_added) {
    feedbackText += ` ${payload.flashcards_added} review card${payload.flashcards_added === 1 ? "" : "s"} added.`;
    await refreshReview();
  }
  elements.checkpointFeedback.textContent = feedbackText;
  elements.checkpointFeedback.hidden = false;
  renderCheckpointResults(payload);
  renderRecallMoment(payload);
  elements.checkpointActions.replaceChildren();
  if (payload.weak) {
    const reread = document.createElement("button");
    reread.type = "button";
    reread.textContent = "Re-read last 10 phrases";
    reread.addEventListener("click", () => {
      state.index = Math.max(0, state.index - 10);
      hideCheckpoint();
      showFrame();
    });
    elements.checkpointActions.append(reread);
  }
  if (state.token && payload.flashcards_added) {
    const reviewNow = document.createElement("button");
    reviewNow.type = "button";
    reviewNow.textContent = "Review now";
    reviewNow.className = "primary";
    reviewNow.addEventListener("click", () => {
      hideCheckpoint();
      setView("review");
    });
    elements.checkpointActions.append(reviewNow);
  } else if (!state.token) {
    const signIn = document.createElement("button");
    signIn.type = "button";
    signIn.textContent = "Sign in to save cards";
    signIn.className = "primary";
    signIn.addEventListener("click", () => {
      elements.authEmail.focus();
    });
    elements.checkpointActions.append(signIn);
  }
  const returnPassage = document.createElement("button");
  returnPassage.type = "button";
  returnPassage.textContent = "Return to passage";
  returnPassage.addEventListener("click", () => {
    hideCheckpoint();
    jumpToFrame(state.index);
  });
  elements.checkpointActions.append(returnPassage);
  elements.checkpointActions.hidden = elements.checkpointActions.childElementCount === 0;
  if (payload.wpm_adjust) {
    elements.wpm.value = String(
      Math.max(200, Math.min(500, Number(elements.wpm.value) + payload.wpm_adjust)),
    );
    updatePaceGuidance();
  }
  state.lastCheckpointFrame = state.index + 1;
  state.activeCheckpointId = null;
  state.previewQuestions = null;
  await refreshWeakStops();
  return true;
}

function isStopFrame() {
  return state.stopFrames.has(state.index);
}

function applyTimeline(timeline) {
  state.timeline = timeline;
  state.stopFrames = new Set(timeline.stop_frames ?? []);
}

function renderWeakFrameMarkers() {
  const frameCount = state.timeline?.frames.length ?? 0;
  elements.weakFrameMarkers.replaceChildren();
  if (!frameCount) return;
  for (const frameIndex of state.weakFrames) {
    if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= frameCount) continue;
    const marker = document.createElement("button");
    marker.type = "button";
    marker.className = "weak-frame-marker";
    marker.style.left = `${((frameIndex + 1) / frameCount) * 100}%`;
    marker.title = `Weak checkpoint at phrase ${frameIndex + 1}`;
    marker.setAttribute("aria-label", marker.title);
    marker.addEventListener("click", () => jumpToFrame(frameIndex));
    elements.weakFrameMarkers.append(marker);
  }
}

function showFrame() {
  const timeline = state.timeline;
  if (!timeline?.frames.length) return;
  const frame = timeline.frames[state.index];
  elements.phrase.textContent = frame.text;
  fitPhraseOnOneLine();
  elements.frameCounter.textContent = `${state.index + 1} / ${timeline.frames.length}`;
  elements.timeCounter.textContent = `${formatTime(frame.starts_at_ms)} / ${formatTime(timeline.duration_ms)}`;
  const progressPercent = ((state.index + 1) / timeline.frames.length) * 100;
  elements.progress.style.width = `${progressPercent}%`;
  elements.progressTrack.setAttribute("aria-valuenow", String(Math.round(progressPercent)));
  renderWeakFrameMarkers();
  scheduleProgressSave();
  if (state.playing) {
    clearTimeout(state.timer);
    const delay = state.reducedMotionReading ? Math.max(frame.duration_ms, 900) : frame.duration_ms;
    state.timer = setTimeout(() => {
      if (state.index >= timeline.frames.length - 1) {
        stop();
        if (!isStopFrame()) {
          elements.reflection.hidden = false;
        } else {
          showCheckpoint();
        }
      } else if (isStopFrame()) {
        stop();
        showCheckpoint();
      } else {
        state.index += 1;
        showFrame();
      }
    }, frame.duration_ms);
  }
}

function updatePlayControl() {
  elements.play.textContent = state.playing ? "Ⅱ" : "▶";
  elements.play.setAttribute("aria-label", state.playing ? "Pause" : "Play");
  elements.play.setAttribute("aria-pressed", String(state.playing));
}

function togglePlay() {
  if (!state.timeline?.frames.length) return;
  state.playing = !state.playing;
  updatePlayControl();
  if (state.playing) {
    elements.reflection.hidden = true;
    hideCheckpoint();
    showFrame();
  } else {
    clearTimeout(state.timer);
    scheduleProgressSave();
  }
}

function move(delta) {
  if (!state.timeline?.frames.length) return;
  state.index = Math.max(0, Math.min(state.timeline.frames.length - 1, state.index + delta));
  showFrame();
}

function renderChapterOptions() {
  const hasMultiple = state.chapters.length > 1;
  elements.chapterRow.hidden = !hasMultiple;
  elements.chapterSelect.replaceChildren();
  for (const chapter of state.chapters) {
    const option = document.createElement("option");
    option.value = String(chapter.index);
    option.textContent = chapter.title;
    elements.chapterSelect.append(option);
  }
  elements.chapterSelect.value = String(state.chapterIndex);
}

function applyChapterText(text, index) {
  state.chapterIndex = index;
  elements.text.value = text;
  updateSourceMeta();
}

async function loadChapter(index) {
  state.chapterIndex = index;
  elements.chapterSelect.value = String(index);
  if (state.documentId && state.token) {
    const response = await fetch(
      `/api/documents/${state.documentId}/chapters/${index}`,
      { headers: authHeaders() },
    );
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    applyChapterText(payload.text, index);
    return;
  }
  if (state.guestFile) {
    const data = new FormData();
    data.append("file", state.guestFile);
    const response = await fetch(`/api/extract?chapter_index=${index}`, {
      method: "POST",
      body: data,
    });
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    applyChapterText(payload.text, index);
  }
}

function progressPayload() {
  const payload = {
    chapter_index: state.chapterIndex,
    frame_index: state.index,
    wpm: Number(elements.wpm.value),
    target_words: Number(elements.chunkSize.value),
  };
  if (elements.stopCheckpoints.checked) {
    payload.stop_every_words = Number(elements.stopEveryWords.value);
  }
  return payload;
}

async function saveProgressNow() {
  if (!state.token || !state.documentId || !state.timeline?.frames.length) return;
  const payload = progressPayload();
  const signature = JSON.stringify(payload);
  if (signature === state.lastSavedProgress) return;

  const response = await fetch(`/api/documents/${state.documentId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
    keepalive: true,
  });
  if (!response.ok) throw new Error(await apiError(response));
  state.lastSavedProgress = signature;
}

function flushProgressSave() {
  if (!state.token || !state.documentId || !state.timeline?.frames.length) return;
  clearTimeout(state.progressTimer);
  fetch(`/api/documents/${state.documentId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(progressPayload()),
    keepalive: true,
  }).catch(() => {});
}

function applyMetadataPayload(payload) {
  state.documentId = payload.document_id ?? null;
  state.chapters = payload.chapters ?? [];
  state.chapterIndex = payload.chapter_index ?? 0;
  state.pendingProgress = payload.progress ?? null;
  state.lastSavedProgress = null;
  state.lastCheckpointFrame = 0;
  state.weakFrames = [];
  renderWeakFrameMarkers();
  renderChapterOptions();
  if (payload.text) {
    applyChapterText(payload.text, state.chapterIndex);
  }
  elements.resume.hidden = !state.pendingProgress;
}

async function prepareReader() {
  stop();
  elements.error.hidden = true;
  elements.prepare.disabled = true;
  elements.prepare.textContent = "Preparing…";
  try {
    const response = await fetch("/api/timeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody()),
    });
    if (!response.ok) throw new Error(await apiError(response));
    applyTimeline(await response.json());
    state.timelineSignature = currentTimelineSignature();
    state.index = 0;
    state.lastSavedProgress = null;
    state.lastCheckpointFrame = 0;
    elements.reflection.hidden = true;
    hideCheckpoint();
    markTimelineStale();
    showFrame();
    if (state.token && state.documentId) {
      fetch("/api/learning-events", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          event_type: "prepare",
          document_id: state.documentId,
          chapter_index: state.chapterIndex,
          wpm: Number(elements.wpm.value),
        }),
      }).catch(() => {});
    }
    document.querySelector("#reader-view")?.classList.add("reader-ready");
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.prepare.disabled = false;
    elements.prepare.textContent = "Prepare focus reader";
  }
}

async function resumeReading() {
  if (!state.pendingProgress) return;
  elements.wpm.value = String(state.pendingProgress.wpm);
  elements.chunkSize.value = String(state.pendingProgress.target_words);
  if (state.pendingProgress.stop_every_words) {
    elements.stopCheckpoints.checked = true;
    elements.stopEveryWords.value = String(state.pendingProgress.stop_every_words);
    elements.stopEveryWords.disabled = false;
  } else {
    elements.stopCheckpoints.checked = false;
    elements.stopEveryWords.disabled = true;
  }
  updatePaceGuidance();
  state.chapterIndex = state.pendingProgress.chapter_index;
  if (!elements.text.value.trim()) {
    await loadChapter(state.chapterIndex);
  }
  elements.chapterSelect.value = String(state.chapterIndex);
  await prepareReader();
  state.index = Math.min(
    state.pendingProgress.frame_index,
    Math.max(0, (state.timeline?.frames.length ?? 1) - 1),
  );
  showFrame();
  elements.resume.hidden = true;
}

async function uploadDocument() {
  const selected = elements.file.files[0];
  if (!selected) return;
  elements.error.hidden = true;
  const data = new FormData();
  data.append("file", selected);
  try {
    if (state.token) {
      const response = await fetch("/api/documents", {
        method: "POST",
        headers: authHeaders(),
        body: data,
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json();
      applyMetadataPayload(payload);
      if (!payload.text) {
        await loadChapter(payload.chapter_index ?? 0);
      }
      await refreshLibrary();
      await refreshWeakStops();
    } else {
      state.guestFile = selected;
      state.documentId = null;
      const response = await fetch("/api/extract", {
        method: "POST",
        body: data,
      });
      if (!response.ok) throw new Error(await apiError(response));
      const payload = await response.json();
      applyMetadataPayload(payload);
    }
    await prepareReader();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.file.value = "";
  }
}

function scheduleProgressSave() {
  if (!state.token || !state.documentId) return;
  clearTimeout(state.progressTimer);
  state.progressTimer = setTimeout(() => {
    saveProgressNow().catch(() => {});
  }, 800);
}

async function refreshLibrary() {
  if (!state.token) {
    elements.libraryPanel.hidden = true;
    elements.continueBanner.hidden = true;
    state.libraryHasDocuments = false;
    state.libraryDocuments = [];
    return;
  }
  const response = await fetch("/api/documents", { headers: authHeaders() });
  if (!response.ok) {
    if (response.status === 401) {
      signOut();
      showAuthError("Session expired on this server. Sign in again, then upload.");
    }
    elements.libraryPanel.hidden = true;
    elements.continueBanner.hidden = true;
    state.libraryHasDocuments = false;
    state.libraryDocuments = [];
    return;
  }
  const payload = await response.json();
  const documents = Array.isArray(payload.documents) ? payload.documents : [];
  state.libraryDocuments = documents;
  state.libraryHasDocuments = documents.length > 0;
  elements.libraryPanel.hidden = false;
  elements.libraryList.replaceChildren();
  for (const entry of documents) {
    const item = document.createElement("li");
    const label = document.createElement("span");
    let labelText = `${entry.title} · ${entry.format.toUpperCase()}`;
    if (entry.comprehension_rate != null) {
      labelText += ` · ${Math.round(entry.comprehension_rate * 100)}% self-check`;
    }
    label.textContent = labelText;
    const action = document.createElement("button");
    action.type = "button";
    action.textContent = entry.has_progress ? "Continue" : "Open";
    action.addEventListener("click", () => resumeDocument(entry.id));
    item.append(label, action);
    elements.libraryList.append(item);
  }
  renderContinueBanner(documents);
  await refreshLibrarySummary();
}

function renderContinueBanner(documents) {
  const resumable = documents.filter((entry) => entry.has_progress);
  if (!resumable.length) {
    elements.continueBanner.hidden = true;
    elements.continueDocumentButton.onclick = null;
    return;
  }
  const document = [...resumable].sort((left, right) => {
    const leftTime = Date.parse(left.progress_updated_at || left.created_at || 0);
    const rightTime = Date.parse(right.progress_updated_at || right.created_at || 0);
    return rightTime - leftTime;
  })[0];
  elements.continueBanner.hidden = false;
  elements.continueDocumentTitle.textContent = document.title || "Untitled document";
  elements.continueDocumentButton.onclick = () => {
    elements.continueBanner.hidden = true;
    setView("read");
    resumeDocument(document.id);
  };
}

async function refreshLibrarySummary() {
  elements.libraryPendingReviews.textContent = "—";
  elements.libraryAverageComprehension.textContent = "—";
  if (elements.libraryDeepPace) elements.libraryDeepPace.textContent = "—";
  elements.libraryWeakStops.textContent = "—";
  elements.libraryLastRead.textContent = "—";
  try {
    const response = await fetch("/api/library/summary", { headers: authHeaders() });
    if (!response.ok) return;
    const payload = await response.json();
    const pending =
      payload.pending_flashcards ??
      payload.pending_reviews ??
      payload.due_flashcards ??
      payload.due_count;
    const average =
      payload.average_comprehension ??
      payload.avg_comprehension ??
      payload.average_score ??
      payload.avg_score;
    const lastRead =
      payload.last_read_at ??
      payload.last_read ??
      payload.last_updated_at ??
      payload.updated_at;
    const weakStops = payload.weak_stop_count ?? payload.weak_stops ?? payload.weak_count;
    if (Number.isFinite(Number(pending)) && Number(pending) > 0) {
      elements.libraryPendingReviews.innerHTML = `<button type="button" class="library-due-link">${Number(pending)} due · Review now</button>`;
      elements.libraryPendingReviews.querySelector("button")?.addEventListener("click", () => setView("review"));
    } else if (Number.isFinite(Number(pending))) {
      elements.libraryPendingReviews.textContent = String(Number(pending));
    }
    if (Number.isFinite(Number(average))) {
      const numericAverage = Number(average);
      const percent = numericAverage <= 1 ? numericAverage * 100 : numericAverage;
      elements.libraryAverageComprehension.textContent = `${Math.round(percent)}%`;
    }
    if (Number.isFinite(Number(weakStops))) {
      elements.libraryWeakStops.textContent = String(Number(weakStops));
    }
    elements.libraryLastRead.textContent = formatDate(lastRead);
    if (elements.libraryDeepPace) {
      if (payload.deep_pace_wpm != null) {
        elements.libraryDeepPace.textContent = `${payload.deep_pace_wpm} WPM`;
        elements.libraryDeepPace.title = payload.deep_pace_message || "";
      } else {
        elements.libraryDeepPace.textContent = "—";
        elements.libraryDeepPace.title = payload.deep_pace_message || "Not enough checks yet";
      }
    }
  } catch {
    // Aggregate stats are optional; the document library remains usable without them.
  }
}

function jumpToFrame(frameIndex) {
  if (!state.timeline?.frames.length) return;
  stop();
  state.index = Math.max(0, Math.min(state.timeline.frames.length - 1, frameIndex));
  hideCheckpoint();
  elements.reflection.hidden = true;
  showFrame();
}

async function refreshWeakStops() {
  if (!state.token || !state.documentId) {
    elements.weakStopsPanel.hidden = true;
    state.weakFrames = [];
    renderWeakFrameMarkers();
    return;
  }
  const response = await fetch(`/api/documents/${state.documentId}/checkpoints`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    elements.weakStopsPanel.hidden = true;
    state.weakFrames = [];
    renderWeakFrameMarkers();
    return;
  }
  const payload = await response.json();
  const checkpoints = Array.isArray(payload.checkpoints) ? payload.checkpoints : [];
  const weakStops = checkpoints.filter((entry) => entry.weak);
  state.weakFrames = [...new Set(
    weakStops.map((entry) => Number(entry.frame_index)).filter(Number.isInteger),
  )];
  renderWeakFrameMarkers();
  elements.weakStopsPanel.hidden = weakStops.length === 0;
  elements.weakStopsList.replaceChildren();
  for (const entry of weakStops) {
    const item = document.createElement("li");
    item.className = "weak-stop-item";
    const label = document.createElement("span");
    const scorePct = Math.round((entry.score ?? 0) * 100);
    label.textContent = `Phrase ${entry.frame_index + 1} · ${scorePct}% self-check`;
    const action = document.createElement("button");
    action.type = "button";
    action.textContent = "Jump to frame";
    action.addEventListener("click", () => jumpToFrame(entry.frame_index));
    item.append(label, action);
    elements.weakStopsList.append(item);
  }
}

async function refreshReview() {
  if (!state.token) {
    state.reviewCards = [];
    elements.reviewCard.hidden = true;
    elements.reviewStatus.textContent = "Sign in to load your review queue and protect what you checked.";
    elements.reviewTabCount.hidden = true;
    return;
  }
  elements.reviewStatus.textContent = "Loading due cards…";
  try {
    let response = await fetch("/api/review/queue", { headers: authHeaders() });
    let fallbackDocumentId = null;
    if (!response.ok && state.documentId) {
      fallbackDocumentId = state.documentId;
      response = await fetch(`/api/documents/${state.documentId}/flashcards`, {
        headers: authHeaders(),
      });
    }
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    const cards = Array.isArray(payload.flashcards)
      ? payload.flashcards
      : Array.isArray(payload.cards)
        ? payload.cards
        : Array.isArray(payload.queue)
          ? payload.queue
          : [];
    const now = Date.now();
    state.reviewCards = cards
      .filter((card) => !fallbackDocumentId || !card.due_at || Date.parse(card.due_at) <= now)
      .map((card) => ({
        ...card,
        document_id: card.document_id ?? fallbackDocumentId,
      }));
    state.reviewIndex = 0;
    state.reviewRevealed = false;
    state.reviewSessionGraded = 0;
    state.reviewSessionAgain = 0;
    if (elements.reviewSessionSummary) elements.reviewSessionSummary.hidden = true;
    updateReviewCount();
    renderReviewCard();
  } catch (error) {
    state.reviewCards = [];
    elements.reviewCard.hidden = true;
    elements.reviewStatus.textContent = error.message || "The review queue could not be loaded.";
    updateReviewCount();
  }
}

function updateReviewCount() {
  const remaining = Math.max(0, state.reviewCards.length - state.reviewIndex);
  elements.reviewTabCount.textContent = String(remaining);
  elements.reviewTabCount.hidden = remaining === 0;
  elements.reviewTab.disabled = false;
  if (remaining > 0) {
    elements.reviewTab.title = `Review ${remaining} due`;
  } else {
    elements.reviewTab.removeAttribute("title");
  }
}

function formatDueDate(value) {
  if (!value) return "soon";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "soon";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(date);
}

function phraseLocationLabel(frameIndex) {
  if (!Number.isInteger(frameIndex)) return "";
  return `From phrase ${frameIndex + 1} in this document`;
}

function renderReviewCard() {
  elements.reviewActions.replaceChildren();
  const card = state.reviewCards[state.reviewIndex];
  if (!card) {
    elements.reviewCard.hidden = true;
    if (state.reviewSessionGraded > 0 && elements.reviewSessionSummary) {
      elements.reviewSessionSummary.hidden = false;
      elements.reviewSessionSummary.textContent =
        `Session clear. ${state.reviewSessionGraded} card${state.reviewSessionGraded === 1 ? "" : "s"} graded` +
        (state.reviewSessionAgain ? ` · ${state.reviewSessionAgain} marked Again` : "") +
        ". Next review lands on the schedule—not on cramming night.";
      elements.reviewStatus.textContent = "";
    } else {
      elements.reviewStatus.textContent =
        "Nothing due right now. That’s the point of spacing—come back when a card is almost forgettable. Meanwhile, a recall check while reading mints the next cards.";
    }
    updateReviewCount();
    updateAttentionLoop();
    return;
  }
  const remaining = state.reviewCards.length - state.reviewIndex;
  elements.reviewStatus.textContent = `${remaining} card${remaining === 1 ? "" : "s"} remaining`;
  elements.reviewCard.hidden = false;
  elements.reviewDocumentTitle.textContent =
    card.document_title || card.title || "Library document";
  if (elements.reviewSourceLocation) {
    elements.reviewSourceLocation.textContent = phraseLocationLabel(Number(card.frame_index));
  }
  elements.reviewFront.textContent = card.front;
  elements.reviewBack.textContent = card.back;
  elements.reviewBack.hidden = !state.reviewRevealed;
  const returnToPassage = document.createElement("button");
  returnToPassage.type = "button";
  returnToPassage.textContent = "Return to passage";
  returnToPassage.addEventListener("click", () => {
    returnToSourcePassage(card).catch((error) => {
      elements.reviewStatus.textContent = error.message || "The source passage could not be loaded.";
    });
  });
  if (!state.reviewRevealed) {
    const reveal = document.createElement("button");
    reveal.type = "button";
    reveal.textContent = "Reveal answer";
    reveal.className = "primary";
    reveal.addEventListener("click", () => {
      state.reviewRevealed = true;
      announceLive("Answer revealed");
      renderReviewCard();
    });
    elements.reviewActions.append(reveal, returnToPassage);
    return;
  }
  const gotIt = document.createElement("button");
  gotIt.type = "button";
  gotIt.className = "primary review-grade";
  gotIt.innerHTML = "Got it<span>Got it · see later</span>";
  gotIt.addEventListener("click", () => gradeReviewCard(card, "got_it"));
  const again = document.createElement("button");
  again.type = "button";
  again.className = "review-grade";
  again.innerHTML = "Again<span>Again · see sooner</span>";
  again.addEventListener("click", () => gradeReviewCard(card, "again"));
  elements.reviewActions.append(gotIt, again, returnToPassage);
}

async function returnToSourcePassage(card) {
  const documentId = card.document_id;
  const frameIndex = Number(card.frame_index);
  if (!documentId || !Number.isInteger(frameIndex)) {
    elements.reviewStatus.textContent = "This card is missing its source passage.";
    return;
  }
  setView("read");
  await resumeDocument(documentId);
  jumpToFrame(frameIndex);
  if (state.token && state.documentId) {
    fetch("/api/learning-events", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        event_type: "return_to_passage",
        document_id: state.documentId,
        frame_index: frameIndex,
      }),
    }).catch(() => {});
  }
}

async function gradeReviewCard(card, grade) {
  const documentId = card.document_id ?? state.documentId;
  if (!documentId) {
    elements.reviewStatus.textContent = "This card is missing its document reference.";
    return;
  }
  const response = await fetch(`/api/documents/${documentId}/flashcards/${card.id}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ grade }),
  });
  if (!response.ok) {
    elements.reviewStatus.textContent = await apiError(response);
    return;
  }
  const result = await response.json();
  state.reviewSessionGraded += 1;
  if (grade === "again") state.reviewSessionAgain += 1;
  announceLive(
    grade === "again"
      ? `Marked Again. Next due ${formatDueDate(result.due_at)}.`
      : `Marked Got it. Next due ${formatDueDate(result.due_at)}.`,
  );
  state.reviewIndex += 1;
  state.reviewRevealed = false;
  updateReviewCount();
  if (state.reviewIndex >= state.reviewCards.length) {
    await refreshReview();
    await refreshLibrarySummary();
    return;
  }
  renderReviewCard();
  refreshLibrarySummary();
}

async function resumeDocument(documentId) {
  elements.error.hidden = true;
  try {
    const response = await fetch(`/api/documents/${documentId}/resume`, {
      headers: authHeaders(),
    });
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    applyMetadataPayload(payload);
    await refreshReview();
    await refreshWeakStops();
    if (payload.progress) {
      await resumeReading();
    } else {
      await prepareReader();
    }
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  }
}

async function authenticate(mode) {
  clearAuthError();
  const validationError = validateAuthInput();
  if (validationError) {
    showAuthError(validationError);
    return;
  }
  const response = await fetch(`/api/auth/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: elements.authEmail.value.trim(),
      password: elements.authPassword.value,
    }),
  });
  if (!response.ok) {
    showAuthError(await apiError(response));
    return;
  }
  const payload = await response.json();
  state.token = payload.token;
  state.email = payload.email;
  localStorage.setItem("phraseframe_token", payload.token);
  localStorage.setItem("phraseframe_email", payload.email);
  elements.authPassword.value = "";
  renderAccountState();
  await refreshLibrary();
  await refreshReview();
}

function renderAccountState() {
  const signedIn = Boolean(state.token);
  elements.authForm.hidden = signedIn;
  elements.accountStatus.hidden = !signedIn;
  elements.accountEmail.textContent = state.email ?? "";
  elements.signInBanner.hidden = signedIn;
  elements.viewTabs.hidden = !signedIn;
  elements.attentionLoop.hidden = !signedIn && !state.checkpointPhase;
  if (!signedIn && state.activeView === "review") setView("read");
  updateAttentionLoop();
}

function signOut() {
  state.token = null;
  state.email = null;
  state.documentId = null;
  localStorage.removeItem("phraseframe_token");
  localStorage.removeItem("phraseframe_email");
  renderAccountState();
  elements.libraryPanel.hidden = true;
  elements.continueBanner.hidden = true;
  elements.weakStopsPanel.hidden = true;
  state.weakFrames = [];
  renderWeakFrameMarkers();
  refreshReview();
}

async function exportVideo() {
  stop();
  elements.export.disabled = true;
  elements.exportStatus.textContent = "Rendering MP4 locally…";
  try {
    const response = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody()),
    });
    if (!response.ok) throw new Error(await apiError(response));
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "phraseframe.mp4";
    link.click();
    URL.revokeObjectURL(url);
    elements.exportStatus.textContent = "MP4 ready.";
  } catch (error) {
    elements.exportStatus.textContent = error.message;
  } finally {
    elements.export.disabled = false;
  }
}

elements.text.addEventListener("input", () => {
  updateSourceMeta();
  markTimelineStale();
});
elements.wpm.addEventListener("input", () => {
  updatePaceGuidance();
  scheduleProgressSave();
});
elements.chunkSize.addEventListener("change", () => {
  markTimelineStale();
  scheduleProgressSave();
});
elements.stopEveryWords.addEventListener("change", () => {
  markTimelineStale();
  scheduleProgressSave();
});
elements.preview.addEventListener("change", markTimelineStale);
elements.file.addEventListener("change", uploadDocument);
elements.prepare.addEventListener("click", prepareReader);
elements.resume.addEventListener("click", resumeReading);
elements.play.addEventListener("click", togglePlay);
elements.previous.addEventListener("click", () => move(-1));
elements.next.addEventListener("click", () => move(1));
elements.restart.addEventListener("click", () => {
  state.index = 0;
  showFrame();
});
elements.export.addEventListener("click", exportVideo);
elements.fullscreen.addEventListener("click", () => elements.stage.requestFullscreen());
elements.chapterSelect.addEventListener("change", async () => {
  try {
    flushProgressSave();
    await loadChapter(Number(elements.chapterSelect.value));
    await prepareReader();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  }
});
elements.authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await authenticate("login");
  } catch (error) {
    showAuthError(error.message);
  }
});
elements.registerButton.addEventListener("click", async () => {
  try {
    await authenticate("register");
  } catch (error) {
    showAuthError(error.message);
  }
});
elements.logoutButton.addEventListener("click", signOut);
elements.refreshLibrary.addEventListener("click", () => refreshLibrary().catch(() => {}));
elements.refreshReview.addEventListener("click", () => refreshReview().catch(() => {}));
elements.readTab.addEventListener("click", () => setView("read"));
elements.reviewTab.addEventListener("click", () => setView("review"));
elements.viewTabs.addEventListener("keydown", (event) => {
  if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  const showReview = event.key === "ArrowRight" || event.key === "End";
  const tab = showReview ? elements.reviewTab : elements.readTab;
  setView(showReview ? "review" : "read");
  tab.focus();
});
elements.manualCheckpoint.addEventListener("click", () => {
  if (!state.timeline?.frames.length) return;
  stop();
  showCheckpoint();
});
elements.heroStartLoop?.addEventListener("click", () => {
  elements.demoGuide.hidden = false;
  setView("read");
  prepareReader()
    .then(() => {
      elements.stage?.scrollIntoView({ behavior: "smooth", block: "center" });
    })
    .catch(() => {
      elements.stage?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
});
elements.sourcePanelToggle?.addEventListener("click", () => {
  const expanded = elements.sourcePanelToggle.getAttribute("aria-expanded") !== "false";
  elements.sourcePanelToggle.setAttribute("aria-expanded", String(!expanded));
  document.querySelector("#source-panel-body")?.classList.toggle("collapsed", expanded);
});
elements.checkpointContinue.addEventListener("click", async () => {
  if (state.checkpointPhase === "results") {
    hideCheckpoint();
    if (state.timeline && state.index < state.timeline.frames.length - 1) {
      state.index += 1;
    }
    togglePlay();
    return;
  }
  const saved = await submitCheckpoint();
  if (!saved) return;
});
elements.stopCheckpoints.addEventListener("change", () => {
  elements.stopEveryWords.disabled = !elements.stopCheckpoints.checked;
  markTimelineStale();
  scheduleProgressSave();
});
elements.demoGuideDismiss.addEventListener("click", () => {
  localStorage.setItem("phraseframe_demo_guide_dismissed", "1");
  elements.demoGuide.hidden = true;
});
window.addEventListener("resize", fitPhraseOnOneLine);
document.addEventListener("fullscreenchange", () => requestAnimationFrame(fitPhraseOnOneLine));
window.addEventListener("beforeunload", flushProgressSave);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") flushProgressSave();
});
elements.reflection.addEventListener("click", (event) => {
  const adjustment = Number(event.target.dataset.adjust);
  if (Number.isNaN(adjustment)) return;
  elements.wpm.value = String(Math.max(200, Math.min(500, Number(elements.wpm.value) + adjustment)));
  updatePaceGuidance();
  elements.reflection.hidden = true;
});
document.addEventListener("keydown", (event) => {
  if (["TEXTAREA", "INPUT", "SELECT"].includes(document.activeElement.tagName)) return;
  if (event.code === "Space") {
    event.preventDefault();
    togglePlay();
  } else if (event.key === "ArrowLeft") {
    move(-1);
  } else if (event.key === "ArrowRight") {
    move(+1);
  }
});

async function bootstrap() {
  const forceDemoGuide = new URLSearchParams(window.location.search).get("demo") === "1";
  const demoGuideDismissed = localStorage.getItem("phraseframe_demo_guide_dismissed") === "1";
  elements.demoGuide.hidden = demoGuideDismissed && !forceDemoGuide;
  renderAccountState();
  updatePlayControl();
  updatePaceGuidance();
  await refreshLibrary();
  await refreshReview();
  if (state.token && state.libraryHasDocuments) {
    return;
  }
  await prepareReader();
}

bootstrap().catch(() => {});
