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
};

const state = {
  timeline: null,
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
  lastSavedFrame: -1,
  lastCheckpointFrame: 0,
  activeCheckpointId: null,
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
    elements.guidance.textContent = "Reflective pacing for dense or unfamiliar material.";
  } else if (wpm <= 350) {
    elements.guidance.textContent = "A balanced range for clear prose. Check your recall.";
  } else {
    elements.guidance.textContent = "At this pace, studies often find lower comprehension. Use it for a first pass, not deep study.";
  }
  updateSourceMeta();
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
  elements.play.textContent = "▶";
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

function checkpointSnippet() {
  const timeline = state.timeline;
  if (!timeline?.frames.length) return "";
  const start = Math.max(0, state.lastCheckpointFrame);
  const end = Math.min(state.index + 1, timeline.frames.length);
  return timeline.frames
    .slice(start, end)
    .map((frame) => frame.text)
    .join(" ");
}

function hideCheckpoint() {
  elements.checkpoint.hidden = true;
  elements.checkpointQuestions.replaceChildren();
  state.activeCheckpointId = null;
}

async function showCheckpoint() {
  if (!state.documentId || !state.token) {
    elements.reflection.hidden = false;
    return;
  }
  elements.reflection.hidden = true;
  elements.checkpoint.hidden = false;
  elements.checkpointQuestions.textContent = "Preparing questions…";
  try {
    const response = await fetch(`/api/documents/${state.documentId}/checkpoints`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        frame_index: state.index,
        snippet: checkpointSnippet(),
      }),
    });
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    state.activeCheckpointId = payload.checkpoint_id;
    elements.checkpointQuestions.replaceChildren();
    for (const question of payload.questions) {
      const label = document.createElement("label");
      label.className = "checkpoint-question";
      const prompt = document.createElement("span");
      prompt.textContent = question.text;
      const input = document.createElement("textarea");
      input.rows = 2;
      input.dataset.questionId = question.id;
      input.setAttribute("aria-label", question.text);
      label.append(prompt, input);
      elements.checkpointQuestions.append(label);
    }
  } catch (error) {
    elements.checkpointQuestions.textContent = error.message;
  }
}

async function submitCheckpoint() {
  if (!state.activeCheckpointId) {
    hideCheckpoint();
    return;
  }
  const answers = [...elements.checkpointQuestions.querySelectorAll("textarea")].map(
    (input) => input.value.trim(),
  );
  await fetch(`/api/documents/${state.documentId}/checkpoints`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      frame_index: state.index,
      snippet: checkpointSnippet(),
      checkpoint_id: state.activeCheckpointId,
      answers,
    }),
  });
  state.lastCheckpointFrame = state.index + 1;
  hideCheckpoint();
}

function isStopFrame() {
  const stops = state.timeline?.stop_frames ?? [];
  return stops.includes(state.index);
}

function showFrame() {
  const timeline = state.timeline;
  if (!timeline?.frames.length) return;
  const frame = timeline.frames[state.index];
  elements.phrase.textContent = frame.text;
  fitPhraseOnOneLine();
  elements.frameCounter.textContent = `${state.index + 1} / ${timeline.frames.length}`;
  elements.timeCounter.textContent = `${formatTime(frame.starts_at_ms)} / ${formatTime(timeline.duration_ms)}`;
  elements.progress.style.width = `${((state.index + 1) / timeline.frames.length) * 100}%`;
  scheduleProgressSave();
  if (state.playing) {
    clearTimeout(state.timer);
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

function togglePlay() {
  if (!state.timeline?.frames.length) return;
  state.playing = !state.playing;
  elements.play.textContent = state.playing ? "Ⅱ" : "▶";
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
  return {
    chapter_index: state.chapterIndex,
    frame_index: state.index,
    wpm: Number(elements.wpm.value),
    target_words: Number(elements.chunkSize.value),
  };
}

async function saveProgressNow() {
  if (!state.token || !state.documentId || !state.timeline?.frames.length) return;
  if (state.index === state.lastSavedFrame) return;

  const response = await fetch(`/api/documents/${state.documentId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(progressPayload()),
    keepalive: true,
  });
  if (!response.ok) throw new Error(await apiError(response));
  state.lastSavedFrame = state.index;
  await refreshLibrary();
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
  state.lastSavedFrame = -1;
  state.lastCheckpointFrame = 0;
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
    state.timeline = await response.json();
    state.index = 0;
    state.lastSavedFrame = -1;
    state.lastCheckpointFrame = 0;
    elements.reflection.hidden = true;
    hideCheckpoint();
    showFrame();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.prepare.disabled = false;
    elements.prepare.textContent = "Prepare reader";
  }
}

async function resumeReading() {
  if (!state.pendingProgress) return;
  elements.wpm.value = String(state.pendingProgress.wpm);
  elements.chunkSize.value = String(state.pendingProgress.target_words);
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
      await loadChapter(payload.chapter_index ?? 0);
      await refreshLibrary();
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
    return;
  }
  const response = await fetch("/api/documents", { headers: authHeaders() });
  if (!response.ok) {
    elements.libraryPanel.hidden = true;
    return;
  }
  const payload = await response.json();
  elements.libraryPanel.hidden = false;
  elements.libraryList.replaceChildren();
  for (const entry of payload.documents) {
    const item = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = `${entry.title} · ${entry.format.toUpperCase()}`;
    const action = document.createElement("button");
    action.type = "button";
    action.textContent = entry.has_progress ? "Continue" : "Open";
    action.addEventListener("click", () => resumeDocument(entry.id));
    item.append(label, action);
    elements.libraryList.append(item);
  }
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
}

function renderAccountState() {
  const signedIn = Boolean(state.token);
  elements.authForm.hidden = signedIn;
  elements.accountStatus.hidden = !signedIn;
  elements.accountEmail.textContent = state.email ?? "";
  elements.signInBanner.hidden = signedIn;
}

function signOut() {
  state.token = null;
  state.email = null;
  state.documentId = null;
  localStorage.removeItem("phraseframe_token");
  localStorage.removeItem("phraseframe_email");
  renderAccountState();
  elements.libraryPanel.hidden = true;
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

elements.text.addEventListener("input", updateSourceMeta);
elements.wpm.addEventListener("input", updatePaceGuidance);
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
elements.checkpointContinue.addEventListener("click", async () => {
  await submitCheckpoint();
  if (state.timeline && state.index < state.timeline.frames.length - 1) {
    state.index += 1;
  }
  togglePlay();
});
elements.stopCheckpoints.addEventListener("change", () => {
  elements.stopEveryWords.disabled = !elements.stopCheckpoints.checked;
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

renderAccountState();
updatePaceGuidance();
refreshLibrary().catch(() => {});
prepareReader();
