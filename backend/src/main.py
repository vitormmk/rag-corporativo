"""
Backend do RAG Corporativo.
Auth simplificada: login retorna dados do usuário, frontend envia
X-Username em requisições subsequentes.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.auth.dependencies import AuthenticatedUser, get_current_user
from src.auth.permissions import get_permissoes
from src.auth.users import authenticate
from src.config import ENVIRONMENT


# === Modelos ===

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    nome: str
    grupos: list[str]
    permissoes: list[str]


class QueryRequest(BaseModel):
    pergunta: str
    assistente_id: str = "ti"


class QueryResponse(BaseModel):
    resposta: str
    fontes: list[str]
    confianca: str
    assistente_id: str
    permissoes_aplicadas: list[str]


# === Lifespan ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[startup] backend iniciando em modo {ENVIRONMENT}")
    yield
    print("[shutdown] backend encerrando")


# === App ===

app = FastAPI(
    title="RAG Corporativo - Backend",
    version="0.2.0",
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
    return {"status": "ok", "version": "0.2.0"}


@app.post("/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """Login simples por usuário + senha. Retorna dados e permissões."""
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
    """Retorna dados do usuário autenticado. Útil pra validar sessão."""
    return {
        "username": user.username,
        "nome": user.nome,
        "grupos": user.grupos,
        "permissoes": user.permissoes,
    }


@app.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Endpoint principal.
    Por enquanto retorna mock, mas já mostra permissões resolvidas.
    Próxima fase: incorporar retrieval e LLM.
    """
    return QueryResponse(
        resposta=(
            f"[mock] Olá {user.nome}. "
            f"Você perguntou ao assistente '{req.assistente_id}': "
            f"'{req.pergunta}'."
        ),
        fontes=[],
        confianca="alta",
        assistente_id=req.assistente_id,
        permissoes_aplicadas=user.permissoes,
    )
