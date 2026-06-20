"""
Mapa determinístico de grupos para classificações de documentos.
Trava de segurança principal: regra em código, nunca em prompt.
"""

CLASSIFICACOES = [
    "publico",
    "ti-publico",
    "ti-interno",
    "rh-publico",
    "rh-confidencial",
]

GRUPO_PERMISSOES: dict[str, list[str]] = {
    "funcionarios": ["publico", "ti-publico", "rh-publico"],
    "ti-infra": ["publico", "ti-publico", "ti-interno", "rh-publico"],
    "rh": ["publico", "ti-publico", "rh-publico", "rh-confidencial"],
    "diretoria": CLASSIFICACOES,
}


def get_permissoes(grupos: list[str]) -> list[str]:
    """União das classificações permitidas pelos grupos do usuário."""
    permitido: set[str] = set()
    for grupo in grupos:
        permitido.update(GRUPO_PERMISSOES.get(grupo, []))
    return sorted(permitido)
