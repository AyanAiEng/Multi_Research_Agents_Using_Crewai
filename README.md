# Multi-Agent AI Research Assistant

A production-grade AI research system that uses **5 specialized CrewAI agents** powered by a **local LLM (Ollama + Qwen2.5-7B)** to generate investor-grade business analysis reports for any product idea. The backend runs on **Google Colab** (free T4 GPU) and is exposed via **ngrok** to a **Streamlit** frontend running on your PC.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR PC                                  │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Streamlit Frontend (app.py)             │   │
│   │                                                      │   │
│   │   User enters product idea ──► Sends POST request    │   │
│   │   Displays 6 report tabs  ◄── Receives JSON response  │   │
│   │   Download buttons for each section                  │   │
│   └──────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│                      │ HTTPS (ngrok tunnel)                  │
│                      │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   GOOGLE COLAB (T4 GPU)                      │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              FastAPI Backend (main.py)                │   │
│   │                                                      │   │
│   │   POST /generate-report ──► CrewAI Pipeline          │   │
│   │   GET  /                  ──► Health check           │   │
│   │   GET  /validate           ──► System validation     │   │
│   └──────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│   ┌──────────────────▼──────────────────────────────────┐   │
│   │           Ollama (Qwen2.5-7B-Instruct)              │   │
│   │                                                      │   │
│   │   - Runs locally on Colab T4 GPU                    │   │
│   │   - No API key needed, no rate limits               │   │
│   │   - ~4.7GB model, tool-calling support              │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  ngrok Tunnel                        │   │
│   │                                                      │   │
│   │   localhost:8000 ──► https://xxxx.ngrok-free.dev    │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## How It Works

When you submit a product idea, 5 AI agents work **sequentially**, each building on the previous agent's output:

| Step | Agent | Output |
|------|-------|--------|
| 1 | **Market Research Specialist** | TAM/SAM/SOM, market trends, growth rates, regulatory landscape |
| 2 | **Competitive Intelligence Analyst** | Direct/indirect competitors, SWOT, market gaps, competitive moats |
| 3 | **Customer Insights Researcher** | User personas, buying journey, switching costs, segment ranking |
| 4 | **Product Strategy Advisor** | MVP features (MoSCoW), pricing, 3-phase roadmap, go-to-market |
| 5 | **Business Analyst** | Go/No-Go verdict, 3-year projections, unit economics, risk matrix |

Each agent receives the outputs of all previous agents as context, producing increasingly refined and synthesized analysis. The final agent delivers an investor-grade business verdict.

---

## Project Structure

```
├── main.py                  # Complete backend (Ollama + CrewAI + FastAPI + ngrok)
├── app.py                   # Streamlit frontend
├── agents.yaml              # Agent definitions (reference file)
├── task.yaml                # Task definitions (reference file)
├── .env                     # Environment variables (TAVILY_API_KEY, NGROK_TOKEN)
├── README.md                # This file
└── outputs/                 # Generated reports (created at runtime)
    └── run_YYYYMMDD_HHMMSS_<idea>/
        ├── 01_market_research.md
        ├── 02_competitive_intelligence.md
        ├── 03_customer_insights.md
        ├── 04_product_strategy.md
        ├── 05_business_analysis.md
        └── final_report.md
```

---

## Prerequisites

### Backend (Google Colab)
- A Google account with access to [Google Colab](https://colab.research.google.com)
- A free ngrok account and auth token from [ngrok.com](https://ngrok.com)
- (Optional) A [Tavily](https://tavily.com) API key for web search

### Frontend (Your PC)
- Python 3.9+ installed
- Streamlit installed: `pip install streamlit requests`

---

## Setup

### Step 1: Backend on Google Colab

1. Open [Google Colab](https://colab.research.google.com) and create a new notebook
2. Make sure **GPU is enabled**: Runtime > Change runtime type > T4 GPU
3. Open the notebook `Multi_Research_Agent_Using_Crewai.ipynb` and run all cells in order:

| Cell | What it does |
|------|-------------|
| 0 | Installs zstd (dependency for Ollama) |
| 1 | Verifies zstd |
| 2 | Installs Ollama |
| 3 | Starts Ollama server on 0.0.0.0:11434 |
| 4 | Downloads Qwen2.5-7B model (~4.7GB, one-time) |
| 5 | Tests the model with a quick prompt |
| 6 | Installs Python packages (crewai, fastapi, etc.) |
| 7 | Installs tavily-python (for web search tool) |
| 8 | Imports all Python libraries |
| 9 | Sets configuration constants |
| 10 | Creates output directory |
| 11 | Defines `setup_ollama()` function |
| 12 | Defines all 5 agents with detailed backstories |
| 13 | Defines all 5 tasks with detailed descriptions |
| 14 | Defines `build_llm()` function |
| 15 | Defines `build_tools()` function (Tavily if key exists) |
| 16 | Defines `build_crew()` function (agents + tasks + context chaining) |
| 17 | Defines `run_research()` function (pipeline runner) |
| 18 | Creates FastAPI app and Pydantic models |
| 19 | Defines `GET /` health endpoint |
| 20 | Defines `GET /validate` endpoint |
| 21 | Defines `POST /generate-report` endpoint |
| 22 | Defines CLI mode function |
| 23 | Defines `start_ngrok()` function |
| 24 | Starts Ollama check, ngrok tunnel, and uvicorn server |

4. When Cell 24 finishes, you will see output like:
   ```
   Ollama already running.
   
   Ngrok URL: https://xxxx-yyyy-zzzz.ngrok-free.dev
   Paste this URL into your Streamlit app.
   
   Server:   http://localhost:8000
   Docs:     http://localhost:8000/docs
   Validate: http://localhost:8000/validate
   Public:   https://xxxx-yyyy-zzzz.ngrok-free.dev
   
   INFO:     Started server process [571]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

5. **Copy the ngrok URL** (the `https://xxxx.ngrok-free.dev` one)

### Step 2: Configure the Frontend

Open `app.py` and find this line (around line 35):

```python
value=os.getenv("API_URL", "https://transgressive-archimedes-vixenly.ngrok-free.dev"),
```

Replace the URL with your current ngrok URL from Step 1.

### Step 3: Run the Frontend

On your PC, open a terminal and run:

```bash
streamlit run app.py
```

A browser window will open at `http://localhost:8501`. The sidebar will show a green "Status: ok" if the backend is reachable.

---

## Usage

1. Open the Streamlit app in your browser
2. Enter a product idea in the text input (be specific about the target user and problem)
3. Click **Generate Report**
4. Wait 5-15 minutes (each agent takes 1-3 minutes on a T4 GPU)
5. View results in 6 tabs:
   - **Final Business Report** - The final synthesized verdict
   - **Market Research** - Market size, trends, regulatory analysis
   - **Competitive Intelligence** - Competitor profiles, SWOT, gaps
   - **Customer Insights** - Personas, buying journey, switching costs
   - **Product Strategy** - MVP features, pricing, roadmap, GTM
   - **Business Analysis** - Go/No-Go, projections, risks, unit economics
6. Download any section as a `.md` file using the download buttons

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check - returns LLM status, model info, Tavily status |
| `GET` | `/validate` | System validation - checks Ollama, model, agents, tasks |
| `POST` | `/generate-report` | Main endpoint - runs the 5-agent pipeline |

### POST /generate-report

**Request body:**
```json
{
  "product_idea": "an AI-powered compliance copilot for fintech startups",
  "verbose": false
}
```

**Response:**
```json
{
  "product_idea": "an AI-powered compliance copilot for fintech startups",
  "final_report": "...",
  "market_research": "...",
  "competitive_intelligence": "...",
  "customer_insights": "...",
  "product_strategy": "...",
  "business_analysis": "...",
  "generated_at": "2025-01-15T10:30:00+00:00",
  "output_path": "/content/outputs/run_20250115_103000_..."
}
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TAVILY_API_KEY` | No | Tavily API key for web search. If not set, agents run without web search. Set it in Colab Secrets or directly in Cell 15. |
| `NGROK_TOKEN` | Yes | Your ngrok authtoken from ngrok.com. Hardcoded in Cell 23. |
| `OLLAMA_HOST` | No | Ollama server URL. Defaults to `http://localhost:11434`. |
| `PORT` | No | FastAPI server port. Defaults to `8000`. |

---

## Tavily Web Search Setup (Optional)

If you want agents to search the web for real-time data:

1. Create a free account at [tavily.com](https://tavily.com)
2. Get your API key from the dashboard
3. In Google Colab, go to Secrets (key icon in the sidebar)
4. Add a new secret: Name = `TAVILY_API_KEY`, Value = `tvly-xxxxx`
5. The `build_tools()` function in Cell 15 automatically reads it from Colab Secrets

Without Tavily, agents rely entirely on the LLM's training knowledge (Qwen2.5-7B, knowledge up to late 2024).

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Qwen2.5-7B-Instruct via Ollama | Local inference, no API costs |
| Agent Framework | CrewAI | Multi-agent orchestration |
| Backend API | FastAPI + Uvicorn | REST API endpoints |
| Tunnel | ngrok | Expose Colab localhost to the internet |
| Frontend | Streamlit | Web UI with tabs and download buttons |
| GPU | Google Colab T4 (free) | GPU acceleration for LLM inference |

---

## Troubleshooting

### "Ollama not reachable"
- Make sure Cell 3 (start Ollama) ran successfully
- Check with `!ollama list` in a new cell
- If Colab disconnected, re-run Cells 3, 24

### "Qwen2.5-7B not found"
- Re-run Cell 4: `!ollama pull qwen2.5:7b`
- The model download is ~4.7GB and takes a few minutes

### ngrok URL not working from Streamlit
- The ngrok URL changes every time Colab restarts. Get the new URL from Cell 24 output
- Update the URL in `app.py` (line 35) or in the Streamlit sidebar
- Free ngrok tunnels may show a warning page on first visit - click "Visit Site"

### "Backend not reachable" in Streamlit
- Colab session may have disconnected. Re-open Colab and re-run Cell 24
- Check if the ngrok URL in Streamlit matches the one in Colab

### "asyncio.run() cannot be called from a running event loop"
- Make sure Cell 24 uses `await server.serve()` instead of `uvicorn.run()`
- The Colab notebook provided uses the correct async pattern

### Pipeline takes too long
- Local LLM on T4 GPU generates ~5-10 tokens/sec
- Each agent produces 500-1000 words, taking 1-3 minutes
- Total pipeline: 5-15 minutes for all 5 agents
- Enable "Verbose agent logs" checkbox to see progress in Colab

### TavilySearchTool auto-install error
- Make sure Cell 7 (`!pip install tavily-python`) ran successfully
- If using Colab Secrets, the key is read automatically in Cell 15
- Without the key, the system works fine (just no web search)

### Report quality is low
- Be specific in your product idea (mention target user, industry, problem)
- Qwen2.5-7B is a capable but smaller model — for better quality, try `qwen2.5:14b` if Colab RAM allows
- Enable Tavily web search for real-time data

---

## Cost

Everything runs on **free tiers**:

| Service | Cost |
|---------|------|
| Google Colab T4 GPU | Free |
| Ollama + Qwen2.5-7B | Free (local) |
| CrewAI | Free (open source) |
| ngrok | Free tier (1 tunnel, some limitations) |
| Tavily | Free tier (1000 searches/month) |
| **Total** | **$0/month** |

---

## Important Notes

- The ngrok URL **changes every time** Colab restarts. You need to update the URL in `app.py` or the Streamlit sidebar each time.
- Colab sessions **disconnect after ~90 minutes** of inactivity (or 12 hours max). When this happens, re-run Cells 3 and 24.
- The Qwen2.5-7B model stays downloaded in Colab's temporary storage. Re-downloading is only needed if Colab resets the runtime.
- FastAPI endpoints are documented at `{ngrok_url}/docs` (Swagger UI) — useful for testing without Streamlit.