const elements = {
  text: document.querySelector("#source-text"),
  file: document.querySelector("#file-input"),
  words: document.querySelector("#word-count"),
  estimate: document.querySelector("#duration-estimate"),
  error: document.querySelector("#source-error"),
  wpm: document.querySelector("#wpm"),
  wpmOutput: document.querySelector("#wpm-output"),
  guidance: document.querySelector("#speed-guidance"),
  chunkSize: document.querySelector("#chunk-size"),
  preview: document.querySelector("#preview-minute"),
  prepare: document.querySelector("#prepare-button"),
  stage: document.querySelector("#reader-stage"),
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
};

const state = {
  timeline: null,
  index: 0,
  playing: false,
  timer: null,
};

function countWords(text) {
  return (text.match(/[\p{L}\p{N}]+(?:[’'-][\p{L}\p{N}]+)*/gu) || []).length;
}

function formatTime(milliseconds) {
  const totalSeconds = Math.round(milliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  return `${minutes}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

function requestBody() {
  const targetWords = Number(elements.chunkSize.value);
  return {
    text: elements.text.value,
    wpm: Number(elements.wpm.value),
    target_words: targetWords,
    max_words: Math.min(targetWords + 2, 10),
    max_characters: 42,
    preview_seconds: elements.preview.checked ? 60 : null,
  };
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
    return typeof body.detail === "string" ? body.detail : "The request could not be completed.";
  } catch {
    return "The request could not be completed.";
  }
}

function stop() {
  state.playing = false;
  clearTimeout(state.timer);
  state.timer = null;
  elements.play.textContent = "▶";
}

function fitPhraseOnOneLine() {
  elements.phrase.style.removeProperty("font-size");
  const preferredSize = Number.parseFloat(getComputedStyle(elements.phrase).fontSize);
  const availableWidth = elements.phrase.clientWidth;
  const requiredWidth = elements.phrase.scrollWidth;
  if (requiredWidth > availableWidth) {
    const fittedSize = Math.max(12, Math.floor(preferredSize * availableWidth / requiredWidth));
    elements.phrase.style.fontSize = `${fittedSize}px`;
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
  elements.progress.style.width = `${((state.index + 1) / timeline.frames.length) * 100}%`;
  if (state.playing) {
    clearTimeout(state.timer);
    state.timer = setTimeout(() => {
      if (state.index >= timeline.frames.length - 1) {
        stop();
        elements.reflection.hidden = false;
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
    showFrame();
  } else {
    clearTimeout(state.timer);
  }
}

function move(delta) {
  if (!state.timeline?.frames.length) return;
  state.index = Math.max(0, Math.min(state.timeline.frames.length - 1, state.index + delta));
  showFrame();
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
    elements.reflection.hidden = true;
    showFrame();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.prepare.disabled = false;
    elements.prepare.textContent = "Prepare reader";
  }
}

async function uploadText() {
  const selected = elements.file.files[0];
  if (!selected) return;
  elements.error.hidden = true;
  const data = new FormData();
  data.append("file", selected);
  try {
    const response = await fetch("/api/extract", { method: "POST", body: data });
    if (!response.ok) throw new Error(await apiError(response));
    const payload = await response.json();
    elements.text.value = payload.text;
    updateSourceMeta();
    await prepareReader();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.file.value = "";
  }
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
elements.file.addEventListener("change", uploadText);
elements.prepare.addEventListener("click", prepareReader);
elements.play.addEventListener("click", togglePlay);
elements.previous.addEventListener("click", () => move(-1));
elements.next.addEventListener("click", () => move(1));
elements.restart.addEventListener("click", () => {
  state.index = 0;
  showFrame();
});
elements.export.addEventListener("click", exportVideo);
elements.fullscreen.addEventListener("click", () => elements.stage.requestFullscreen());
window.addEventListener("resize", fitPhraseOnOneLine);
document.addEventListener("fullscreenchange", () => requestAnimationFrame(fitPhraseOnOneLine));
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
    move(1);
  }
});

updatePaceGuidance();
prepareReader();
