<p align="center">
  <img src="frontend/public/shopassist_ai_logo.png" alt="ShopAssist AI" width="400">
</p>

<p align="center">
  <strong>AI-powered retail chatbot with RAG, real-time order tracking, and product recommendations.</strong>
</p>

<p align="center">
  <a href="https://shopassistai-web.azurewebsites.net">Live Demo</a> &nbsp;&bull;&nbsp;
  <a href="https://shopassist-api.azurewebsites.net/health">API Health</a> &nbsp;&bull;&nbsp;
  <a href="https://shopassist-api.azurewebsites.net/docs">API Docs</a>
</p>

---

A Retrieval-Augmented Generation (RAG) application that serves as an intelligent customer support assistant for retail businesses. It answers questions about store policies, products, and orders using semantic search and large language models.

## Overview

ShopAssist AI loads three data sources at startup -- a product catalog, an orders database, and a store policies document -- into an in-memory vector database. When a user asks a question, the system retrieves the most relevant context and generates a natural language response using Groq's Llama 3.3 70B model.

For order-related queries, the system implements a verification flow: it detects the intent, asks the customer for their Order ID, looks up the order by exact match, and responds with the relevant details.

## Architecture

```
                     +------------------+
                     |   React Frontend |
                     |   (Vite + Tailwind)
                     +--------+---------+
                              |
                         SSE Streaming
                              |
                     +--------+---------+
                     |  FastAPI Backend  |
                     +--------+---------+
                              |
              +---------------+---------------+
              |               |               |
     +--------+------+ +-----+-----+ +-------+-------+
     | ChromaDB      | | Groq API  | | Pandas        |
     | (Embeddings + | | (Llama    | | (Orders       |
     |  Policies &   | |  3.3 70B) | |  DataFrame)   |
     |  Products)    | |           | |               |
     +---------------+ +-----------+ +---------------+
```

**Frontend:** React 18, Vite, Tailwind CSS, Server-Sent Events for streaming responses.

**Backend:** FastAPI with lazy-loaded imports to minimize startup memory. Deferred loading of PyTorch, SentenceTransformers, and ChromaDB until first use.

**LLM:** Groq API (Llama 3.3 70B Versatile) for text generation. No local GPU required.

**Embeddings:** SentenceTransformers (all-MiniLM-L6-v2) running locally on CPU (~90 MB model).

**Vector Database:** ChromaDB (in-memory, ephemeral). All data is re-embedded on each backend restart.

**Orders:** Loaded into a Pandas DataFrame for exact-match lookup by Order ID. Not embedded.

## Project Structure

```
retail-data-copilot/
  app/
    app.py              FastAPI application with lifespan startup
    router.py           API endpoints (query, stream, retrieve, stats, PII)
    rag.py              RAG pipeline: embedding, retrieval, generation
    hf_client.py        Groq API client for LLM inference
    config.py           Centralized configuration and prompts
    data_loader.py      Auto-loads policies, products, orders at startup
    dbx_sql.py          PII masking utilities (Presidio)
  frontend/
    src/
      components/       React components (ChatWindow, Header, Sidebar, etc.)
      hooks/            Custom hooks (useChat for SSE streaming)
      api/              API client with SSE parser
    public/             Static assets (logo, favicon)
    index.html          Entry point
    vite.config.js      Vite configuration with API proxy
    tailwind.config.js  Tailwind CSS configuration
    Dockerfile          Multi-stage build (Node + Nginx)
    nginx.conf          Reverse proxy for API + SPA routing
  data/
    amazon_co-ecommerce_sample_retail_copilot.csv   Product catalog (26,280 items)
    ecommerce_orders_clean.csv                       Orders database (10,000 records)
    retail_polocies.txt                              Store FAQ and policies
  .env.example          Environment variables template
  requirements.txt      Python dependencies
  Dockerfile.backend    Backend container
  docker-compose.yml    Multi-service orchestration
  quickstart.sh         One-command setup and start script
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ or Bun (recommended for low-memory environments)
- A Groq API key (free at https://console.groq.com)

### 1. Clone and configure

```bash
git clone https://github.com/HaamzaHM/Shopassist-AI.git
cd retail-data-copilot
cp .env.example .env
```

Edit `.env` and add your API keys:

```
GROQ_API_KEY=gsk_your_groq_api_key_here
HUGGINGFACE_TOKEN=hf_your_token_here
```

### 2. Backend setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
bun install        # or: npm install
cd ..
```

### 4. Start the application

```bash
# Terminal 1: Start backend (auto-loads knowledge base on startup)
PYTHONUNBUFFERED=1 .venv/bin/python -m uvicorn app.app:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend && bun run dev
```

Or use the quickstart script:

```bash
chmod +x quickstart.sh
./quickstart.sh
```

The frontend runs at `http://localhost:3000` and the backend at `http://localhost:8000`.

### Docker deployment

```bash
docker-compose up --build
```

This starts both services. The frontend is served via Nginx on port 3000 and proxies API requests to the backend on port 8000.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/query | Non-streaming RAG query |
| POST | /api/query/stream | Streaming RAG query via SSE |
| POST | /api/retrieve | Retrieve documents without generation |
| GET | /api/stats | Knowledge base statistics |
| POST | /api/pii/mask | Mask PII in text |
| POST | /api/pii/analyze | Detect PII entities in text |
| GET | /health | Health check with KB status |

### Streaming query example

```bash
curl -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the return policy?", "n_results": 3, "temperature": 0.7}'
```

The response is a Server-Sent Events stream with three event types:
- `metadata` -- retrieved context documents (sent first)
- `token` -- individual text chunks as they are generated
- `done` -- signals end of stream, may include conversation context for multi-turn flows

## Technical Details

### Knowledge Base Loading

On startup, the FastAPI lifespan event triggers `auto_load_knowledge_base()` which:

1. Parses the policies TXT file by markdown headers (`##` and `###`), creating one document per Q&A section (~117 sections). Each sub-question is prefixed with its parent category for retrieval context.
2. Reads the products CSV and builds condensed summary strings (name, manufacturer, price, category, rating, stock). Embeds up to 5,000 products in batches of 500 to limit peak memory.
3. Loads the orders CSV into a Pandas DataFrame for exact-match lookups. Orders are not embedded.

### Order Verification Flow

The streaming endpoint handles three cases:

1. **Normal RAG** -- queries about policies or products are answered via ChromaDB retrieval.
2. **Order intent detected** -- if the query matches personal order keywords ("my order", "delivery status", "track my", etc.), the system asks for an Order ID.
3. **Order ID provided** -- the system extracts the UUID from the message, looks up the order in the DataFrame, and streams a response with order details as context.

Multi-turn state is managed via `conversation_context` passed in SSE `done` events and sent back with the next request.

### Memory Optimization

The application is designed to run on machines with 8 GB RAM:

- **Deferred imports**: PyTorch, SentenceTransformers, and ChromaDB are imported lazily on first use, not at module load time.
- **Batched embedding**: Products are embedded in batches of 500 to limit peak memory during ingestion.
- **Groq API for LLM**: No local GPU or large model download needed. Only the embedding model (~90 MB) runs locally.
- **Ephemeral ChromaDB**: In-memory storage avoids disk I/O overhead. Trade-off: data must be reloaded on restart.

### Frontend Architecture

- **SSE streaming**: The chat uses `fetch` + `ReadableStream` (not `EventSource`) because SSE requires POST requests.
- **Conversation context**: A `useRef` tracks the `conversation_context` from `done` events for multi-turn order verification.
- **Configurable settings**: Temperature, max tokens, and context document count are adjustable via the sidebar.
- **Markdown rendering**: Bot responses are rendered with `react-markdown` and `remark-gfm` for tables, lists, and code blocks.

### Updating Store Policies

The policies file (`data/retail_polocies.txt`) uses markdown formatting with `##` for categories and `###` for individual questions. To update policies:

1. Edit `data/retail_polocies.txt`
2. Restart the backend to reload the knowledge base

The parser automatically handles both markdown headers and legacy ALL CAPS formats.

## Configuration

All configuration is centralized in `app/config.py`. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| LLM_MODEL_ID | llama-3.3-70b-versatile | Groq model for text generation |
| EMBEDDINGS_MODEL_ID | all-MiniLM-L6-v2 | Local embedding model |
| PRODUCT_EMBED_LIMIT | 5000 | Max products to embed |
| PRODUCT_BATCH_SIZE | 500 | Embedding batch size |
| DEFAULT_TEMPERATURE | 0.7 | LLM sampling temperature |
| DEFAULT_N_RESULTS | 3 | Documents retrieved per query |

System prompts for both general RAG and order-specific responses are defined in `config.py` and can be edited without code changes.

## Troubleshooting

**Backend hangs on startup**: Ensure sufficient RAM is available. The embedding process requires ~4 GB peak. Close other memory-intensive applications.

**Policies not updating**: ChromaDB is in-memory. You must restart the backend after editing `data/retail_polocies.txt`.

**CORS errors in browser**: The backend allows all origins by default. If deploying behind a reverse proxy, ensure the proxy forwards the `Origin` header.

**SSE stream not working**: Check that no proxy or CDN is buffering the response. The backend sets `X-Accel-Buffering: no` and `Cache-Control: no-cache`.

**npm gets killed on low-memory machines**: Use Bun instead (`curl -fsSL https://bun.sh/install | bash`). It uses significantly less memory than npm.

## Deployment

The application is deployed on **Microsoft Azure** with CI/CD via GitHub Actions.

| Service | URL |
|---------|-----|
| Frontend | [shopassistai-web.azurewebsites.net](https://shopassistai-web.azurewebsites.net) |
| Backend API | [shopassist-api.azurewebsites.net](https://shopassist-api.azurewebsites.net/health) |
| API Documentation | [shopassist-api.azurewebsites.net/docs](https://shopassist-api.azurewebsites.net/docs) |

**Infrastructure:** Azure App Service (B2), Azure Container Registry, GitHub Actions for automated builds and deployments. Pushing to `main` triggers automatic deployment of both frontend and backend containers.

## Contact

**Hamza Malik** — feel free to reach out!

[![Email](https://img.shields.io/badge/Email-m.hamzamaliik%40gmail.com-red?style=flat&logo=gmail&logoColor=white)](mailto:m.hamzamaliik@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-hamzamaliik-blue?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hamzamaliik/)

## License

This project is licensed under the MIT License.
