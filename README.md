# AI Clinical Documentation Copilot

An AI-powered clinical documentation assistant that automatically generates structured medical documentation from audio recordings and clinical notes. Built with FastAPI, Next.js 14, and integrated with Groq's LLM API for intelligent extraction and summarization.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

## 🌟 Features

- **Audio Transcription**: Automatic transcription using Faster-Whisper
- **Clinical Entity Extraction**: AI-powered extraction of symptoms, history, observations, and recommendations
- **RAG Enhancement**: Clinical guidelines retrieval to enhance accuracy
- **SOAP Notes Generation**: Structured clinical documentation
- **Task Management**: Automated follow-up task generation
- **Modern UI**: Beautiful dark-themed interface with glassmorphism effects
- **Session Management**: Save and review previous documentation sessions

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────┐
│                 │     │              Backend (FastAPI)           │
│   Next.js 14    │────▶│  ┌─────────────────────────────────────┐ │
│   Frontend      │     │  │ Faster-Whisper │ Groq LLM │ ChromaDB│ │
│                 │◀────│  └─────────────────────────────────────┘ │
└─────────────────┘     │              SQLite Storage              │
                        └──────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **Groq API Key** (free at [console.groq.com](https://console.groq.com))

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd "AI Clinical Documentation Copilot"
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python run.py
```

The backend will start at `http://localhost:8000`

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start at `http://localhost:3000`

### 4. Open the Application

Open your browser and navigate to `http://localhost:3000`

## 📁 Project Structure

```
AI Clinical Documentation Copilot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic models
│   │   │   └── database.py      # SQLite database
│   │   ├── routers/
│   │   │   ├── upload.py        # File upload endpoints
│   │   │   ├── processing.py    # Processing pipeline
│   │   │   └── sessions.py      # Session management
│   │   ├── services/
│   │   │   ├── transcription.py # Whisper transcription
│   │   │   ├── pdf_extractor.py # PDF/text extraction
│   │   │   ├── groq_client.py   # Groq LLM client
│   │   │   ├── rag_pipeline.py  # RAG with ChromaDB
│   │   │   └── summary_generator.py
│   │   ├── data/
│   │   │   └── clinical_guidelines.py  # RAG knowledge base
│   │   └── utils/
│   │       └── helpers.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Upload page
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── globals.css      # Global styles
│   │   │   ├── results/[sessionId]/page.tsx
│   │   │   └── sessions/page.tsx
│   │   ├── components/
│   │   │   ├── AudioUploader.tsx
│   │   │   ├── NotesUploader.tsx
│   │   │   ├── ProcessingStatus.tsx
│   │   │   ├── TranscriptionView.tsx
│   │   │   ├── EntitiesView.tsx
│   │   │   ├── SoapNotes.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── SessionCard.tsx
│   │   ├── hooks/
│   │   │   └── useProcessing.ts
│   │   └── lib/
│   │       └── api.ts
│   ├── package.json
│   └── next.config.js
│
├── sample_data/
│   ├── sample_notes.txt         # Example clinical notes
│   └── sample_output.json       # Example output
│
└── README.md
```

## 🔧 Configuration

### Environment Variables

The Groq API key is configured in `backend/app/config.py`. You can also set it via environment variable:

```bash
export GROQ_API_KEY=your_api_key_here
```

### Whisper Model

The default Whisper model is `small`. You can change it in `backend/app/config.py`:

```python
whisper_model: str = "small"  # Options: tiny, base, small, medium, large
```

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/audio` | Upload audio file |
| POST | `/api/upload/notes` | Upload notes file |
| POST | `/api/process/{session_id}` | Start processing |
| GET | `/api/process/{session_id}/status` | Get status |
| GET | `/api/process/{session_id}/result` | Get results |
| GET | `/api/sessions` | List all sessions |
| GET | `/api/sessions/{session_id}` | Get session details |
| DELETE | `/api/sessions/{session_id}` | Delete session |
| GET | `/health` | Health check |

## 🧪 Testing

### Sample Files

Use the provided sample files in `sample_data/`:

1. **sample_notes.txt**: Clinical notes for an audiology patient
2. **sample_output.json**: Expected output format

### Quick Test

1. Start both backend and frontend
2. Open `http://localhost:3000`
3. Upload `sample_data/sample_notes.txt` as notes
4. Click "Generate Documentation"
5. View the generated SOAP notes and tasks

## 🎨 UI Features

- **Dark Mode**: Modern dark theme with gradient accents
- **Glassmorphism**: Beautiful frosted glass card effects
- **Animations**: Smooth transitions and loading states
- **Responsive**: Works on desktop and tablet
- **Drag & Drop**: Easy file uploads

## 🔬 Technical Details

### RAG Pipeline

The RAG system uses:
- **Vector Store**: ChromaDB (local, persistent)
- **Embeddings**: sentence-transformers `all-mpnet-base-v2`
- **Knowledge Base**: 14 clinical guideline documents covering:
  - Hearing loss classification
  - Audiological assessment
  - Treatment recommendations
  - Tinnitus management
  - Vestibular disorders
  - Pediatric audiology
  - Follow-up protocols

### LLM Integration

- **Provider**: Groq (free tier available)
- **Model**: Llama-3.1-70b-versatile
- **Features**:
  - Structured JSON extraction
  - Retry logic with exponential backoff
  - Response sanitization

### Transcription

- **Engine**: Faster-Whisper
- **Model**: Configurable (default: small)
- **Features**:
  - VAD (Voice Activity Detection)
  - Timestamped segments
  - Language detection

## 🚨 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Ensure Python 3.10+ is installed
   - Check all dependencies are installed: `pip install -r requirements.txt`
   - Verify the Groq API key is valid

2. **Whisper model download fails**
   - First run will download the model (~500MB for small)
   - Ensure stable internet connection
   - Models are cached in `~/.cache/huggingface/`

3. **Frontend API errors**
   - Ensure backend is running on port 8000
   - Check browser console for CORS errors
   - Verify `next.config.js` proxy is configured

4. **Processing timeout**
   - Large audio files may take longer
   - Check backend logs for errors
   - Groq API has rate limits on free tier

## 🌐 Deployment

### Deploy to Production (Render + Vercel)

This application can be deployed using **Render** (backend) and **Vercel** (frontend).

#### Prerequisites
- GitHub account with this repo pushed
- [Render](https://render.com) account (free tier available)
- [Vercel](https://vercel.com) account (free tier available)
- Groq API key from [console.groq.com](https://console.groq.com)

#### 1. Deploy Backend to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `clinical-copilot-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variable**:
   - `GROQ_API_KEY` = your Groq API key
   - `WHISPER_MODEL` = `tiny` (for free tier) or `small` (paid tier)
6. Click **Create Web Service**
7. Wait for deployment, note your URL: `https://your-app.onrender.com`

#### 2. Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import your GitHub repository
3. Configure the project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
4. Add **Environment Variable**:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
5. Click **Deploy**

#### 3. Verify Deployment

1. Visit your Vercel URL
2. Upload a sample file and test the documentation generation
3. Check Render logs if issues occur

> **Note**: Render free tier may sleep after 15 minutes of inactivity. First request after sleep takes ~30 seconds.

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast LLM inference
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) for transcription
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

