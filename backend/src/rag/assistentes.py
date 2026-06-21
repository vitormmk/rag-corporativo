"""
Definição dos assistentes (escopos especializados por domínio).

Cada assistente tem:
- nome e descrição para a interface
- conjunto de classificações que ele pode consultar
- system prompt específico (usado quando integrarmos o LLM)

A intersecção entre permissões do usuário e classificações do assistente
forma o filtro real aplicado na busca.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Assistente:
    id: str
    nome: str
    descricao: str
    classificacoes: list[str]
    system_prompt: str


ASSISTENTES: dict[str, Assistente] = {
    "ti": Assistente(
        id="ti",
        nome="TI",
        descricao="Infraestrutura, redes, sistemas",
        classificacoes=["publico", "ti-publico", "ti-interno"],
        system_prompt=(
            "Você é o assistente de TI da empresa. Responde sobre "
            "infraestrutura, redes, VPN, sistemas internos. Use apenas "
            "as informações do contexto fornecido."
        ),
    ),
    "rh": Assistente(
        id="rh",
        nome="RH",
        descricao="Políticas, benefícios, processos internos",
        classificacoes=["publico", "rh-publico", "rh-confidencial"],
        system_prompt=(
            "Você é o assistente de RH da empresa. Responde sobre "
            "políticas, benefícios, férias. Use apenas as informações "
            "do contexto fornecido."
        ),
    ),
    "processos": Assistente(
        id="processos",
        nome="Processos",
        descricao="Procedimentos gerais da empresa",
        classificacoes=["publico"],
        system_prompt=(
            "Você é o assistente de processos gerais da empresa. "
            "Responde sobre procedimentos disponíveis para todos os "
            "funcionários. Use apenas as informações do contexto fornecido."
        ),
    ),
}


def get_assistente(assistente_id: str) -> Assistente | None:
    return ASSISTENTES.get(assistente_id)


def classificacoes_efetivas(
    assistente_id: str, permissoes_usuario: list[str]
) -> list[str]:
    """
    Calcula a INTERSEÇÃO entre o escopo do assistente e as permissões
    do usuário. Esta é a lista final de classificações que será aplicada
    como filtro na busca.

    Exemplo:
    - Assistente TI pode buscar em: publico, ti-publico, ti-interno
    - Usuário Alice tem permissão para: publico, ti-publico, rh-publico
    - Intersecção: publico, ti-publico

    Alice falando com assistente TI nunca verá ti-interno, mesmo que
    o assistente saiba dessa classificação.
    """
    assistente = get_assistente(assistente_id)
    if not assistente:
        return []
    return sorted(set(assistente.classificacoes) & set(permissoes_usuario))
