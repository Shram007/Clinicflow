ClinicFlow Skeleton

Overview
- Turns doctor voice notes into structured clinical documentation.
- Frontend: React + Vite + TypeScript with Tailwind and shadcn/ui.
- Backend: FastAPI exposing health, visits, and voice upload endpoints.

Project Layout
- Backend: `clinicflow/backend`
  - Entrypoint: `backend/main.py`
  - Routers: `backend/api/routes_health.py`, `backend/api/routes_visits.py`, `backend/api/routes_voice.py`
  - Schemas: `backend/schemas/visit.py`
- Frontend: `clinicflow/frontend`
  - App: `src/App.tsx`, pages: `src/pages/Index.tsx`, `src/pages/Visits.tsx`
  - Components: `src/components/MicRecorder.tsx`, `src/components/VisitCard.tsx`, `src/components/PageContainer.tsx`
  - Dev config: `vite.config.ts` (proxy `/api` to backend)

Backend Endpoints
- `GET /api/health` – service status
- `GET /api/visits` – list of visit summaries
- `GET /api/visits/{visit_id}` – visit detail
- `POST /api/voice/upload` – accepts audio (`multipart/form-data` field `file`) and optional `visit_id`
  - Saves to `clinicflow/audio/{visit_id}.<ext>`
  - Transcribes using OpenAI Whisper if `OPENAI_API_KEY` is set; otherwise returns placeholder text

Prerequisites
- Python 3.9+
- Node.js 18+

Setup
- Python env and deps
  - `py -3 -m venv .venv`
  - `.venv\Scripts\python -m pip install --upgrade pip`
  - `.venv\Scripts\python -m pip install fastapi uvicorn pydantic python-multipart`
  - Optional STT: `.venv\Scripts\python -m pip install openai`
- Frontend deps
  - `cd clinicflow/frontend`
  - `npm install`

Environment Variables
- `OPENAI_API_KEY` (optional) – enables Whisper transcription in `/api/voice/upload`
- Recommended for production:
  - `ALLOWED_ORIGINS` – comma-separated CORS origins (backend)
 - Copy `clinicflow/.env.example` → `clinicflow/.env` and fill values (do not commit secrets)

- Run (Development)
- Backend (from `clinicflow`):
  - Simple: `.venv\Scripts\python -m backend`
    - Uses `BACKEND_HOST`/`BACKEND_PORT` env vars if set
    - Auto-selects a free port (starts at 8000)
    - Enable reload: `RELOAD=1 .venv\Scripts\python -m backend`
  - Advanced: `.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
- Frontend (from `clinicflow/frontend`):
  - `npm run dev` (Vite dev server)
  - Open `http://localhost:8081/`
  - Vite proxy forwards `/api/*` to `http://127.0.0.1:8000`

Voice Note Flow
- On `/`:
  - Click Start Recording to capture mic audio
  - Click Stop Recording to upload `audio/webm` to `/api/voice/upload`
  - Transcript appears in an editable textarea
  - Click “Run ClinicFlow” (placeholder)

Production Notes
- Avoid hard-coded API hosts; use relative `/api` paths and proxy/gateway in front of services
- Tighten CORS with explicit origins via env variable
- Consider persistent storage (S3/object storage) for audio files
- Add provider abstraction for STT (OpenAI Whisper, Deepgram, local Whisper)
- Implement file size limits, content-type checks, and request logging

Testing and Quality
- Add unit tests for routers and schema validation
- Integrate React Query for data fetching and caching on pages
- Use loading skeletons and error toasts for better UX

Key Files to Review
- `backend/api/routes_voice.py` – upload + transcription
- `frontend/src/components/MicRecorder.tsx` – recording and upload
- `frontend/vite.config.ts` – proxy config for `/api`

Pin Backend Port for Production Compatibility
- To keep frontend proxy (`/api` → `127.0.0.1:8000`) aligned and mirror production behavior, set a fixed backend port.
- Windows PowerShell:
  - `Set-Item -Path Env:BACKEND_PORT -Value 8000`
  - `Set-Item -Path Env:BACKEND_HOST -Value 127.0.0.1`
  - `.venv\Scripts\python -m backend`
- macOS/Linux:
  - `export BACKEND_PORT=8000 BACKEND_HOST=127.0.0.1`
  - `.venv/\Scripts/python -m backend`
- Notes:
  - With `BACKEND_PORT=8000`, Vite’s dev proxy requires no changes.
  - In production, keep the API behind a reverse proxy and serve the frontend under the same domain to avoid CORS.

## MCP Server

`clinicflow/backend/mcp_server.py` exposes clinical documentation tools as [Model Context Protocol](https://modelcontextprotocol.io/) callable tools over stdio JSON-RPC 2.0.

### Tools exposed

| Tool | Description |
|------|-------------|
| `generate_soap_note` | Generate a SOAP note from a voice transcript |
| `list_visits` | List all stored visit summaries |
| `get_visit` | Retrieve a single visit by ID |

### Run the MCP server

```bash
python clinicflow/backend/mcp_server.py
```

The server reads JSON-RPC 2.0 requests from `stdin` and writes responses to `stdout` — compatible with any MCP host (Claude Desktop, Cursor, etc.).

### Smoke test (no API key required)

```bash
python clinicflow/backend/tests/test_mcp_server.py
```
