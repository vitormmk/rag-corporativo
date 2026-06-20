"""
Backend do RAG Corporativo.
Esqueleto inicial: endpoints /health e /query com resposta mockada.
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Carrega variáveis do .env (que está na raiz do projeto, um nível acima)
load_dotenv(dotenv_path="../.env")


# === Modelos de dados (Pydantic) ===

class QueryRequest(BaseModel):
    """Request enviado pelo frontend ao endpoint /query."""
    pergunta: str
    assistente_id: str = "ti"  # default temporário; depois vira obrigatório


class QueryResponse(BaseModel):
    """Response devolvido pelo endpoint /query."""
    resposta: str
    fontes: list[str]
    confianca: str  # "alta", "baixa", "sem_resposta"
    assistente_id: str


# === Lifespan: executado no start/shutdown da aplicação ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    env = os.getenv("ENVIRONMENT", "development")
    print(f"[startup] backend iniciando em modo {env}")
    yield
    # Shutdown
    print("[shutdown] backend encerrando")


# === Aplicação ===

app = FastAPI(
    title="RAG Corporativo - Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: permite o frontend (Next.js em localhost:3000) chamar essa API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Endpoints ===

@app.get("/health")
async def health():
    """Endpoint de saúde. Usado pra verificar se o backend está no ar."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """
    Endpoint principal. Por enquanto retorna resposta mockada.
    Nas próximas fases vai incorporar auth, retrieval e LLM.
    """
    return QueryResponse(
        resposta=f"[mock] Você perguntou: '{req.pergunta}' ao assistente '{req.assistente_id}'.",
        fontes=[],
        confianca="alta",
        assistente_id=req.assistente_id,
    )
