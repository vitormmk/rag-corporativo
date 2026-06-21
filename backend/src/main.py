"""
Backend do RAG Corporativo.
Endpoint /query aplica retrieval com filtro de permissão e classifica
o nível de confiança baseado no score do melhor chunk recuperado.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.auth.dependencies import AuthenticatedUser, get_current_user
from src.auth.permissions import get_permissoes
from src.auth.users import authenticate
from src.config import ENVIRONMENT, RETRIEVAL_THRESHOLD_ALTA
from src.rag.assistentes import (
    ASSISTENTES,
    classificacoes_efetivas,
    get_assistente,
)
from src.rag.retrieval import buscar_chunks


# === Modelos ===

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    nome: str
    grupos: list[str]
    permissoes: list[str]


class AssistenteInfo(BaseModel):
    id: str
    nome: str
    descricao: str


class QueryRequest(BaseModel):
    pergunta: str
    assistente_id: str = "ti"


class FonteRecuperada(BaseModel):
    id: str
    texto: str
    fonte: str
    classificacao: str
    score: float


class QueryResponse(BaseModel):
    resposta: str
    fontes: list[FonteRecuperada]
    confianca: str
    assistente_id: str
    classificacoes_consultadas: list[str]
    debug: dict


# === Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[startup] backend iniciando em modo {ENVIRONMENT}")
    yield
    print("[shutdown] backend encerrando")


# === App ===

app = FastAPI(
    title="RAG Corporativo - Backend",
    version="0.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# === Endpoints públicos ===

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.4.0"}


@app.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    return LoginResponse(
        username=user.username,
        nome=user.nome,
        grupos=user.grupos,
        permissoes=get_permissoes(user.grupos),
    )


# === Endpoints protegidos ===

@app.get("/me")
async def me(user: AuthenticatedUser = Depends(get_current_user)):
    return {
        "username": user.username,
        "nome": user.nome,
        "grupos": user.grupos,
        "permissoes": user.permissoes,
    }


@app.get("/assistentes", response_model=list[AssistenteInfo])
async def listar_assistentes(
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Retorna apenas assistentes que o usuário tem acesso parcial ou total."""
    disponiveis = []
    for assistente in ASSISTENTES.values():
        if classificacoes_efetivas(assistente.id, user.permissoes):
            disponiveis.append(
                AssistenteInfo(
                    id=assistente.id,
                    nome=assistente.nome,
                    descricao=assistente.descricao,
                )
            )
    return disponiveis


def _classificar_confianca(chunks: list) -> str:
    """
    Classifica a confiança do retrieval com base no score do top chunk.
    - sem_resposta: nenhum chunk passou no threshold mínimo.
    - alta: top chunk com score >= RETRIEVAL_THRESHOLD_ALTA.
    - baixa: tem chunks, mas top com score abaixo de RETRIEVAL_THRESHOLD_ALTA.
    """
    if not chunks:
        return "sem_resposta"
    if chunks[0].score >= RETRIEVAL_THRESHOLD_ALTA:
        return "alta"
    return "baixa"


def _montar_resposta_mock(
    confianca: str, num_chunks: int, pergunta: str, assistente_nome: str
) -> str:
    """Resposta mockada baseada na confiança. Será substituída pelo Claude."""
    if confianca == "sem_resposta":
        return (
            f"Não encontrei informação suficiente sobre isso no assistente "
            f"de {assistente_nome}. Reformule a pergunta ou tente outro "
            f"assistente que tenha acesso ao tema."
        )
    if confianca == "baixa":
        return (
            f"[mock] Encontrei {num_chunks} trecho(s), mas a relevância "
            f"é baixa. A resposta pode não ser precisa. "
            f"Pergunta original: '{pergunta}'."
        )
    return (
        f"[mock] Encontrei {num_chunks} trecho(s) relevantes. "
        f"Pergunta original: '{pergunta}'."
    )


@app.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Recebe pergunta, busca chunks com filtro de permissão, classifica confiança."""
    assistente = get_assistente(req.assistente_id)
    if not assistente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assistente '{req.assistente_id}' não existe",
        )

    classificacoes = classificacoes_efetivas(
        req.assistente_id, user.permissoes
    )

    if not classificacoes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para o assistente '{req.assistente_id}'",
        )

    chunks = buscar_chunks(
        pergunta=req.pergunta,
        permissoes_usuario=user.permissoes,
        assistente_id=req.assistente_id,
    )

    confianca = _classificar_confianca(chunks)
    resposta = _montar_resposta_mock(
        confianca, len(chunks), req.pergunta, assistente.nome
    )

    # Debug info: útil pra diagnosticar problemas
    debug = {
        "num_chunks_recuperados": len(chunks),
        "score_top": chunks[0].score if chunks else None,
        "score_min": chunks[-1].score if chunks else None,
        "threshold_alta": RETRIEVAL_THRESHOLD_ALTA,
    }

    return QueryResponse(
        resposta=resposta,
        fontes=[
            FonteRecuperada(
                id=c.id,
                texto=c.texto,
                fonte=c.fonte,
                classificacao=c.classificacao,
                score=round(c.score, 2),
            )
            for c in chunks
        ],
        confianca=confianca,
        assistente_id=req.assistente_id,
        classificacoes_consultadas=classificacoes,
        debug=debug,
    )
