# AGENTS.md — Agent Instructions for PGAGI Screening System

## Project Context
AI-powered candidate screening system using RAG + FastAPI + Next.js.
Read this file completely before writing any code in any session.

## Tech Stack (non-negotiable)
- **Backend**: Python 3.11, FastAPI, `uv` (package manager), SQLite + SQLAlchemy (async), ChromaDB, LangChain 0.2, sentence-transformers (`all-MiniLM-L6-v2`), PyMuPDF
- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind CSS v3, shadcn/ui, Zustand, React Query v5, pnpm

## Code Style Rules

### Python
- Use **Ruff** for linting and formatting (`ruff check .` and `ruff format .`)
- **Type hints on ALL functions** — parameters AND return types, no exceptions
- **Pydantic v2** models for all request/response schemas
- **Async/await** on all FastAPI route handlers and DB calls
- Docstrings on all public classes and functions (one-line minimum)
- No bare `except:` — always catch specific exception types
- Environment variables ONLY via `config.py` using `pydantic-settings BaseSettings`
- Never import from `__future__` unless strictly necessary

### TypeScript/React
- **Functional components only** — no class components
- Explicit return types on all functions (no implicit `any`)
- **React Query** for ALL server state — no `useState` for fetched data
- **Zustand** only for UI/local state (current question index, interview phase, etc.)
- No inline styles — Tailwind utility classes only
- Components in `PascalCase`, filenames match component name exactly
- No `// @ts-ignore` unless absolutely unavoidable (must add comment explaining why)

## Architecture Rules
1. Backend is the **single source of truth** for ALL business logic
2. Frontend only calls backend APIs — no direct AI/LLM API calls from the browser
3. All LLM prompt templates live exclusively in `backend/core/rag/prompts.py`
4. Session state persists in SQLite — frontend must reconstruct from API on page refresh
5. ChromaDB collections are named: `role_{role_slug}` (e.g. `role_aiml_engineer`, `role_data_scientist`)
6. Question generation happens **upfront** at interview start (not on-demand per question)

## API Contract (frontend ↔ backend)
Base URL: `http://localhost:8000`

```
POST   /api/v1/resume/parse              → ResumeData
POST   /api/v1/sessions                  → { session_id, role, status }
POST   /api/v1/interview/start           → { session_id, first_question, total_questions }
POST   /api/v1/interview/answer          → { next_question|null, progress, is_complete }
GET    /api/v1/sessions/{id}/report      → SessionReport
GET    /health                           → { status, db, chroma }
```

**All responses** must use this wrapper:
```json
{ "success": true, "data": { ... }, "error": null }
{ "success": false, "data": null, "error": "human-readable message" }
```

## Environment Variables
All must exist in `.env` (never hardcoded):
```
OPENAI_API_KEY=
CHROMA_PERSIST_PATH=./knowledge_base/chroma_db
DATABASE_URL=sqlite+aiosqlite:///./pgagi.db
MAX_QUESTIONS_PER_SESSION=8
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-4o-mini
CORS_ORIGINS=http://localhost:3000
```

## File Generation Order
Follow this order exactly to avoid import errors:
1. `backend/config.py`
2. `backend/db/models.py` → `database.py` → `crud.py` → `schemas.py`
3. `backend/core/resume_parser.py`
4. `backend/core/rag/prompts.py` → `ingestor.py` → `retriever.py`
5. `backend/core/question_generator.py` → `session_manager.py` → `evaluator.py`
6. `backend/api/dependencies.py` → `api/routes/*.py` → `main.py`
7. `frontend/lib/types.ts` → `lib/api.ts` → `lib/store.ts`
8. `frontend/components/*.tsx`
9. `frontend/app/**/*.tsx`

## Do NOT
- Do NOT use `pip` directly — use `uv add <package>`
- Do NOT use `npm` or `yarn` — use `pnpm`
- Do NOT hardcode API keys, URLs, or magic numbers
- Do NOT put business logic in route handlers — only in `core/` service classes
- Do NOT use synchronous file I/O inside async route handlers (use `aiofiles`)
- Do NOT generate placeholder/mock data — every API response must come from the real pipeline
- Do NOT create new files outside the defined folder structure without asking
- Do NOT skip error handling on LLM calls — always wrap in try/catch with retry logic

## LLM Output Parsing
All LLM calls that need structured output must:
1. Use `response_format={"type": "json_object"}` in the OpenAI call
2. Strip any ```json fences before parsing
3. Validate with Pydantic before returning
4. Retry once on parse failure, then raise a typed exception

## ChromaDB Rules
- Always use `PersistentClient` (not `EphemeralClient`) so data survives restarts
- Use cosine similarity metric for all collections
- Metadata on every chunk: `source_file`, `page_number`, `role`, `chunk_index`
- Deduplicate retrieved chunks by content hash before passing to LLM

## Testing
- Every `core/` module must have a corresponding test file in `backend/tests/`
- Tests must use real data (not mocks) wherever possible
- At minimum: resume parser test, RAG retrieval test, one API route test
