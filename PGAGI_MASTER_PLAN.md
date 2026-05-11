# PGAGI AI Screening System 


---

## STRATEGY OVERVIEW

| Dimension | Choice | Rationale |
|---|---|---|
| Package Manager (FE) | `pnpm` | Faster installs, strict hoisting, better monorepo support |
| Package Manager (BE) | `uv` (Python) | 10–100x faster than pip, modern lock files |
| Frontend | Next.js 14 (App Router) | SSR + API routes fallback, great DX |
| Backend | FastAPI (Python 3.11+) | Async-first, auto OpenAPI, perfect for ML pipelines |
| Vector DB | ChromaDB (local) | Zero infra, persists to disk, sufficient for demo |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | Fast, free, runs locally, 384-dim |
| LLM | OpenAI `gpt-4o-mini` (primary) OR Groq `llama3-70b` | Cost-efficient; swap via env var |
| DB (sessions) | SQLite via SQLAlchemy | Zero config, persists, good enough for demo |
| Resume Parsing | PyMuPDF (`fitz`) + regex/NLP | Reliable PDF text extraction |
| RAG Orchestration | LangChain 0.2 | Mature, well-documented, ChromaDB integration built-in |
| Styling | Tailwind CSS v3 + shadcn/ui | Fastest way to production UI |
| State (FE) | Zustand + React Query | Lightweight, minimal boilerplate |
| Code Style | Ruff (Python) + ESLint/Prettier (JS) | Fast, opinionated |
| AI Model in Prompts | `claude-sonnet-4-20250514` for Opencode | Best reasoning for complex code gen |

---

## SYSTEM ARCHITECTURE

```
pgagi-screening/
├── README.md
├── AGENTS.md                    ← Opencode agent config
├── .env.example
├── docker-compose.yml           ← optional, for demo
│
├── backend/                     ← FastAPI Python service
│   ├── pyproject.toml           ← uv project config
│   ├── uv.lock
│   ├── main.py                  ← FastAPI app entry
│   ├── config.py                ← settings via pydantic-settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── sessions.py      ← POST /sessions, GET /sessions/{id}
│   │   │   ├── resume.py        ← POST /resume/parse
│   │   │   ├── interview.py     ← POST /interview/start, /next, /submit
│   │   │   └── reports.py       ← GET /reports/{session_id}
│   │   └── dependencies.py      ← FastAPI DI (db session, services)
│   │
│   ├── core/
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── ingestor.py      ← chunk + embed knowledge base docs
│   │   │   ├── retriever.py     ← query ChromaDB, return top-k chunks
│   │   │   └── prompts.py       ← all LLM prompt templates
│   │   ├── resume_parser.py     ← extract skills/experience from PDF
│   │   ├── question_generator.py← RAG → LLM → structured questions
│   │   ├── session_manager.py   ← interview state machine
│   │   └── evaluator.py         ← score answers, generate report
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          ← SQLAlchemy engine + session factory
│   │   ├── models.py            ← Session, Question, Answer ORM models
│   │   └── crud.py              ← typed CRUD helpers
│   │
│   ├── knowledge_base/
│   │   ├── raw/                 ← drop PDFs here (ML books)
│   │   ├── chroma_db/           ← persisted vector index (gitignored)
│   │   └── ingest_script.py     ← run once: python ingest_script.py
│   │
│   └── tests/
│       ├── test_rag.py
│       ├── test_resume_parser.py
│       └── test_api.py
│
└── frontend/                    ← Next.js 14 App Router
    ├── package.json
    ├── pnpm-lock.yaml
    ├── tailwind.config.ts
    ├── next.config.ts
    │
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx             ← Landing / role selection
    │   ├── interview/
    │   │   ├── setup/page.tsx   ← Upload resume + select role
    │   │   ├── [sessionId]/
    │   │   │   ├── page.tsx     ← Interview chat interface
    │   │   │   └── report/page.tsx ← Final report
    │   └── api/                 ← (optional Next.js route handlers)
    │
    ├── components/
    │   ├── ui/                  ← shadcn/ui primitives
    │   ├── ResumeUpload.tsx
    │   ├── RoleSelector.tsx
    │   ├── InterviewChat.tsx
    │   ├── QuestionCard.tsx
    │   ├── AnswerInput.tsx
    │   ├── ProgressBar.tsx
    │   └── ReportView.tsx
    │
    ├── lib/
    │   ├── api.ts               ← typed fetch wrappers for backend
    │   ├── store.ts             ← Zustand store (session state)
    │   └── types.ts             ← shared TypeScript types
    │
    └── hooks/
        ├── useInterview.ts
        └── useReport.ts
```

---

## AGENTS.md (place in repo root)

```markdown
# AGENTS.md — Opencode Agent Instructions for PGAGI Screening System

## Project Context
AI-powered interview system using RAG + FastAPI + Next.js.
Read this file completely before writing any code.

## Tech Stack (non-negotiable)
- Backend: Python 3.11, FastAPI, uv (package manager), SQLite + SQLAlchemy, ChromaDB, LangChain 0.2, sentence-transformers, PyMuPDF
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS v3, shadcn/ui, Zustand, React Query v5, pnpm

## Code Style Rules
### Python
- Use Ruff for linting (ruff check + ruff format)
- Type hints on ALL functions (parameters + return types)
- Pydantic v2 models for all request/response schemas
- Async/await for all FastAPI route handlers
- Docstrings on all public classes and functions
- No bare `except:` — always catch specific exceptions
- Environment variables ONLY via `config.py` (pydantic-settings BaseSettings)

### TypeScript/React
- Functional components only, no class components
- Explicit return types on all functions
- Use React Query for ALL server state (no useState for fetched data)
- Zustand only for UI/local state (current question index, interview phase)
- No inline styles — Tailwind classes only
- Components in PascalCase, files match component name

## Architecture Rules
1. Backend is the single source of truth for ALL business logic
2. Frontend only calls backend APIs — no direct AI API calls from frontend
3. All AI prompts live in `backend/core/rag/prompts.py` — never scattered in routes
4. Session state persists in SQLite — frontend reconstructs from API on refresh
5. ChromaDB collection named: `role_{role_slug}` (e.g. `role_aiml_engineer`)

## File Generation Order (follow this exactly)
1. Backend: config.py → db/models.py → db/database.py → db/crud.py
2. Backend: core/resume_parser.py → core/rag/* → core/question_generator.py
3. Backend: api/routes/* → main.py
4. Frontend: lib/types.ts → lib/api.ts → lib/store.ts
5. Frontend: components/* → app/pages

## API Contract (frontend ↔ backend)
Base URL: http://localhost:8000

POST   /api/v1/resume/parse         → { skills, experience, education, raw_text }
POST   /api/v1/sessions             → { session_id, role, status }
POST   /api/v1/interview/start      → { session_id, first_question }
POST   /api/v1/interview/answer     → { next_question | null, session_complete }
GET    /api/v1/sessions/{id}/report → { questions[], answers[], score, insights }

All responses wrapped in: { "success": bool, "data": ..., "error": str | null }

## Environment Variables (.env)
OPENAI_API_KEY=
CHROMA_PERSIST_PATH=./knowledge_base/chroma_db
DATABASE_URL=sqlite:///./pgagi.db
MAX_QUESTIONS_PER_SESSION=8
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-4o-mini
CORS_ORIGINS=http://localhost:3000

## Do NOT
- Do not use pip directly — use `uv add <package>`
- Do not use npm/yarn — use `pnpm`
- Do not hardcode API keys
- Do not put business logic in route handlers — only in core/ services
- Do not use synchronous file I/O in async route handlers (use aiofiles)
- Do not generate mock data — every response must come from real pipeline
```

---

## PHASES & OPENCODE PROMPTS

### PHASE 0 — Project Scaffold & Config
**Goal:** Create all config files, env setup, and project skeleton.

```
You are setting up a new monorepo project called "pgagi-screening".

Create the following structure exactly:
1. Root: README.md, AGENTS.md (content provided in repo), .env.example, .gitignore
2. Backend: Initialize with `uv init backend` then add dependencies:
   fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings alembic
   pymupdf langchain langchain-community langchain-openai chromadb
   sentence-transformers openai python-multipart aiofiles ruff pytest httpx

3. Frontend: Run `pnpm create next-app frontend --typescript --tailwind --app --src-dir=no --import-alias="@/*"`
   Then: pnpm add zustand @tanstack/react-query axios react-dropzone lucide-react
   Then: pnpm dlx shadcn-ui@latest init (accept defaults, use "slate" theme)
   Install components: pnpm dlx shadcn-ui@latest add button card badge progress textarea select separator

4. Create backend/config.py using pydantic-settings BaseSettings reading all env vars from .env.example
5. Create .env.example with all variables listed in AGENTS.md

Output the exact terminal commands to run, then generate each file. Do not skip any file.
```

---

### PHASE 1 — Database Layer
**Goal:** SQLAlchemy models + CRUD for sessions, questions, answers.

```
In backend/db/, implement the complete database layer.

Models to create in db/models.py:
- InterviewSession: id (UUID), candidate_name, role (enum), resume_text, skills_extracted (JSON), status (enum: CREATED/ACTIVE/COMPLETED), created_at, completed_at
- InterviewQuestion: id (UUID), session_id (FK), question_text, context_chunks (JSON), question_number, difficulty (enum: BASIC/INTERMEDIATE/ADVANCED), topic, created_at
- InterviewAnswer: id (UUID), question_id (FK), session_id (FK), answer_text, score (float nullable), feedback (text nullable), answered_at

In db/database.py:
- Create async SQLAlchemy engine using DATABASE_URL from config
- Session factory with async context manager
- create_all() function for table creation on startup

In db/crud.py:
- create_session(db, role, candidate_name, resume_text) → InterviewSession
- update_session_skills(db, session_id, skills) → InterviewSession
- get_session(db, session_id) → InterviewSession | None
- complete_session(db, session_id) → InterviewSession
- create_question(db, session_id, question_text, context, topic, difficulty) → InterviewQuestion
- get_session_questions(db, session_id) → list[InterviewQuestion]
- create_answer(db, question_id, session_id, answer_text) → InterviewAnswer
- update_answer_score(db, answer_id, score, feedback) → InterviewAnswer
- get_session_report(db, session_id) → dict with full session data

All functions must be async. All models must have Pydantic v2 schema equivalents in db/schemas.py.
Use proper cascade deletes. Add indexes on session_id foreign keys.
```

---

### PHASE 2 — Resume Parser
**Goal:** Extract structured data from uploaded PDF resumes.

```
Create backend/core/resume_parser.py

This module must:
1. Accept a bytes object (PDF file content) as input
2. Use PyMuPDF (fitz) to extract raw text from all pages
3. Parse the extracted text to identify:
   - skills: List[str] — programming languages, frameworks, tools, ML libraries
     Look for sections like "Skills", "Technologies", "Tech Stack"
     Also scan bullet points for recognizable tech terms
   - experience_years: float — estimate from work history dates
   - education: List[str] — degrees + institutions
   - job_titles: List[str] — previous roles
   - domains: List[str] — categorized areas (e.g. "Machine Learning", "Backend Development", "Data Engineering")
   - projects: List[str] — project names/descriptions
   - raw_text: str — full extracted text for RAG context

4. Return a ResumeData Pydantic model with all above fields

Implementation notes:
- Use regex patterns for date extraction (experience_years calculation)
- Build a comprehensive KNOWN_SKILLS set covering: Python, Java, JavaScript, TypeScript, React, Next.js, FastAPI, Django, Flask, Node.js, TensorFlow, PyTorch, scikit-learn, pandas, numpy, SQL, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, GCP, Azure, Git, LangChain, HuggingFace, OpenCV, Spark
- Categorize domains based on which skills cluster together
- Gracefully handle malformed PDFs (return partial data, never raise)
- Add a test in tests/test_resume_parser.py with a synthetic resume string
```

---

### PHASE 3 — RAG Pipeline
**Goal:** Ingest knowledge base, retriever, and question generator.

```
Implement the complete RAG pipeline in backend/core/rag/

=== PART A: ingestor.py ===
Create a KnowledgeBaseIngestor class that:
1. Loads PDF files from knowledge_base/raw/ directory
2. Uses LangChain's PyMuPDFLoader
3. Chunking strategy:
   - RecursiveCharacterTextSplitter with chunk_size=800, chunk_overlap=150
   - This preserves sentence context while keeping chunks retrievable
4. Embeds chunks using HuggingFaceEmbeddings with model "all-MiniLM-L6-v2"
5. Stores in ChromaDB with collection named by role slug
6. Each chunk's metadata must include: source_file, page_number, role, chunk_index
7. Method: ingest_for_role(role: str, pdf_paths: List[str]) → int (chunks stored)
8. Method: get_collection_stats() → dict (per-role chunk counts)

=== PART B: retriever.py ===
Create a RAGRetriever class that:
1. Connects to existing ChromaDB at CHROMA_PERSIST_PATH
2. Method: retrieve(query: str, role: str, k: int = 5) → List[RetrievedChunk]
   - RetrievedChunk: { text, source, page, relevance_score }
3. Method: build_interview_query(resume_data: ResumeData, role: str) → List[str]
   - Generates 3-5 targeted queries based on candidate's skills + role
   - E.g. for ML Engineer with PyTorch: "gradient descent optimization neural networks"
   - E.g. for weaker area: "supervised learning fundamentals evaluation metrics"
4. Method: get_context_for_generation(resume_data, role) → str
   - Calls build_interview_query, retrieves, deduplicates, returns concatenated context

=== PART C: prompts.py ===
Define all prompt templates as Python constants (use LangChain PromptTemplate):

QUESTION_GENERATION_PROMPT: Given role, resume summary, retrieved context → generate N questions
- Questions must be conceptual AND applied (not just definition-asking)
- Must vary in difficulty based on candidate's experience level
- Must reference specific technologies from the candidate's resume
- Output MUST be valid JSON array: [{"question": str, "topic": str, "difficulty": str, "expected_keywords": [str]}]

FOLLOW_UP_PROMPT: Given question, candidate answer, resume context → generate adaptive follow-up
- If answer is weak: simplify and probe foundational understanding
- If answer is strong: deepen with edge cases or architecture decisions

EVALUATION_PROMPT: Given question, expected_keywords, candidate answer → score 0-10 + feedback
- Output JSON: {"score": float, "feedback": str, "strengths": [str], "gaps": [str]}

REPORT_GENERATION_PROMPT: Given full session data → generate structured insights
- Output JSON: {"overall_score": float, "recommendation": str, "strengths": [str], "areas_for_improvement": [str], "topic_scores": {str: float}}
```

---

### PHASE 4 — Core Services
**Goal:** Question generator, session manager, evaluator.

```
Implement the three core service classes in backend/core/

=== question_generator.py ===
Class QuestionGenerator:
- __init__(self, retriever: RAGRetriever, llm_model: str)
- Initialize AsyncOpenAI client
- Method: generate_questions(resume_data: ResumeData, role: str, count: int = 8) → List[GeneratedQuestion]
  1. Call retriever.get_context_for_generation(resume_data, role)
  2. Build QUESTION_GENERATION_PROMPT with context + resume summary
  3. Call LLM with response_format={"type": "json_object"}
  4. Parse + validate output, return List[GeneratedQuestion]
  5. On parse failure: retry once, then raise QuestionGenerationError
- Method: generate_followup(question: str, answer: str, resume_data: ResumeData) → str
  Uses FOLLOW_UP_PROMPT

=== session_manager.py ===
Class InterviewSessionManager:
State machine: CREATED → ACTIVE → COMPLETED
- Method: start_session(db, session_id: str) → dict with first question
  1. Load session from DB
  2. Generate all questions upfront (store in DB)  
  3. Mark session ACTIVE
  4. Return first question
- Method: submit_answer(db, session_id: str, answer_text: str) → dict
  1. Retrieve current question (by question_number order)
  2. Store answer in DB
  3. Evaluate answer asynchronously (fire-and-forget ok)
  4. Get next question or signal completion
  5. Return { next_question, progress, is_complete }
- Method: get_current_question(db, session_id: str) → InterviewQuestion | None

=== evaluator.py ===
Class ResponseEvaluator:
- Method: evaluate_answer(question: InterviewQuestion, answer_text: str) → EvaluationResult
  Uses EVALUATION_PROMPT → returns score, feedback, strengths, gaps
- Method: generate_session_report(session_id: str, db) → SessionReport
  Aggregates all Q&A pairs → REPORT_GENERATION_PROMPT → full report
  Includes: per-topic scores, overall recommendation, skill gap analysis
```

---

### PHASE 5 — FastAPI Routes & Main
**Goal:** All API endpoints wired together.

```
Implement all FastAPI routes in backend/api/routes/ and backend/main.py

=== api/dependencies.py ===
- get_db() → AsyncGenerator for SQLAlchemy session
- get_question_generator() → singleton QuestionGenerator
- get_session_manager() → singleton InterviewSessionManager  
- get_evaluator() → singleton ResponseEvaluator

=== api/routes/resume.py ===
POST /api/v1/resume/parse
- Accept: multipart/form-data with file (PDF) + role (str)
- Parse with ResumeParser
- Return: ResumeDataResponse
- Validation: file must be PDF, max 5MB

=== api/routes/sessions.py ===
POST /api/v1/sessions
Body: { candidate_name, role, resume_text, skills_extracted }
Response: { session_id, role, status, created_at }

GET /api/v1/sessions/{session_id}
Response: Full session with questions and answers

=== api/routes/interview.py ===
POST /api/v1/interview/start
Body: { session_id }
Response: { session_id, question: {id, text, number, topic, difficulty}, total_questions }

POST /api/v1/interview/answer
Body: { session_id, question_id, answer_text }
Response: { answered: true, next_question | null, progress: {current, total}, is_complete }

=== api/routes/reports.py ===
GET /api/v1/sessions/{session_id}/report
Response: Full SessionReport with scores, insights, Q&A transcript

=== main.py ===
- Create FastAPI app with title "PGAGI Interview System API"
- Mount all routers with prefix /api/v1
- CORS: allow origins from config.CORS_ORIGINS
- On startup: call database create_all(), log ChromaDB stats
- Global exception handler returning { success: false, error: str }
- Health check: GET /health → { status: "ok", db: "ok", chroma: "ok" }
- Add request logging middleware

All routes must:
- Return wrapped response { success: bool, data: ..., error: str|null }
- Use Depends() for all injected services
- Have proper HTTP status codes (422 for validation, 404 for not found, 500 for server errors)
- Include docstrings for OpenAPI docs
```

---

### PHASE 6 — Frontend Foundation
**Goal:** Types, API client, Zustand store.

```
Set up the frontend data layer in frontend/lib/

=== lib/types.ts ===
Define all TypeScript interfaces matching backend Pydantic schemas:
- ResumeData, InterviewSession, InterviewQuestion, InterviewAnswer
- StartInterviewResponse, SubmitAnswerResponse, SessionReport
- ApiResponse<T> wrapper: { success: boolean, data: T, error: string | null }
- Role enum: "aiml_engineer" | "backend_engineer" | "data_scientist"
- RoleConfig: { value: Role, label: string, description: string, icon: string }
- Define AVAILABLE_ROLES constant array with all 3 roles + metadata

=== lib/api.ts ===
Create typed API client using axios with:
- Base URL from NEXT_PUBLIC_API_URL env var (default http://localhost:8000)
- All API calls match backend routes exactly
- Functions: parseResume, createSession, startInterview, submitAnswer, getReport
- Error extraction from ApiResponse wrapper
- Proper TypeScript return types for all functions
- Request/response logging in development mode

=== lib/store.ts ===
Zustand store for interview state:
State shape:
  - phase: "setup" | "in_progress" | "completed"
  - sessionId: string | null
  - resumeData: ResumeData | null
  - selectedRole: Role | null
  - currentQuestion: InterviewQuestion | null
  - questionIndex: number
  - totalQuestions: number
  - answers: Record<string, string> (questionId → answerText)
  - isSubmitting: boolean

Actions: setPhase, setSession, setResumeData, setRole, setCurrentQuestion, 
         recordAnswer, setSubmitting, resetInterview

=== app/layout.tsx ===
Wrap with QueryClientProvider (React Query) + custom ThemeProvider
Clean dark/light mode support with next-themes
Professional font: use Geist Sans (already in Next.js 14)
```

---

### PHASE 7 — Frontend UI Components
**Goal:** All React components with polished UI.

```
Build all frontend components in frontend/components/

Design direction: Clean, professional, "technical recruiter dashboard" aesthetic.
Dark background (#0f0f0f), accent color electric blue (#3B82F6), 
clean monospace font for code elements, card-based layout.

=== ResumeUpload.tsx ===
Drag-and-drop PDF uploader:
- Use react-dropzone
- Show file name + size after upload  
- Upload progress indicator (axios onUploadProgress)
- Parse resume on drop → show extracted skills as badges
- Skills shown as colored tags: blue for languages, green for frameworks, purple for ML
- Error states: "Invalid file type" / "File too large" / "Parse failed"
- Animate in extracted skills with staggered fade

=== RoleSelector.tsx ===
Role selection card grid:
- 3 cards: AI/ML Engineer, Backend Engineer, Data Scientist
- Each card: icon (lucide), title, description, skill tags, "Select" button
- Selected state: electric blue border + checkmark
- Hover: subtle scale transform

=== InterviewChat.tsx ===
Main interview interface:
- Left panel (60%): Question display + answer textarea
- Right panel (40%): Interview progress + context
- Progress bar at top showing question N of M
- Question card with topic badge + difficulty badge
- Large textarea for answer (min-height 200px, auto-grows)
- Submit button with loading spinner
- Timer showing time on current question
- Previous questions collapsed in accordion below

=== QuestionCard.tsx ===
Individual question display:
- Question number badge
- Topic chip (e.g. "Gradient Descent", "System Design")  
- Difficulty indicator: colored dots (green/yellow/red)
- Question text in large readable font
- Subtle entrance animation (fade + slide up)

=== ProgressBar.tsx ===
Visual progress through interview:
- Circular progress indicator OR segmented bar
- Shows "Question 3 of 8"
- Color transitions green→yellow→orange as interview progresses

=== ReportView.tsx ===
Final report display:
- Overall score as large circular gauge (SVG, animated fill)
- Recommendation badge: "Strong Hire" / "Hire" / "No Hire"
- Skill breakdown: radar chart or bar chart (use recharts)
- Full Q&A transcript accordion (each item expandable)
- Per-answer scores with color coding
- Strengths + gaps as styled lists
- "Start New Interview" CTA button

All components must:
- Be fully TypeScript typed (no `any`)
- Have loading + error + empty states
- Be keyboard accessible
- Work in both light and dark mode via Tailwind dark: classes
```

---

### PHASE 8 — Frontend Pages
**Goal:** Wire pages together with routing and data flow.

```
Build all Next.js app pages in frontend/app/

=== app/page.tsx (Landing) ===
Hero section: "AI-Powered Technical Interviews"
Sub: "Intelligent questions tailored to your background"
Single CTA: "Start Interview" → /interview/setup
Background: subtle grid pattern or animated gradient
Show 3 feature cards: "Resume-Aware", "RAG-Powered", "Instant Insights"

=== app/interview/setup/page.tsx ===
Two-step setup flow:
Step 1: ResumeUpload component
  - On successful parse: show extracted profile preview (name, skills, experience)
  - "Looks good? Continue" button → step 2

Step 2: RoleSelector component
  - After role selected: "Start Interview" button
  - On click: call createSession + startInterview → redirect to /interview/[sessionId]
  
Use Zustand to persist resumeData + selectedRole between steps
Show loading overlay during API calls

=== app/interview/[sessionId]/page.tsx ===
Dynamic route for active interview:
- On mount: check Zustand store for currentQuestion
- If no current question in store: call GET /sessions/{sessionId} to restore state
- Render InterviewChat component
- On answer submit:
  1. Set isSubmitting = true
  2. Call submitAnswer API
  3. If next_question: update store + animate question transition
  4. If is_complete: redirect to /interview/[sessionId]/report
- Handle page refresh gracefully (restore from API)
- Prevent accidental navigation with beforeunload warning

=== app/interview/[sessionId]/report/page.tsx ===
- Fetch report from GET /sessions/{sessionId}/report
- Render ReportView component
- Loading skeleton while fetching
- Error state with retry button
- Share/download report (optional: jsPDF export)

Add proper Next.js metadata (title, description) to all pages.
Add loading.tsx files for each route segment.
```

---

### PHASE 9 — Knowledge Base Ingestion Script
**Goal:** One-command ingestion of ML books into ChromaDB.

```
Create backend/knowledge_base/ingest_script.py

This is a standalone script (not part of FastAPI) that:
1. Reads all PDF files from knowledge_base/raw/ directory
2. Maps each book to the correct role based on filename:
   - "mitchell*" or "hundred*" or "beginners*" → role: "aiml_engineer"  
   - "introduction*python*" or "brownlee*" → role: "data_scientist"
   - "bishop*" or "deep_learning*" → role: "advanced" (added to both above)
3. For each role, instantiates KnowledgeBaseIngestor
4. Calls ingest_for_role() with all matching PDFs
5. Prints progress: "Ingesting: <filename> → <role> ... done (N chunks)"
6. At end: prints summary table of chunks per role per collection
7. Creates knowledge_base/ingestion_log.json with metadata

Also create knowledge_base/README.md explaining:
- Where to download each book (PDF links from assignment)
- How to run: `cd backend && uv run python knowledge_base/ingest_script.py`
- Expected output (chunk counts per book)

The script should be idempotent: if a collection already exists, ask user to confirm re-ingestion or skip.
Use tqdm for progress bars on chunk processing.
```

---

### PHASE 10 — README, Docker, Final Polish
**Goal:** Production-ready documentation and easy setup.

```
Create the final project documentation and setup files.

=== README.md (root) ===
Structure:
1. Project overview + screenshot placeholder
2. Architecture diagram (ASCII or mermaid code block)
3. Tech stack table
4. Prerequisites (Python 3.11+, Node 18+, pnpm, uv)
5. Setup instructions:
   a. Clone + .env setup
   b. Download knowledge base PDFs (with links)
   c. Backend: `cd backend && uv sync && uv run python knowledge_base/ingest_script.py`
   d. Backend: `uv run uvicorn main:app --reload`
   e. Frontend: `cd frontend && pnpm install && pnpm dev`
6. Key Design Decisions section:
   - Why ChromaDB over Pinecone (zero-infra for demo, persistent local storage)
   - Why chunk_size=800 with overlap=150 (preserves sentence context, ML textbooks are dense)
   - Why questions generated upfront vs on-demand (consistent session experience, avoids latency mid-interview)
   - Why all-MiniLM-L6-v2 (small, fast, great semantic similarity, runs without GPU)
7. API documentation link (http://localhost:8000/docs)
8. Known limitations + future improvements

=== docker-compose.yml ===
Services:
- backend: Python FastAPI, port 8000, mounts knowledge_base volume
- frontend: Next.js, port 3000
- Both depend on each other's health checks

=== .env.example ===
All required env vars with placeholder values and inline comments explaining each.

=== backend/tests/ ===
Write minimal but real tests (not mocks):
- test_resume_parser.py: test with a synthetic resume string
- test_rag.py: test retriever returns non-empty results (requires ingested data)
- test_api.py: test /health endpoint + /resume/parse with a small PDF

Add pyproject.toml [tool.pytest] configuration.
Add Makefile with commands: make backend, make frontend, make ingest, make test
```

---


