HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LFM3-Omni Studio</title>

<style>
:root {
    --bg: #0d1017;
    --panel: #151a24;
    --panel-2: #1b2130;
    --border: #2a3245;
    --text: #eef1f8;
    --muted: #9aa5bd;
    --accent: #6c7cff;
    --accent-2: #8a96ff;
    --ok: #3ecf8e;
    --warn: #f5b942;
    --err: #ff6b6b;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
}

header {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; flex-wrap: wrap;
    padding: 18px 32px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
}
header h1 { margin: 0; font-size: 21px; letter-spacing: .2px; }
header p { margin: 2px 0 0; color: var(--muted); font-size: 13px; }

.badges { display: flex; gap: 8px; flex-wrap: wrap; }
.badge {
    font-size: 12px; padding: 5px 10px; border-radius: 999px;
    background: var(--panel-2); border: 1px solid var(--border); color: var(--muted);
}
.badge.ok { color: var(--ok); border-color: #28634a; }
.badge.bad { color: var(--err); border-color: #6b2c2c; }

.layout {
    max-width: 1280px; margin: 26px auto; padding: 0 20px;
    display: grid; grid-template-columns: minmax(340px, 460px) 1fr; gap: 22px;
}
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }

.panel {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 14px; padding: 22px;
}
.panel h2 { margin: 0 0 14px; font-size: 16px; }

.tabs {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px;
    background: var(--bg); padding: 5px; border-radius: 10px; border: 1px solid var(--border);
}
.tab {
    padding: 10px 4px; border: none; border-radius: 7px; background: transparent;
    color: var(--muted); font-size: 13px; font-weight: 600; cursor: pointer;
}
.tab:hover { background: transparent; color: var(--text); }
.tab.active { background: var(--accent); color: white; }

.field-label { display: block; margin: 18px 0 7px; font-size: 13px; font-weight: 600; color: #d3d9e8; }
select, textarea {
    width: 100%; padding: 11px 12px; font-size: 14px; color: var(--text);
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px; font-family: inherit;
}
select:focus, textarea:focus { outline: none; border-color: var(--accent); }
textarea { min-height: 120px; resize: vertical; }

.row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

/* ---------- DROP ZONE ---------- */
.dropzone {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 6px; text-align: center;
    padding: 26px 16px;
    border: 2px dashed var(--border); border-radius: 12px;
    background: var(--bg); cursor: pointer; transition: border-color .15s, background .15s;
}
.dropzone:hover, .dropzone:focus-visible, .dropzone.drag {
    border-color: var(--accent); background: #10152a; outline: none;
}
.dz-icon {
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: #1d2442; color: var(--accent-2); margin-bottom: 4px;
}
.dz-icon svg { width: 24px; height: 24px; }
.dz-title { font-size: 15px; font-weight: 600; color: var(--text); }
.dz-or { font-size: 12px; color: var(--muted); }
.dz-browse {
    margin: 2px 0 4px; padding: 8px 18px; font-size: 13px;
    background: var(--accent); color: #fff; border-radius: 8px; border: none; font-weight: 700;
    pointer-events: none;   /* click is handled by the whole zone */
}
.chips { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin-top: 4px; }
.chip {
    font-size: 11px; font-weight: 700; letter-spacing: .4px;
    padding: 3px 8px; border-radius: 5px;
    background: var(--panel-2); border: 1px solid var(--border); color: var(--muted);
}
.dz-limit { font-size: 12px; color: var(--muted); margin-top: 4px; }

.filecard {
    border: 1px solid var(--border); border-radius: 12px; background: var(--bg); padding: 12px;
}
.preview img, .preview video {
    max-width: 100%; max-height: 240px; border-radius: 8px; display: block; margin: 0 auto;
}
.preview audio { width: 100%; }
.fileinfo {
    margin-top: 10px; display: flex; justify-content: space-between; align-items: center;
    gap: 10px; font-size: 13px; color: var(--muted);
}
.fileinfo .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.fileinfo .name b { color: var(--text); font-weight: 600; }
.fileinfo button {
    flex-shrink: 0; margin: 0; padding: 6px 12px; font-size: 12px;
    background: #3a1f25; border: 1px solid #6b2c2c; color: var(--err);
}
.fileinfo button:hover { background: #4a2630; }

.check { display: flex; align-items: center; gap: 10px; margin-top: 16px; font-size: 14px; color: #d3d9e8; }
.check input { accent-color: var(--accent); width: 16px; height: 16px; }
.check label { cursor: pointer; }

.hint { margin: 8px 0 0; font-size: 12px; color: var(--muted); }
.hidden { display: none !important; }

.actions { display: flex; gap: 10px; margin-top: 22px; }
button {
    padding: 12px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 700;
    cursor: pointer; color: white; background: var(--accent); transition: .15s;
}
button:hover { background: #5766ee; }
button:disabled { opacity: .5; cursor: not-allowed; }
button.secondary { background: var(--panel-2); border: 1px solid var(--border); color: var(--text); }
button.secondary:hover { background: #232b3e; }
button.danger { background: #3a1f25; border: 1px solid #6b2c2c; color: var(--err); }
button.danger:hover { background: #4a2630; }
button.primary { flex: 1; }

.statusbar {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    font-size: 13px; color: var(--muted); margin-bottom: 12px;
}
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--muted); }
.dot.running { background: var(--accent); animation: pulse 1s infinite; }
.dot.done { background: var(--ok); }
.dot.error { background: var(--err); }
@keyframes pulse { 50% { opacity: .3; } }

.progress { height: 4px; background: var(--border); border-radius: 4px; overflow: hidden; margin-bottom: 14px; }
.progress div { height: 100%; width: 0; background: var(--accent); transition: width .3s; }
.progress.indeterminate div { width: 35%; animation: slide 1.2s infinite ease-in-out; }
@keyframes slide { 0% { margin-left: -35%; } 100% { margin-left: 100%; } }

.result {
    background: var(--bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 18px; min-height: 280px; max-height: 62vh; overflow-y: auto;
    white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.75; font-size: 15px;
}
.result.placeholder { color: var(--muted); }
.result.streaming::after { content: "▍"; color: var(--accent-2); animation: pulse 1s infinite; }
.result.error { color: var(--err); }

.metrics { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.metric { font-size: 12px; padding: 5px 10px; border-radius: 6px; background: var(--panel-2); color: var(--muted); }
.notice {
    margin-top: 12px; padding: 10px 14px; border-radius: 8px; font-size: 13px;
    background: #2e2614; border: 1px solid #6b5520; color: var(--warn);
}
.notice.info { background: #14233a; border-color: #2a4a7a; color: #8db8ff; }

.toolbar { display: flex; gap: 8px; margin-top: 14px; }
.toolbar button { padding: 8px 14px; font-size: 13px; }

.history { margin-top: 22px; }
.history h3 { font-size: 14px; margin: 0 0 10px; color: var(--muted); }
.history-item {
    padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg);
    margin-bottom: 8px; cursor: pointer; font-size: 13px;
}
.history-item:hover { border-color: var(--accent); }
.history-item small { color: var(--muted); display: block; margin-top: 3px; }

.footer { text-align: center; padding: 22px; color: #6f7a92; font-size: 12px; }
</style>
</head>

<body>

<header>
    <div>
        <h1>LFM3-Omni Studio</h1>
        <p>Multimodal AI: text, image, audio and video understanding</p>
    </div>
    <div class="badges">
        <span class="badge" id="bModel">Model: checking...</span>
        <span class="badge" id="bDevice">Device: -</span>
        <span class="badge" id="bQueue">Queue: -</span>
    </div>
</header>

<div class="layout">

    <!-- ============ INPUT PANEL ============ -->
    <section class="panel">
        <h2>Input</h2>

        <div class="tabs" id="tabs">
            <button class="tab active" data-mode="text">Text</button>
            <button class="tab" data-mode="image">Image</button>
            <button class="tab" data-mode="audio">Audio</button>
            <button class="tab" data-mode="video">Video</button>
        </div>

        <div id="fileSection" class="hidden">
            <span class="field-label" id="uploadLabel">Upload file</span>

            <!-- Empty state: drop zone -->
            <div class="dropzone" id="drop" tabindex="0" role="button" aria-label="Choose a file to upload">
                <input type="file" id="file" class="hidden">
                <div class="dz-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                </div>
                <div class="dz-title" id="dzTitle">Drag and drop your file here</div>
                <div class="dz-or">or</div>
                <span class="dz-browse">Browse files</span>
                <div class="chips" id="chips"></div>
                <div class="dz-limit">Maximum file size: 50 MB</div>
            </div>

            <!-- Selected state: file card -->
            <div class="filecard hidden" id="fileCard">
                <div class="preview" id="preview"></div>
                <div class="fileinfo">
                    <span class="name" id="fileInfoText"></span>
                    <button type="button" id="removeFile">Remove</button>
                </div>
            </div>
        </div>

        <div id="languageSection" class="hidden">
            <label class="field-label" for="language">Audio language (transcription)</label>
            <select id="language">
                <option>English</option><option>Arabic</option><option>Chinese</option>
                <option>French</option><option>German</option><option>Hindi</option>
                <option>Japanese</option><option>Korean</option><option>Spanish</option>
                <option>Urdu</option>
            </select>
            <p class="hint">Leave the prompt empty to transcribe. Long audio is processed in 30 second parts. Urdu is not an officially supported language.</p>
        </div>

        <div id="videoSection" class="hidden">
            <div class="check">
                <input type="checkbox" id="includeAudio">
                <label for="includeAudio">Also analyze the video soundtrack (slower)</label>
            </div>
            <p class="hint">Videos are automatically shortened and downscaled on the server for speed. Short clips work best.</p>
        </div>

        <label class="field-label" for="question" id="questionLabel">Your prompt</label>
        <textarea id="question" placeholder="Ask something..."></textarea>

        <div class="row">
            <div>
                <label class="field-label" for="maxTokens">Maximum answer length</label>
                <select id="maxTokens">
                    <option value="256">Short (256 tokens)</option>
                    <option value="512">Medium (512 tokens)</option>
                    <option value="1024" selected>Long (1024 tokens)</option>
                    <option value="2048">Very long (2048 tokens)</option>
                    <option value="4096">Maximum (4096 tokens)</option>
                </select>
            </div>
            <div></div>
        </div>

        <div class="actions">
            <button class="primary" id="analyzeBtn">Analyze</button>
            <button class="danger hidden" id="cancelBtn">Cancel</button>
        </div>
    </section>

    <!-- ============ OUTPUT PANEL ============ -->
    <section class="panel">
        <h2>Response</h2>

        <div class="statusbar">
            <span class="dot" id="dot"></span>
            <span id="statusText">Ready</span>
            <span id="timerText"></span>
        </div>

        <div class="progress" id="progress"><div id="progressBar"></div></div>

        <div class="result placeholder" id="result">Your model response will appear here and stream in live.</div>

        <div id="notices"></div>
        <div class="metrics" id="metrics"></div>

        <div class="toolbar">
            <button class="secondary" id="copyBtn" disabled>Copy</button>
            <button class="secondary" id="downloadBtn" disabled>Download .txt</button>
            <button class="secondary" id="clearBtn">Clear</button>
        </div>

        <div class="history hidden" id="historyBox">
            <h3>Recent results</h3>
            <div id="historyList"></div>
        </div>
    </section>

</div>

<div class="footer">Powered by Liquid AI LFM3-Omni-2B</div>

<script>
(function () {

const $ = (id) => document.getElementById(id);

const state = {
    mode: "text",
    file: null,
    previewUrl: null,
    jobId: null,
    polling: false,
    timer: null,
    startTime: 0,
    lastText: "",
    history: []
};

const MAX_FILE = 50 * 1024 * 1024;

const cfg = {
    text:  { placeholder: "Example: Explain what multimodal AI means.", label: "Your prompt" },
    image: { noun: "image", upload: "Upload image",
             accept: ".jpg,.jpeg,.png,.webp", exts: [".jpg", ".jpeg", ".png", ".webp"],
             placeholder: "Example: Describe everything you can see in this image.",
             label: "Your question (optional)" },
    audio: { noun: "audio file", upload: "Upload audio",
             accept: ".mp3,.wav,.m4a,.flac,.ogg", exts: [".mp3", ".wav", ".m4a", ".flac", ".ogg"],
             placeholder: "Leave empty to transcribe, or ask a question about the audio.",
             label: "Question (optional, empty = transcription)" },
    video: { noun: "video", upload: "Upload video",
             accept: ".mp4,.mov,.mkv,.avi,.webm", exts: [".mp4", ".mov", ".mkv", ".avi", ".webm"],
             placeholder: "Example: Describe what happens in this video.",
             label: "Your question (optional)" }
};

// ---------- helpers ----------
function fmtTime(sec) {
    sec = Math.floor(sec);
    const m = Math.floor(sec / 60), s = sec % 60;
    return m > 0 ? m + "m " + s + "s" : s + "s";
}
function setDot(cls) { $("dot").className = "dot " + (cls || ""); }
function setResult(text, cls) {
    const r = $("result");
    r.textContent = text;
    r.className = "result" + (cls ? " " + cls : "");
    r.scrollTop = r.scrollHeight;
}
function addNotice(text, kind) {
    const d = document.createElement("div");
    d.className = "notice" + (kind === "info" ? " info" : "");
    d.textContent = text;
    $("notices").appendChild(d);
}
function setMetrics(items) {
    const box = $("metrics");
    box.innerHTML = "";
    items.forEach((t) => {
        const s = document.createElement("span");
        s.className = "metric";
        s.textContent = t;
        box.appendChild(s);
    });
}

// ---------- health ----------
async function refreshHealth() {
    try {
        const r = await fetch("/health", { cache: "no-store" });
        const h = await r.json();
        const m = $("bModel");
        m.textContent = h.model_loaded ? "Model ready" : "Model loading...";
        m.className = "badge " + (h.model_loaded ? "ok" : "");
        $("bDevice").textContent = h.device.toUpperCase() + " | " + h.dtype + " | " + h.threads + " threads";
        $("bQueue").textContent = "Active jobs: " + h.active_jobs;
    } catch (e) {
        const m = $("bModel");
        m.textContent = "Server unreachable";
        m.className = "badge bad";
    }
}
refreshHealth();
setInterval(refreshHealth, 10000);

// ---------- drop zone rendering ----------
function renderDropzone() {
    const c = cfg[state.mode];
    if (!c || !c.exts) return;

    $("uploadLabel").textContent = c.upload;
    $("dzTitle").textContent = "Drag and drop your " + c.noun + " here";
    $("file").accept = c.accept;

    const chips = $("chips");
    chips.innerHTML = "";
    c.exts.forEach((e) => {
        const s = document.createElement("span");
        s.className = "chip";
        s.textContent = e.replace(".", "").toUpperCase();
        chips.appendChild(s);
    });
}

// ---------- mode switching ----------
function setMode(mode) {
    state.mode = mode;
    document.querySelectorAll(".tab").forEach((t) =>
        t.classList.toggle("active", t.dataset.mode === mode));

    clearFile();

    // The prompt belongs to the tab it was written in: reset it on every switch.
    $("question").value = "";

    $("fileSection").classList.toggle("hidden", mode === "text");
    $("languageSection").classList.toggle("hidden", mode !== "audio");
    $("videoSection").classList.toggle("hidden", mode !== "video");

    $("question").placeholder = cfg[mode].placeholder;
    $("questionLabel").textContent = cfg[mode].label;
    renderDropzone();
}
document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => {
        if (state.polling || t.dataset.mode === state.mode) return;
        setMode(t.dataset.mode);
    }));

// ---------- file handling ----------
function clearFile() {
    state.file = null;
    $("file").value = "";
    if (state.previewUrl) { URL.revokeObjectURL(state.previewUrl); state.previewUrl = null; }
    $("preview").innerHTML = "";
    $("fileCard").classList.add("hidden");
    $("drop").classList.remove("hidden");
}

function setFile(f) {
    const ext = "." + f.name.toLowerCase().split(".").pop();
    if (!cfg[state.mode].exts.includes(ext)) {
        alert("Unsupported file format for " + state.mode + " mode.\nAllowed: " +
              cfg[state.mode].exts.join(", "));
        $("file").value = "";
        return;
    }
    if (f.size > MAX_FILE) {
        alert("File is too large. Maximum size is 50 MB.");
        $("file").value = "";
        return;
    }

    if (state.previewUrl) URL.revokeObjectURL(state.previewUrl);
    $("preview").innerHTML = "";
    state.file = f;
    state.previewUrl = URL.createObjectURL(f);

    let el = null;
    if (state.mode === "image") { el = document.createElement("img"); el.alt = f.name; }
    else if (state.mode === "audio") { el = document.createElement("audio"); el.controls = true; }
    else if (state.mode === "video") { el = document.createElement("video"); el.controls = true; el.muted = true; }
    if (el) { el.src = state.previewUrl; $("preview").appendChild(el); }

    const info = $("fileInfoText");
    info.innerHTML = "";
    const b = document.createElement("b");
    b.textContent = f.name;
    info.appendChild(b);
    info.appendChild(document.createTextNode("  |  " + (f.size / 1048576).toFixed(2) + " MB"));
    info.title = f.name;

    $("drop").classList.add("hidden");
    $("fileCard").classList.remove("hidden");
}

const drop = $("drop");
drop.addEventListener("click", () => { if (!state.polling) $("file").click(); });
drop.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("file").click(); }
});
$("file").addEventListener("change", () => { if ($("file").files[0]) setFile($("file").files[0]); });
$("removeFile").addEventListener("click", () => { if (!state.polling) clearFile(); });

["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => {
    e.preventDefault(); drop.classList.add("drag");
}));
["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => {
    e.preventDefault(); drop.classList.remove("drag");
}));
drop.addEventListener("drop", (e) => {
    if (!state.polling && e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
});

// Stop the browser from opening a file that is dropped outside the drop zone.
["dragover", "drop"].forEach((ev) => window.addEventListener(ev, (e) => e.preventDefault()));

// ---------- busy state ----------
function setBusy(busy) {
    state.polling = busy;
    $("analyzeBtn").disabled = busy;
    $("analyzeBtn").textContent = busy ? "Processing..." : "Analyze";
    $("cancelBtn").classList.toggle("hidden", !busy);
    document.querySelectorAll(".tab").forEach((t) => (t.disabled = busy));
    $("removeFile").disabled = busy;
}

function startTimer() {
    state.startTime = Date.now();
    state.timer = setInterval(() => {
        $("timerText").textContent = fmtTime((Date.now() - state.startTime) / 1000);
    }, 500);
}
function stopTimer() {
    if (state.timer) clearInterval(state.timer);
    state.timer = null;
}

function setProgress(mode, pct) {
    const p = $("progress");
    p.classList.toggle("indeterminate", mode === "indeterminate");
    $("progressBar").style.width = mode === "indeterminate" ? "" : (pct || 0) + "%";
}

// ---------- submit (XHR for upload progress) ----------
function submitJob(formData) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/jobs");
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                $("statusText").textContent = "Uploading file... " + pct + "%";
                setProgress("determinate", pct);
            }
        };
        xhr.onload = () => {
            let data = null;
            try { data = JSON.parse(xhr.responseText); } catch (e) {}
            if (xhr.status >= 200 && xhr.status < 300 && data && data.job_id) resolve(data.job_id);
            else reject(new Error((data && data.detail) || "Server error (HTTP " + xhr.status + ")."));
        };
        xhr.onerror = () => reject(new Error("Network error while uploading."));
        xhr.send(formData);
    });
}

// ---------- polling ----------
async function pollJob(jobId) {
    let failures = 0;
    while (state.polling && state.jobId === jobId) {
        try {
            const r = await fetch("/api/jobs/" + jobId, { cache: "no-store" });
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                throw new Error(err.detail || "HTTP " + r.status);
            }
            const j = await r.json();
            failures = 0;

            if (j.status === "queued") {
                $("statusText").textContent = j.queue_position > 0
                    ? "Queued: " + j.queue_position + " job(s) ahead"
                    : "Starting...";
                setDot("running");
                setProgress("indeterminate");
            } else if (j.status === "running") {
                $("statusText").textContent = j.stage;
                setDot("running");
                setProgress("indeterminate");
                if (j.text) {
                    setResult(j.text, "streaming");
                    state.lastText = j.text;
                }
                if (j.tokens) {
                    setMetrics([j.tokens + " tokens", j.tokens_per_second + " tokens/s"]);
                }
            } else {
                return j;
            }
        } catch (e) {
            failures++;
            if (failures >= 6) throw new Error("Lost connection to the server: " + e.message);
        }
        await new Promise((res) => setTimeout(res, 700));
    }
    return null;
}

// ---------- analyze ----------
async function analyze() {
    const prompt = $("question").value.trim();

    if (state.mode !== "text" && !state.file) { alert("Please upload a file first."); return; }
    if (state.mode === "text" && !prompt) { alert("Please enter some text or a question."); return; }

    const fd = new FormData();
    fd.append("mode", state.mode);
    fd.append("question", prompt);
    fd.append("max_new_tokens", $("maxTokens").value);
    if (state.mode !== "text") fd.append("file", state.file);
    if (state.mode === "audio") fd.append("language", $("language").value);
    if (state.mode === "video") fd.append("include_audio", $("includeAudio").checked ? "true" : "false");

    $("notices").innerHTML = "";
    setMetrics([]);
    $("copyBtn").disabled = true;
    $("downloadBtn").disabled = true;
    setResult("Working on it...", "placeholder");
    $("timerText").textContent = "";
    state.lastText = "";

    setBusy(true);
    setDot("running");
    $("statusText").textContent = "Submitting...";
    setProgress("indeterminate");
    startTimer();

    try {
        const jobId = await submitJob(fd);
        state.jobId = jobId;
        const job = await pollJob(jobId);
        if (!job) return;

        stopTimer();
        $("timerText").textContent = "Total: " + fmtTime(job.elapsed);

        (job.notes || []).forEach((n) => addNotice(n, "info"));

        if (job.status === "done") {
            setDot("done");
            $("statusText").textContent = "Completed";
            setProgress("determinate", 100);
            setResult(job.text);
            state.lastText = job.text;
            $("copyBtn").disabled = false;
            $("downloadBtn").disabled = false;
            setMetrics([job.tokens + " tokens", job.tokens_per_second + " tokens/s", "Time " + fmtTime(job.elapsed)]);
            if (job.truncated) {
                addNotice("The answer reached the maximum length and may be cut off. Increase 'Maximum answer length' and run again.", "warn");
            }
            addHistory(job, prompt);
        } else if (job.status === "cancelled") {
            setDot("");
            $("statusText").textContent = "Cancelled";
            setProgress("determinate", 0);
            setResult(job.text || "Cancelled.", job.text ? "" : "placeholder");
            if (job.text) { $("copyBtn").disabled = false; $("downloadBtn").disabled = false; }
        } else {
            throw new Error(job.error || "Processing failed.");
        }
    } catch (e) {
        stopTimer();
        setDot("error");
        $("statusText").textContent = "Failed";
        setProgress("determinate", 0);
        setResult("Error: " + e.message, "error");
        console.error(e);
    } finally {
        setBusy(false);
    }
}

$("analyzeBtn").addEventListener("click", analyze);
$("cancelBtn").addEventListener("click", async () => {
    if (!state.jobId) return;
    $("statusText").textContent = "Cancelling...";
    try { await fetch("/api/jobs/" + state.jobId, { method: "DELETE" }); } catch (e) {}
});

// ---------- toolbar ----------
$("copyBtn").addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(state.lastText);
        $("copyBtn").textContent = "Copied";
    } catch (e) {
        $("copyBtn").textContent = "Copy failed";
    }
    setTimeout(() => ($("copyBtn").textContent = "Copy"), 1500);
});
$("downloadBtn").addEventListener("click", () => {
    const blob = new Blob([state.lastText], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "lfm3-omni-" + state.mode + "-result.txt";
    a.click();
    URL.revokeObjectURL(a.href);
});
$("clearBtn").addEventListener("click", () => {
    if (state.polling) return;
    $("question").value = "";
    $("notices").innerHTML = "";
    setMetrics([]);
    setDot("");
    $("statusText").textContent = "Ready";
    $("timerText").textContent = "";
    setProgress("determinate", 0);
    setResult("Your model response will appear here and stream in live.", "placeholder");
    $("copyBtn").disabled = true;
    $("downloadBtn").disabled = true;
    state.lastText = "";
});

// ---------- history ----------
function addHistory(job, prompt) {
    state.history.unshift({
        mode: state.mode,
        prompt: prompt || "(no prompt)",
        text: job.text,
        time: new Date().toLocaleTimeString()
    });
    state.history = state.history.slice(0, 15);
    renderHistory();
}
function renderHistory() {
    const list = $("historyList");
    list.innerHTML = "";
    $("historyBox").classList.toggle("hidden", state.history.length === 0);
    state.history.forEach((h) => {
        const d = document.createElement("div");
        d.className = "history-item";
        const t = document.createElement("div");
        t.textContent = h.mode.toUpperCase() + ": " + h.prompt.slice(0, 80);
        const s = document.createElement("small");
        s.textContent = h.time + " | " + h.text.slice(0, 90).replace(/\s+/g, " ");
        d.appendChild(t);
        d.appendChild(s);
        d.addEventListener("click", () => {
            if (state.polling) return;
            setResult(h.text);
            state.lastText = h.text;
            $("copyBtn").disabled = false;
            $("downloadBtn").disabled = false;
        });
        list.appendChild(d);
    });
}

// ---------- ctrl+enter ----------
$("question").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !state.polling) analyze();
});

setMode("text");

})();
</script>

</body>
</html>
"""