# buildwithgemini-us-travel-planner — Conversational US Road-Trip & Motorcycle Planner

> **Note:** This project was coded as part of a Qwiklabs demo using the gcloud shell environment and has not been tested via a local run on macOS. YMMV.

Production-grade **Google ADK + Gemini 2.5** conversational agent that plans multi-day US road trips
and motorcycle routes: live rental lookup via Firestore, trip budget sandboxing, RAG-backed travel
guidelines, real-time AI-generated destination photography, and full A2A protocol support. Deployed
on Vertex AI Agent Runtime with a Cloud Run frontend.

![Zion National Park](https://storage.googleapis.com/us-travel-planner-media-qwiklabs-04/stock/zion_national_park.jpg)

## Live Service

| Endpoint | URL |
|---|---|
| **Frontend (Cloud Run)** | https://us-travel-planner-frontend-313999655048.us-east1.run.app |
| **Local dev server** | `http://localhost:8085` (FastAPI proxy + chat UI) |
| **Agent Runtime ID** | `projects/313999655048/locations/us-east1/reasoningEngines/4212783199870255104` |
| **Media bucket** | `gs://us-travel-planner-media-qwiklabs-04` (public read) |

---

## Using the App

1. **Plan a trip** — describe your dates, departure city, riding experience, and budget. The agent retains preferences across sessions via Vertex AI Memory Bank.
2. **Route lookup** — ask for a specific highway (Scenic Byway 12, Zion Mount Carmel, Route 66, Grand Canyon South Rim) to get mileage, difficulty, waypoints, and season.
3. **Rental search** — query available motorcycles by city and type (Cruiser, Adventure Touring) from the Firestore `motorcycle_rentals` collection.
4. **Budget estimation** — the sandbox code executor computes itemized trip costs: rental, fuel (45 MPG × $3.85/gal), lodging tier, meals, and park passes.
5. **Destination imagery** — the agent calls `generate_destination_image` / `generate_domain_item_image` (gemini-3.1-flash-lite-image) and returns a public GCS-hosted photo URL inline.
6. **Travel guidelines** — `consult_travel_instructions` queries the Vertex AI RAG corpus seeded from `rag/instructions.txt` for speed limits, operating hours, and park rules.

### Sample prompt

> "Plan a 7-day motorcycle road trip from Salt Lake City or Las Vegas covering Utah's Scenic Byway 12 and the Grand Canyon, including local motorcycle rental options and daily riding distance breakdowns under $2,500."

---

| Area | Stack / Detail |
|---|---|
| **Agent framework** | Google ADK — `Agent`, `App`, `Runner`; `PreloadMemoryTool` injects cross-session facts on every turn |
| **Model** | gemini-3.6-flash (conversation + tool routing); gemini-3.1-flash-lite-image (image generation) |
| **Session & memory** | Vertex AI Session Service + Vertex AI Memory Bank (cross-session user preference recall) |
| **Code execution** | `AgentEngineSandboxCodeExecutor` — Python sandbox on the Reasoning Engine for budget math |
| **RAG** | Vertex AI Serverless RAG corpus (`text-embedding-005`); `LlmParserConfig` with gemini-2.5-flash + custom extraction prompt; 512-token chunks, 100-token overlap |
| **Firestore** | `motorcycle_rentals` collection — city/type-filtered reads + upserts via ADK tools |
| **GCS** | Public bucket `us-travel-planner-media-qwiklabs-04`; subfolders: `generated_items/`, `postcards/`, `stock/`, `rag/` |
| **A2A protocol** | Full A2A JSON-RPC + agent-card endpoints via `a2a-sdk`; streaming + ADK executor extension |
| **Telemetry** | Cloud Trace, BigQuery, Cloud Logging (opt-in via `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY`) |
| **Frontend** | Mesop-based UI in `frontend/`; proxies chat to the FastAPI backend |
| **IaC** | Terraform in `deployment/terraform/single-project/` |

---

## Architecture

```
User browser
  └─ Cloud Run (Mesop frontend, us-east1)
       └─ HTTP proxy → FastAPI backend (local or Agent Runtime)
            ├─ /api/**           ADK web routes (adk_api)
            ├─ /a2a/app/**       A2A JSON-RPC + agent-card
            └─ /reasoning/**     Vertex AI Console Playground adapter

FastAPI (app/fast_api_app.py)
  └─ Runner (shared session / memory / artifact services)
       └─ root_agent  [gemini-3.6-flash]
            ├─ PreloadMemoryTool ──────────────────► Vertex AI Memory Bank
            ├─ get_weather / get_current_time        (in-process stubs)
            ├─ consult_travel_instructions ──────────► Vertex AI RAG Corpus (us-central1)
            │                                           gs://…/rag/instructions.txt
            ├─ list/get/add_motorcycle_rental ───────► Firestore (motorcycle_rentals)
            ├─ calculate_trip_budget ────────────────► AgentEngineSandbox (Python executor)
            ├─ get_scenic_route_highlights            (in-process route database)
            ├─ generate_destination_image ───────────► gemini-3.1-flash-lite-image
            │   └─ upload ──────────────────────────► GCS (postcards/)
            └─ generate_domain_item_image ───────────► gemini-3.1-flash-lite-image
                └─ save artifact + upload ──────────► GCS (generated_items/)

Vertex AI Agent Runtime (us-east1)
  └─ reasoningEngine/4212783199870255104
       ├─ Session Service   (cross-request session persistence)
       └─ Memory Bank       (cross-session user preference recall)
```

---

## Running

Install dependencies and launch the local playground:

```bash
uvx google-agents-cli setup
```

```bash
agents-cli install
```

```bash
agents-cli playground
```

Open `http://localhost:8085` to chat with the agent.

### Key commands

| Command | What it does |
|---|---|
| `agents-cli playground` | Local dev server with hot-reload |
| `agents-cli eval` | Run eval suite (`tests/eval/`) |
| `uv run pytest tests/unit tests/integration` | Unit + integration tests |
| `agents-cli deploy` | Deploy/update agent on Vertex AI Agent Runtime |
| `agents-cli publish gemini-enterprise` | Register with Gemini Enterprise via A2A |
| `agents-cli scaffold enhance` | Add CI/CD pipelines + Terraform infra |
| `python scripts/create_rag_corpus.py` | (Re)create and seed the RAG corpus |
| `python scripts/seed_firestore.py` | Seed the Firestore `motorcycle_rentals` collection |

---

## Cost

| Resource | Cost |
|---|---|
| **Vertex AI Agent Runtime** | Per-invocation (Reasoning Engine); ~$0 when idle |
| **Cloud Run frontend** | Scale-to-zero; negligible at demo traffic levels |
| **Firestore** | Free tier covers demo-scale read/write |
| **Vertex AI RAG** | Serverless mode — pay per query, no always-on node |
| **GCS media bucket** | ~$0.02/GB/month; demo volume is negligible |
| **Gemini image model** | Per-image generation call |

---

## Key Design Decisions

| Concern | Approach |
|---|---|
| **Cross-session memory** | `PreloadMemoryTool` injects recalled user facts (budget, riding level, departure city) into every turn — no explicit "remember this" prompt needed |
| **Image delivery** | AI-generated images are uploaded to a public GCS bucket and returned as HTTPS URLs — no base64 in the chat response, frontend renders them inline |
| **RAG parsing** | `LlmParserConfig` with gemini-2.5-flash extracts structured travel rules from free-text docs, improving retrieval precision over naive chunking |
| **Sandbox budget math** | `AgentEngineSandboxCodeExecutor` runs Python arithmetic in an isolated environment — avoids hallucinated totals from pure LLM arithmetic |
| **Shared services** | `services.py` registers session, memory, and artifact services under `shared://` URIs so the ADK API, A2A path, and Reasoning Engine adapter share one consistent state |
| **A2A interoperability** | All agent capabilities are exposed on the A2A JSON-RPC path (`/a2a/app`), allowing other agents or Gemini Enterprise to call this agent as a sub-agent |
