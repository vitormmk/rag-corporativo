"""
Backend do RAG Corporativo.
Endpoint /query agora aplica retrieval com filtro de permissão.
Resposta do LLM ainda é mock; será substituída na próxima fase.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.auth.dependencies import AuthenticatedUser, get_current_user
from src.auth.permissions import get_permissoes
from src.auth.users import authenticate
from src.config import ENVIRONMENT
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


# === Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[startup] backend iniciando em modo {ENVIRONMENT}")
    yield
    print("[shutdown] backend encerrando")


# === App ===

app = FastAPI(
    title="RAG Corporativo - Backend",
    version="0.3.0",
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
    return {"status": "ok", "version": "0.3.0"}


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
    """
    Retorna assistentes disponíveis para o usuário.
    Um assistente é 'disponível' se a intersecção com as permissões
    do usuário não for vazia (ou seja, há ao menos algo a ver).
    """
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


@app.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Recebe pergunta, aplica retrieval com filtro de permissão,
    monta resposta mockada com base nos chunks recuperados.
    """
    # Valida que o assistente existe
    assistente = get_assistente(req.assistente_id)
    if not assistente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assistente '{req.assistente_id}' não existe",
        )

    # Calcula as classificações que serão efetivamente consultadas
    classificacoes = classificacoes_efetivas(
        req.assistente_id, user.permissoes
    )

    # Se a intersecção for vazia, usuário não tem acesso ao assistente
    if not classificacoes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para o assistente '{req.assistente_id}'",
        )

    # Busca os chunks
    chunks = buscar_chunks(
        pergunta=req.pergunta,
        permissoes_usuario=user.permissoes,
        assistente_id=req.assistente_id,
    )

    # Confiança e resposta mockada baseadas no que foi recuperado
    if not chunks:
        confianca = "sem_resposta"
        resposta = (
            "Não encontrei informação sobre isso no escopo deste assistente. "
            "Tente reformular a pergunta ou consulte outro assistente."
        )
    elif chunks[0].score < 0.5:
        confianca = "baixa"
        resposta = (
            f"[mock] Encontrei {len(chunks)} trecho(s) com relevância "
            f"limitada. Pergunta original: '{req.pergunta}'."
        )
    else:
        confianca = "alta"
        resposta = (
            f"[mock] Encontrei {len(chunks)} trecho(s) relevantes para "
            f"sua pergunta. Pergunta original: '{req.pergunta}'."
        )

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
    )
