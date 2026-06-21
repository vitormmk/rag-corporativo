"""
Camada de retrieval. Busca por substring em chunks hardcoded por enquanto;
quando integrarmos o ChromaDB, esta é a única função que muda.

Padrão importante: filtros (escopo do assistente + permissões do usuário)
são aplicados ANTES da busca textual. Mesmo que um chunk contivesse a
palavra exata da query, ele não retorna se o usuário não tem permissão.
"""
from dataclasses import dataclass

from src.config import RETRIEVAL_SCORE_MINIMO, RETRIEVAL_TOP_K
from src.rag.assistentes import classificacoes_efetivas
from src.rag.chunks_fake import CHUNKS


STOPWORDS = {
    "de", "da", "do", "das", "dos", "a", "o", "as", "os", "e", "ou",
    "em", "na", "no", "nas", "nos", "para", "por", "com", "sem", "que",
    "se", "um", "uma", "uns", "umas", "ao", "aos", "à", "às", "como",
    "qual", "quais", "quem", "onde", "quando", "porque", "porquê",
    "é", "são", "foi", "ser", "estar", "ter", "há",
}


@dataclass
class ChunkRecuperado:
    """Chunk retornado pela busca, com score de relevância."""
    id: str
    texto: str
    fonte: str
    classificacao: str
    score: float


def _tokenizar(texto: str) -> list[str]:
    """Quebra texto em palavras minúsculas, removendo pontuação e stopwords."""
    palavras = []
    for palavra in texto.lower().split():
        limpa = palavra.strip(".,?!;:()[]\"'")
        if len(limpa) > 2 and limpa not in STOPWORDS:
            palavras.append(limpa)
    return palavras


def _calcular_score(pergunta_tokens: list[str], chunk_texto: str) -> float:
    """
    Score por palavra inteira: proporção de tokens da pergunta que
    aparecem como palavra completa no chunk.
    Evita falsos positivos por substring (ex: "cor" dentro de "corporativo").
    """
    if not pergunta_tokens:
        return 0.0

    chunk_tokens = set(_tokenizar(chunk_texto))
    matches = sum(1 for token in pergunta_tokens if token in chunk_tokens)
    return matches / len(pergunta_tokens)


def buscar_chunks(
    pergunta: str,
    permissoes_usuario: list[str],
    assistente_id: str,
    top_k: int | None = None,
    score_minimo: float | None = None,
) -> list[ChunkRecuperado]:
    """
    Busca chunks relevantes, aplicando:
    1. Filtro de classificação (intersecção assistente × usuário).
    2. Busca textual.
    3. Threshold de score (descarta resultados fracos).
    4. Ordenação por relevância e corte em top_k.
    """
    k = top_k if top_k is not None else RETRIEVAL_TOP_K
    score_min = score_minimo if score_minimo is not None else RETRIEVAL_SCORE_MINIMO

    classificacoes_permitidas = set(
        classificacoes_efetivas(assistente_id, permissoes_usuario)
    )

    if not classificacoes_permitidas:
        return []

    pergunta_tokens = _tokenizar(pergunta)

    candidatos: list[ChunkRecuperado] = []
    for chunk in CHUNKS:
        if chunk.classificacao not in classificacoes_permitidas:
            continue

        score = _calcular_score(pergunta_tokens, chunk.texto)
        if score < score_min:
            continue

        candidatos.append(
            ChunkRecuperado(
                id=chunk.id,
                texto=chunk.texto,
                fonte=chunk.fonte,
                classificacao=chunk.classificacao,
                score=score,
            )
        )

    candidatos.sort(key=lambda c: c.score, reverse=True)
    return candidatos[:k]
