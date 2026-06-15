# Phase-Wise Implementation Plan

This document outlines the step-by-step implementation plan for the Automated Weekly App Review Pulse for the Groww app. It is based on the system architecture and requirements defined in the problem statement.

---

## Phase 1: Project Setup and Infrastructure
**Goal:** Establish the foundation, repository structure, and core execution mechanisms.
- **1.1 Repository Initialization:** Set up the project structure for the main agent, ingestion scripts, and MCP servers.
- **1.2 CLI Foundation:** Build the command-line interface (CLI) to trigger runs manually (e.g., specifying ISO week and product).
- **1.3 Orchestration & Logging:** Implement the basic scheduling stub (e.g., cron) and configure structured logging to ensure auditability (tracking run IDs, timestamps, and parameters).

## Phase 2: Data Ingestion (Google Play Store)
**Goal:** Successfully extract raw review data for the Groww app.
- **2.1 Scraper Development:** Build or integrate a scraper to fetch reviews from the Google Play Store for the Groww app.
- **2.2 Time-Window Filtering:** Implement logic to filter reviews strictly for the last 8–12 weeks.
- **2.3 Data Normalization:** Filter out noise (emojis, non-English text, short reviews) and standardize the extracted data into a strict schema keeping only (`Rating`, `Text`). Metadata like `Review ID`, `Date`, etc. are explicitly stripped to reduce noise. Save this locally or pass it in-memory to the next module.

## Phase 3: Reasoning & Analysis Engine
**Goal:** Process raw reviews into themes, quotes, and actionable ideas using machine learning and LLMs.
- **3.1 PII Scrubbing (Local):** Implement local sanitization (e.g., Presidio/Regex) to strip PII from review text. This preserves LLM rate limits for the final summarization.
- **3.2 Embeddings Generation (Local):** Use a local, lightweight embedding model (e.g., `sentence-transformers` via HuggingFace) rather than an API, to avoid burning Groq API token limits on embeddings.
- **3.3 Clustering (Local):** Run density-based clustering (e.g., UMAP + HDBSCAN) locally to group reviews into distinct thematic clusters.
- **3.4 LLM Summarization (Groq API):** Use the `llama-3.3-70b-versatile` model via Groq. **Critical constraint:** Groq limits are 30 RPM and 12K TPM. To respect this:
  - Implement token counting before sending prompts to ensure the combined prompt + completion stays well under 12K TPM.
  - Process clusters sequentially with rate-limiting (delays) to respect the 30 RPM limit.
  - If a cluster's reviews exceed the token limit, sample only the top N most representative reviews (those closest to the cluster centroid) to ensure the request succeeds.
- **3.5 Quote Validation:** Build a strict validation function to cross-check LLM-selected quotes against the raw review text to prevent hallucination.

## Phase 4: Output Generation & Formatting
**Goal:** Convert the raw JSON insights from the reasoning engine into human-readable formats.
- **4.1 Docs Formatter:** Create a module that takes the themes, quotes, and actions and formats them into a clean Markdown/HTML structure for Google Docs.
- **4.2 Email Formatter:** Create a lightweight "teaser" template for the Gmail output that includes bullet points of top themes and a placeholder for the deep link.

## Phase 5: Custom MCP Server Development (FastAPI)
**Goal:** Build a complete MCP-style server in Python that integrates with Google Docs and Gmail using FastAPI.

**Directory Structure:**
`google-mcp-server/`
- `server.py`: FastAPI app exposing two POST endpoints (`/append_to_doc`, `/create_email_draft`). Implements an interactive terminal approval (`Approve? (y/n)`) before executing any action.
- `auth.py`: Google OAuth 2.0 authentication requesting Docs and Gmail scopes. Handles loading/saving `credentials.json` and `token.json`.
- `docs_tool.py`: Contains `append_to_doc(doc_id, content)` using the Google Docs API.
- `gmail_tool.py`: Contains `create_email_draft(to, subject, body)` using the Gmail API.
- `requirements.txt`: Dependencies (`fastapi`, `uvicorn`, `google-auth-oauthlib`, `google-api-python-client`).
- `README.md`: Instructions for setup, creating OAuth credentials, and running the server.

> [!WARNING]  
> **Interactive Prompts in FastAPI**
> You requested an interactive `Approve? (y/n)` prompt inside the server before taking action. I will implement this by using a synchronous endpoint or running `input()` in a thread so it doesn't crash the async event loop. Since the server runs in the terminal, the terminal will hang and wait for your `y` or `n` input for every single request. Is this acceptable?

## Phase 6: Integration and End-to-End Testing
**Goal:** Connect all modules and ensure the system runs seamlessly from end to end.
- **6.1 Pipeline Assembly:** Wire the Ingestion -> Reasoning -> Formatting -> MCP Delivery flow together.
- **6.2 CLI Backfill Testing:** Test the CLI to generate reports for historical ISO weeks and ensure idempotency holds up.
- **6.3 Staging Run:** Run the entire system in "draft-only" mode for email and verify the Google Doc append behavior. Review the generated deep links to ensure they correctly navigate to the new Doc section.

## Phase 7: Deployment and Handoff
**Goal:** Move the system to a production environment.
- **7.1 Production Configuration:** Securely deploy the MCP servers with production credentials.
- **7.2 Scheduler Activation:** Activate the weekly scheduled cron job (e.g., Monday morning IST).
- **7.3 Documentation:** Finalize READMEs and operational runbooks for maintaining the scraper, updating LLM prompts, and handling backfills.
