# 🤖 Agronexus AI Chatbot

A production RAG chatbot for **Agronexus Trading Co.** — answers buyer questions about spice products, pricing, and shipping using OpenAI GPT + LangChain + FAISS.

🔗 **Live Demo:** [agronexus-chatbot.vercel.app](https://agronexus-chatbot.vercel.app)
📦 **Backend API:** [agronexus-chatbot.onrender.com](https://agronexus-chatbot.onrender.com)

---

## Architecture

```
Customer Question → React Frontend → Flask API → LangChain RAG Pipeline
                                                    ↓              ↓
                                              FAISS Vector DB   OpenAI GPT
                                                    ↓
                                              Answer returned
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Axios, Vite |
| Backend | Python, Flask, Flask-CORS |
| AI / LLM | OpenAI GPT-4o-mini via OpenRouter |
| RAG | LangChain 0.1.20, FAISS vector store |
| Embeddings | OpenAI text-embedding-3-small |
| Deployment | Render (backend), Vercel (frontend) |

## Features

- RAG pipeline — answers grounded in real Agronexus business data
- Conversational memory — remembers context across conversation
- Custom knowledge base — products, pricing, shipping, FAQ
- Production deployed — zero downtime on Render + Vercel

## Run Locally

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY=sk-or-v1-your-openrouter-key
export OPENAI_API_BASE=https://openrouter.ai/api/v1
export OPENAI_EMBEDDING_KEY=sk-proj-your-openai-key

python rag.py   # build knowledge base (run once)
python app.py   # start server on :5000

# Frontend
cd frontend && npm install
echo "VITE_API_URL=http://localhost:5000" > .env.local
npm run dev     # runs on :5173
```

## Project Structure

```
docs: add comprehensive README with architecture, setup, and deployment├── backend/
│   ├── app.py           # Flask REST API
│   ├── rag.py           # RAG pipeline + embeddings
│   ├── requirements.txt
│   └── knowledge/
│       ├── products.txt
│       ├── pricing.txt
│       └── faq.txt
└── frontend/
    └── src/App.jsx      # Chat UI
```

## Environment Variables

| Variable | Value |
|---|---|
| OPENAI_API_KEY | OpenRouter key (chat) |
| OPENAI_API_BASE | https://openrouter.ai/api/v1 |
| OPENAI_EMBEDDING_KEY | OpenAI key (embeddings) |

---

**Author:** [Anurag Bishnoi](https://bishnoianurag.site) · [LinkedIn](https://linkedin.com/in/anuragbishnoi)
