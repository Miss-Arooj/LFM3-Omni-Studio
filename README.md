# LFM3-Omni Studio

A web-based multimodal AI application powered by **Liquid AI's LFM3-Omni-2B** model. The application provides a single dashboard for interacting with text, images, audio, and videos.

## Dashboard Preview

<!-- Replace each placeholder URL with your own uploaded video URL. -->
### 1. Dashboard Overview
A quick walkthrough of the dashboard, its input modes, response panel, and available controls.

https://github.com/user-attachments/assets/b973e409-2bb3-4dd5-9f77-c71bf9fe8101

### 2. Text Input
Demonstrates submitting a text prompt and viewing the model's generated response.

https://github.com/user-attachments/assets/1679585b-dedc-44bc-b2c6-a36755c0fe11

### 3. Image Input
Shows how to upload an image and ask the model questions about its visual content.

https://github.com/user-attachments/assets/a3273b58-e734-464b-ac81-3dfea6472cff

### 4. Audio Input — Without a Prompt
Demonstrates uploading an audio file with an empty prompt to generate a transcription.

https://github.com/user-attachments/assets/2854ca59-5b3a-4459-845d-68a83bc07590

### 5. Audio Input — With a Prompt
Demonstrates asking a question about an audio file instead of requesting a basic transcription.

https://github.com/user-attachments/assets/111c34d6-ec2d-4f71-992e-35ffd1482f85

### 6. Video Input
Shows how to upload a video and ask the model to describe or analyze its content. The dashboard also includes an option to analyze the video's soundtrack.

https://github.com/user-attachments/assets/bd355aba-aeb3-47d2-9c16-19b56c544e3b

---

## Features

- **Text understanding:** Submit text prompts and receive generated responses.
- **Image understanding:** Upload an image and ask questions about its contents.
- **Audio understanding:** Transcribe audio when the prompt is empty, or ask questions about the audio.
- **Video understanding:** Analyze video content and optionally include its soundtrack.
- **Live response updates:** Display generated text as it becomes available.
- **Job controls:** View task status and cancel a running task.
- **Upload validation:** Supports configured file types and a 50 MB upload limit.
- **Performance information:** Displays model/device status, active jobs, and generation metrics.

## Tech Stack

- Python
- PyTorch
- Hugging Face Transformers
- Liquid AI LFM3-Omni-2B
- FastAPI
- HTML, CSS, and JavaScript
- FFmpeg / imageio-ffmpeg for media processing

## Project Structure

```text
LFM3-Omni-Studio/
├── main.py
├── ui.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer (use a Python version supported by the installed PyTorch and Transformers releases).
- Internet access for the initial model download.
- Sufficient RAM or GPU memory for the model and selected input.
- FFmpeg is recommended for audio/video processing. The project also includes `imageio-ffmpeg` as a Python dependency.

> **Note:** Model loading and inference can require substantial memory. CPU inference may be slow, especially for video. Actual performance depends on your hardware and input size.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/LFM3-Omni-Studio.git
cd LFM3-Omni-Studio
```

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install a PyTorch build appropriate for your operating system and hardware if the default installation does not provide the required CPU/GPU support. Refer to the [official PyTorch installation selector](https://pytorch.org/get-started/locally/).

### 4. Configure environment variables (optional)

Copy `.env.example` to `.env` and adjust values if needed. The application reads environment variables from the process environment; it does not automatically load a `.env` file. Export the variables in your terminal before starting the app, or use your preferred environment-variable loader.

### 5. Run the application

```bash
python main.py
```

Open the dashboard at:

```text
http://localhost:5005
```

The first startup downloads the model from Hugging Face if it is not already cached. Keep the terminal running while using the application.

## Supported Inputs

| Input | Supported formats / behavior |
|---|---|
| Text | Text prompt |
| Image | `.jpg`, `.jpeg`, `.png`, `.webp` |
| Audio | `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg` |
| Video | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm` |

Maximum upload size: **50 MB**.

For audio, an empty prompt requests transcription. A non-empty prompt asks the model a question about the audio. For video, the soundtrack can optionally be included in the analysis.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the dashboard |
| `GET` | `/health` | Returns model and application status |
| `POST` | `/api/jobs` | Creates a text, image, audio, or video task |
| `GET` | `/api/jobs/{job_id}` | Retrieves task status and response |
| `DELETE` | `/api/jobs/{job_id}` | Requests task cancellation |

Interactive API documentation is available at `http://localhost:5005/docs` while the server is running.

## Configuration

The backend supports these environment variables:

| Variable | Default | Description |
|---|---:|---|
| `MODEL_ID` | `LiquidAI/LFM3-Omni-2B` | Hugging Face model ID |
| `DEVICE` | `cpu` | Device used by the model, e.g. `cpu` or `cuda` |
| `DTYPE` | `float32` | Model data type |
| `NUM_THREADS` | CPU count | PyTorch CPU thread count |
| `IMAGE_MAX_SIDE` | `768` | Maximum image side length used during preprocessing |
| `VIDEO_MAX_SIDE` | `448` | Maximum video side length used during preprocessing |
| `VIDEO_FPS` | `1` | Video sampling rate |
| `MAX_VIDEO_FRAMES` | `16` | Maximum video frames |
| `AUDIO_CHUNK_SECONDS` | `30` | Audio transcription chunk length |
| `AUDIO_MAX_SECONDS` | `600` | Maximum audio transcription duration |
| `AUDIO_QA_MAX_SECONDS` | `120` | Maximum audio question-answering duration |
| `MAX_QUEUE` | `5` | Maximum number of queued/running jobs |

Defaults are defined in `main.py`. Set environment variables before starting the application to override them.

## Model

This project uses [LiquidAI/LFM3-Omni-2B](https://huggingface.co/LiquidAI/LFM3-Omni-2B). Review the model card and its license/usage terms before using or redistributing the model.

The model is downloaded from Hugging Face at runtime; model weights are not included in this repository.

## Notes and Limitations

- The application runs model inference locally on the machine hosting the backend.
- Video analysis can take considerably longer than text or image analysis, particularly on CPU.
- The audio language selector includes Urdu, but the dashboard notes that Urdu is not an officially supported language by the model.
- Do not upload private, confidential, or sensitive media unless you have permission and understand where the server processes and stores it.
- This repository does not include model weights, virtual environments, uploaded media, or generated temporary files.

## Future Improvements

The following features are planned to expand the application's real-time multimodal capabilities:

- **Live Audio Input:** Capture audio directly from the microphone and enable real-time audio understanding and interaction.
- **Live Image Capture:** Capture images directly using a webcam instead of uploading image files.
- **Live Audio/Video Capture:** Enable real-time camera and microphone access for capturing and analyzing audio and video streams.
- **Real-Time Multimodal Interaction:** Support continuous interaction with the model using live text, images, audio, and video inputs.
- **Improved Performance:** Optimize inference speed, memory usage, and response latency for a smoother user experience.
- **Expanded Language Support:** Improve multilingual capabilities and support for additional languages.
