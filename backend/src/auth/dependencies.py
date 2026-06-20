"""
Dependência simples de autenticação via header X-Username.
DEV ONLY: confia que o frontend envia o username correto após login.
Em produção, trocar por JWT validado no servidor.
"""
from fastapi import Header, HTTPException, status

from src.auth.permissions import get_permissoes
from src.auth.users import User, get_user


class AuthenticatedUser:
    """Usuário autenticado com permissões já resolvidas."""

    def __init__(self, user: User):
        self.username = user.username
        self.nome = user.nome
        self.grupos = user.grupos
        self.permissoes = get_permissoes(user.grupos)


async def get_current_user(
    x_username: str | None = Header(default=None, alias="X-Username"),
) -> AuthenticatedUser:
    """Extrai usuário do header X-Username. 401 se ausente ou inválido."""
    if not x_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-Username ausente",
        )

    user = get_user(x_username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido",
        )

    return AuthenticatedUser(user)
