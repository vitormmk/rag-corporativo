"""
Usuários de teste hardcoded.
ATENÇÃO: senha em texto puro. Apenas para desenvolvimento local.
Em produção, substituir por hash + JWT + integração SSO/LDAP.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    nome: str
    password: str  # texto puro - DEV ONLY
    grupos: list[str]


USERS: dict[str, User] = {
    "alice": User(
        username="alice",
        nome="Alice (Funcionária comum)",
        password="senha123",
        grupos=["funcionarios"],
    ),
    "bob": User(
        username="bob",
        nome="Bob (TI)",
        password="senha123",
        grupos=["funcionarios", "ti-infra"],
    ),
    "carol": User(
        username="carol",
        nome="Carol (RH)",
        password="senha123",
        grupos=["funcionarios", "rh"],
    ),
}


def get_user(username: str) -> User | None:
    return USERS.get(username)


def authenticate(username: str, password: str) -> User | None:
    """Retorna o User se credenciais válidas, None caso contrário."""
    user = get_user(username)
    if user and user.password == password:
        return user
    return None
