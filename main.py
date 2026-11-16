import os
import time
import uuid
import shutil
import logging
import tempfile
import threading
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import torch
import numpy as np
import soundfile as sf
import librosa
from PIL import Image, ImageOps

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from transformers import AutoModelForMultimodalLM, AutoProcessor

from ui import HTML_PAGE


# ============================================================
# CONFIGURATION (override with environment variables)
# ============================================================

MODEL_ID = os.getenv("MODEL_ID", "LiquidAI/LFM3-Omni-2B")
DEVICE = os.getenv("DEVICE", "cpu")

# float32 is safest. bfloat16 is faster only on CPUs with AVX512-BF16 / AMX.
DTYPE_NAME = os.getenv("DTYPE", "float32")
DTYPE = {"float32": torch.float32, "bfloat16": torch.bfloat16,
         "float16": torch.float16}.get(DTYPE_NAME, torch.float32)

NUM_THREADS = int(os.getenv("NUM_THREADS", str(os.cpu_count() or 4)))

MAX_FILE_SIZE = 50 * 1024 * 1024          # 50 MB upload limit
DEFAULT_MAX_NEW_TOKENS = 1024
HARD_MAX_NEW_TOKENS = 4096

# Speed controls: smaller input = far fewer tokens = much faster on CPU
IMAGE_MAX_SIDE = int(os.getenv("IMAGE_MAX_SIDE", "768"))
VIDEO_MAX_SIDE = int(os.getenv("VIDEO_MAX_SIDE", "448"))
VIDEO_FPS = float(os.getenv("VIDEO_FPS", "1"))
MAX_VIDEO_FRAMES = int(os.getenv("MAX_VIDEO_FRAMES", "16"))
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SECONDS = int(os.getenv("AUDIO_CHUNK_SECONDS", "30"))
AUDIO_MAX_SECONDS = int(os.getenv("AUDIO_MAX_SECONDS", "600"))   # transcription cap
AUDIO_QA_MAX_SECONDS = int(os.getenv("AUDIO_QA_MAX_SECONDS", "120"))

MAX_QUEUE = int(os.getenv("MAX_QUEUE", "5"))
JOB_TTL_SECONDS = 3600

ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".webp"},
    "audio": {".wav", ".mp3", ".m4a", ".flac", ".ogg"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("LFM3-Omni")


# ============================================================
# GLOBALS
# ============================================================

model = None
processor = None

# One worker: CPU inference is already multi-threaded, parallel jobs only slow each other.
executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="inference")

jobs: dict[str, "Job"] = {}
jobs_lock = threading.Lock()


class JobCancelled(Exception):
    pass


@dataclass
class Job:
    id: str
    mode: str
    status: str = "queued"            # queued | running | done | error | cancelled
    stage: str = "Waiting in queue"
    text: str = ""
    error: Optional[str] = None
    truncated: bool = False
    tokens: int = 0
    created: float = field(default_factory=time.time)
    started: Optional[float] = None
    finished: Optional[float] = None
    notes: list = field(default_factory=list)
    cancel_event: threading.Event = field(default_factory=threading.Event)

    def check_cancel(self):
        if self.cancel_event.is_set():
            raise JobCancelled()


# ============================================================
# FFMPEG HELPERS
# ============================================================

def get_ffmpeg() -> Optional[str]:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


FFMPEG = None


def run_ffmpeg(args: list[str], timeout: int = 180):
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed")


# ============================================================
# MODEL LOADING
# ============================================================

def load_model():
    global model, processor, FFMPEG

    FFMPEG = get_ffmpeg()
    logger.info("ffmpeg: %s", FFMPEG or "NOT FOUND (video/audio preprocessing limited)")

    torch.set_num_threads(NUM_THREADS)
    logger.info("Loading %s on %s (%s, %d threads)...",
                MODEL_ID, DEVICE, DTYPE_NAME, NUM_THREADS)

    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        max_frames=MAX_VIDEO_FRAMES,
    )

    model = AutoModelForMultimodalLM.from_pretrained(
        MODEL_ID,
        dtype=DTYPE,
        device_map=DEVICE,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    ).eval()

    logger.info("Model loaded. Running warm-up...")
    try:
        t0 = time.time()
        conversation = [
            {"role": "system", "content": "Respond in text."},
            {"role": "user", "content": "Hi"},
        ]
        _generate(conversation, None, max_new_tokens=4)
        logger.info("Warm-up finished in %.1fs", time.time() - t0)
    except Exception:
        logger.exception("Warm-up failed (non fatal)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield
    executor.shutdown(wait=False, cancel_futures=True)
    logger.info("Shutting down.")


app = FastAPI(title="LFM3-Omni Multimodal AI", version="2.0.0", lifespan=lifespan)


# ============================================================
# GENERATION (with live token streaming)
# ============================================================

class JobStreamer:
    """Receives tokens from model.generate and pushes partial text to the job."""

    def __init__(self, job: Job, prompt_len: int, prefix: str):
        self.job = job
        self.prompt_len = prompt_len
        self.prefix = prefix
        self.ids: list[int] = []
        self.first = True

    def put(self, value):
        if self.job is None:
            return
        self.job.check_cancel()                      # lets "Cancel" abort mid-generation

        ids = value.reshape(-1).tolist() if hasattr(value, "reshape") else list(value)
        if self.first:
            self.first = False
            if len(ids) == self.prompt_len:          # first call carries the prompt
                return
        self.ids.extend(ids)
        text = processor.decode(self.ids, skip_special_tokens=True)
        self.job.text = self.prefix + text
        self.job.tokens = len(self.ids)

    def end(self):
        pass


def _generate(conversation, job, max_new_tokens, video_with_audio=False, prefix=""):
    if model is None or processor is None:
        raise RuntimeError("Model is not loaded.")

    template_options = {}
    if video_with_audio:
        template_options = {
            "load_audio_from_video": True,
            "processor_kwargs": {"use_audio_in_video": True, "fps": VIDEO_FPS},
        }

    inputs = processor.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        **template_options,
    ).to(DEVICE)

    prompt_len = inputs["input_ids"].shape[1]
    gen_kwargs = dict(
        **inputs,
        max_new_tokens=max_new_tokens,
        generation_mode="text",
        do_sample=False,
    )

    with torch.inference_mode():
        try:
            streamer = JobStreamer(job, prompt_len, prefix)
            outputs = model.generate(**gen_kwargs, streamer=streamer)
        except JobCancelled:
            raise
        except (TypeError, ValueError) as error:
            if "streamer" not in str(error).lower():
                raise
            logger.warning("Model does not support streaming; falling back.")
            outputs = model.generate(**gen_kwargs)

    if hasattr(outputs, "sequence_lengths"):
        output_length = int(outputs.sequence_lengths[0].item())
    else:
        output_length = outputs.sequences.shape[1]

    generated = outputs.sequences[0, prompt_len:output_length]
    answer = processor.decode(generated, skip_special_tokens=True).strip()
    truncated = generated.shape[0] >= max_new_tokens

    if job is not None:
        job.text = prefix + answer
        job.tokens = int(generated.shape[0])

    return answer, truncated


# ============================================================
# PREPROCESSING
# ============================================================

def prepare_image(path: str, job: Job) -> str:
    job.stage = "Optimizing image"
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        w, h = img.size
        if max(w, h) > IMAGE_MAX_SIDE:
            scale = IMAGE_MAX_SIDE / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            job.notes.append(f"Image resized from {w}x{h} to {img.size[0]}x{img.size[1]} for speed.")
        out = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        out.close()
        img.save(out.name, "JPEG", quality=92)
    return out.name


def prepare_audio(path: str, job: Job, max_seconds: int) -> np.ndarray:
    job.stage = "Decoding audio"
    wav_path = None
    try:
        if FFMPEG:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            wav_path = tmp.name
            run_ffmpeg(["-i", path, "-t", str(max_seconds), "-ac", "1",
                        "-ar", str(AUDIO_SAMPLE_RATE), "-c:a", "pcm_s16le", wav_path])
            audio, _ = sf.read(wav_path, dtype="float32")
        else:
            audio, _ = librosa.load(path, sr=AUDIO_SAMPLE_RATE, mono=True,
                                    duration=max_seconds)
    except Exception as error:
        raise ValueError(f"Could not decode this audio file: {error}")
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)

    if audio is None or len(audio) == 0:
        raise ValueError("The uploaded audio contains no readable audio.")
    return audio


def prepare_video(path: str, job: Job, include_audio: bool) -> str:
    if not FFMPEG:
        job.notes.append("ffmpeg not found: using the original video (slower).")
        return path

    job.stage = "Optimizing video"
    max_seconds = max(1, int(MAX_VIDEO_FRAMES / max(VIDEO_FPS, 0.1)))
    out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    out.close()

    args = [
        "-i", path,
        "-t", str(max_seconds),
        "-vf", f"fps={VIDEO_FPS},scale='min({VIDEO_MAX_SIDE},iw)':-2",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-pix_fmt", "yuv420p",
    ]
    if include_audio:
        args += ["-c:a", "aac", "-ar", str(AUDIO_SAMPLE_RATE), "-ac", "1"]
    else:
        args += ["-an"]
    args += [out.name]

    try:
        run_ffmpeg(args)
    except Exception as error:
        os.remove(out.name)
        raise ValueError(f"Could not process this video: {error}")

    job.notes.append(
        f"Video optimized: first {max_seconds}s, {VIDEO_FPS} fps, max width {VIDEO_MAX_SIDE}px."
    )
    return out.name


# ============================================================
# TASK RUNNERS
# ============================================================

def run_text(job, question, max_new_tokens):
    if not question.strip():
        raise ValueError("Please enter a question or text.")
    conversation = [
        {"role": "system", "content": "You are a helpful assistant. Respond in text."},
        {"role": "user", "content": question},
    ]
    job.stage = "Generating answer"
    return _generate(conversation, job, max_new_tokens)


def run_image(job, file_path, question, max_new_tokens, cleanup):
    optimized = prepare_image(file_path, job)
    cleanup.append(optimized)
    job.check_cancel()

    conversation = [
        {"role": "system", "content": (
            "Answer questions about the provided image. "
            "Base every answer only on what can be seen. Respond in text.")},
        {"role": "user", "content": [
            {"type": "image", "image": optimized},
            {"type": "text", "text": question.strip() or "Describe this image in detail."},
        ]},
    ]
    job.stage = "Analyzing image"
    return _generate(conversation, job, max_new_tokens)


def write_wav(samples: np.ndarray, cleanup) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    sf.write(tmp.name, samples, AUDIO_SAMPLE_RATE, subtype="PCM_16")
    cleanup.append(tmp.name)
    return tmp.name


def run_audio(job, file_path, question, language, max_new_tokens, cleanup):
    if question.strip():
        audio = prepare_audio(file_path, job, AUDIO_QA_MAX_SECONDS)
        clip = write_wav(audio, cleanup)
        conversation = [
            {"role": "system", "content": (
                "Answer questions about the provided audio clip. "
                "Base every answer only on what can be heard. Respond in text.")},
            {"role": "user", "content": [
                {"type": "audio", "audio": clip},
                {"type": "text", "text": question},
            ]},
        ]
        job.stage = "Analyzing audio"
        return _generate(conversation, job, max_new_tokens)

    # Transcription: split into chunks so long audio is transcribed completely.
    audio = prepare_audio(file_path, job, AUDIO_MAX_SECONDS)
    chunk_size = AUDIO_CHUNK_SECONDS * AUDIO_SAMPLE_RATE
    chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]
    chunks = [c for c in chunks if len(c) > AUDIO_SAMPLE_RATE // 4]   # drop tiny tails

    system_prompt = (
        f"Perform ASR in {language}. Transcribe the spoken words accurately. "
        "Do not summarize or rewrite the speech. Respond in text."
    )

    full_text = ""
    any_truncated = False
    for index, chunk in enumerate(chunks, start=1):
        job.check_cancel()
        job.stage = f"Transcribing part {index} of {len(chunks)}"
        clip = write_wav(chunk, cleanup)
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [{"type": "audio", "audio": clip}]},
        ]
        prefix = full_text + (" " if full_text else "")
        part, truncated = _generate(conversation, job, max_new_tokens, prefix=prefix)
        any_truncated = any_truncated or truncated
        full_text = (prefix + part).strip()
        job.text = full_text

    return full_text, any_truncated


def run_video(job, file_path, question, include_audio, max_new_tokens, cleanup):
    optimized = prepare_video(file_path, job, include_audio)
    if optimized != file_path:
        cleanup.append(optimized)
    job.check_cancel()

    system_prompt = "Respond in text."
    if include_audio:
        system_prompt = ("Answer questions about the video using what you see "
                         "and hear. Respond in text.")

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "video", "video": optimized},
            {"type": "text",
             "text": question.strip() or "Describe what happens in this video."},
        ]},
    ]
    job.stage = "Analyzing video (this is the slowest mode on CPU)"
    return _generate(conversation, job, max_new_tokens, video_with_audio=include_audio)


# ============================================================
# JOB EXECUTION
# ============================================================

def execute_job(job: Job, params: dict):
    cleanup: list[str] = [params["file_path"]] if params.get("file_path") else []
    try:
        job.check_cancel()
        job.status = "running"
        job.started = time.time()

        mode = job.mode
        mnt = params["max_new_tokens"]

        if mode == "text":
            answer, truncated = run_text(job, params["question"], mnt)
        elif mode == "image":
            answer, truncated = run_image(job, params["file_path"], params["question"], mnt, cleanup)
        elif mode == "audio":
            answer, truncated = run_audio(job, params["file_path"], params["question"],
                                          params["language"], mnt, cleanup)
        else:
            answer, truncated = run_video(job, params["file_path"], params["question"],
                                          params["include_audio"], mnt, cleanup)

        job.text = answer
        job.truncated = bool(truncated)
        if not answer.strip():
            raise ValueError("The model returned an empty response.")
        job.stage = "Completed"
        job.status = "done"

    except JobCancelled:
        job.status = "cancelled"
        job.stage = "Cancelled"
    except torch.cuda.OutOfMemoryError:
        job.status, job.error = "error", "Insufficient GPU memory for inference."
    except MemoryError:
        job.status, job.error = "error", "The system ran out of memory during inference."
    except Exception as error:
        logger.exception("Job %s failed", job.id)
        job.status, job.error = "error", str(error)
    finally:
        job.finished = time.time()
        for path in cleanup:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


def purge_old_jobs():
    now = time.time()
    with jobs_lock:
        for job_id in [j for j, job in jobs.items()
                       if job.finished and now - job.finished > JOB_TTL_SECONDS]:
            del jobs[job_id]


def queue_position(job: Job) -> int:
    with jobs_lock:
        ahead = [j for j in jobs.values()
                 if j.status in ("queued", "running") and j.created < job.created]
    return len(ahead)


def job_to_dict(job: Job) -> dict:
    now = time.time()
    start = job.started or job.created
    end = job.finished or now
    elapsed = end - job.created
    gen_time = max(end - start, 0.001)
    return {
        "id": job.id,
        "mode": job.mode,
        "status": job.status,
        "stage": job.stage,
        "text": job.text,
        "error": job.error,
        "truncated": job.truncated,
        "tokens": job.tokens,
        "elapsed": round(elapsed, 1),
        "tokens_per_second": round(job.tokens / gen_time, 2) if job.tokens else 0,
        "queue_position": queue_position(job) if job.status == "queued" else 0,
        "notes": job.notes,
    }


# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


@app.get("/health")
async def health():
    with jobs_lock:
        active = sum(1 for j in jobs.values() if j.status in ("queued", "running"))
    return {
        "status": "running",
        "model": MODEL_ID,
        "device": DEVICE,
        "dtype": DTYPE_NAME,
        "threads": NUM_THREADS,
        "model_loaded": model is not None,
        "ffmpeg": FFMPEG is not None,
        "active_jobs": active,
        "max_queue": MAX_QUEUE,
    }


@app.post("/api/jobs")
async def create_job(
    mode: str = Form(...),
    question: str = Form(""),
    language: str = Form("English"),
    include_audio: bool = Form(False),
    max_new_tokens: int = Form(DEFAULT_MAX_NEW_TOKENS),
    file: UploadFile = File(None),
):
    if mode not in {"text", "image", "audio", "video"}:
        raise HTTPException(400, "Invalid input mode.")
    if model is None:
        raise HTTPException(503, "Model is still loading. Try again shortly.")

    max_new_tokens = max(16, min(int(max_new_tokens), HARD_MAX_NEW_TOKENS))

    purge_old_jobs()
    with jobs_lock:
        active = sum(1 for j in jobs.values() if j.status in ("queued", "running"))
    if active >= MAX_QUEUE:
        raise HTTPException(429, "The server is busy. Please try again in a moment.")

    temp_path = None
    try:
        if mode == "text":
            if not question.strip():
                raise HTTPException(400, "Please enter a question or text.")
        else:
            if file is None:
                raise HTTPException(400, "Please upload a file.")

            extension = Path(file.filename or "").suffix.lower()
            if extension not in ALLOWED_EXTENSIONS[mode]:
                raise HTTPException(400, f"Unsupported {mode} file format.")

            size = 0
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
                temp_path = temp_file.name
                while True:
                    block = await file.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    if size > MAX_FILE_SIZE:
                        raise HTTPException(413, "File is too large. Maximum size is 50 MB.")
                    temp_file.write(block)

            if size == 0:
                raise HTTPException(400, "Uploaded file is empty.")
    except HTTPException:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    finally:
        if file is not None:
            await file.close()

    job = Job(id=uuid.uuid4().hex[:12], mode=mode)
    with jobs_lock:
        jobs[job.id] = job

    params = {
        "question": question,
        "language": language,
        "include_audio": include_audio,
        "max_new_tokens": max_new_tokens,
        "file_path": temp_path,
    }
    executor.submit(execute_job, job, params)

    return {"job_id": job.id}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found or expired.")
    return job_to_dict(job)


@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found or expired.")
    job.cancel_event.set()
    return {"cancelled": True}


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5005, reload=False, workers=1)