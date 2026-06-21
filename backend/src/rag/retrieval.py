"""
Camada de retrieval. Por enquanto usa busca por substring em chunks
hardcoded; quando integrarmos o ChromaDB, esta é a única função que muda.

Padrão importante: os filtros (escopo do assistente + permissões do
usuário) são aplicados ANTES da busca textual. Mesmo que um chunk
contivesse a palavra exata da query, ele não retorna se o usuário
não tem permissão de vê-lo.
"""
from dataclasses import dataclass

from src.rag.assistentes import classificacoes_efetivas
from src.rag.chunks_fake import CHUNKS


# Palavras muito comuns que não ajudam na busca; ignoradas no matching
STOPWORDS = {
    "de", "da", "do", "das", "dos", "a", "o", "as", "os", "e", "ou",
    "em", "na", "no", "nas", "nos", "para", "por", "com", "sem", "que",
    "se", "um", "uma", "uns", "umas", "ao", "aos", "à", "às", "como",
    "qual", "quais", "quem", "onde", "quando", "porque", "porquê",
    "é", "são", "foi", "ser", "estar", "ter", "há", "qual",
}


@dataclass
class ChunkRecuperado:
    """Chunk retornado pela busca, com score de relevância."""
    id: str
    texto: str
    fonte: str
    classificacao: str
    score: float  # 0.0 a 1.0, maior = mais relevante


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
    Score simples: proporção de tokens da pergunta que aparecem no chunk.
    Vai de 0.0 (nada bate) a 1.0 (todos os tokens batem).
    """
    if not pergunta_tokens:
        return 0.0

    chunk_lower = chunk_texto.lower()
    matches = sum(1 for token in pergunta_tokens if token in chunk_lower)
    return matches / len(pergunta_tokens)


def buscar_chunks(
    pergunta: str,
    permissoes_usuario: list[str],
    assistente_id: str,
    top_k: int = 5,
    score_minimo: float = 0.2,
) -> list[ChunkRecuperado]:
    """
    Busca chunks relevantes para a pergunta, aplicando:
    1. Filtro de classificação (intersecção assistente × usuário).
    2. Busca textual por substring (substituída por embeddings depois).
    3. Threshold de score (descarta resultados fracos).
    4. Ordenação por relevância e corte em top_k.
    """
    # === Filtro DETERMINÍSTICO: nunca passa pelo LLM ===
    classificacoes_permitidas = set(
        classificacoes_efetivas(assistente_id, permissoes_usuario)
    )

    if not classificacoes_permitidas:
        return []

    pergunta_tokens = _tokenizar(pergunta)

    candidatos: list[ChunkRecuperado] = []
    for chunk in CHUNKS:
        # Filtro de segurança
        if chunk.classificacao not in classificacoes_permitidas:
            continue

        score = _calcular_score(pergunta_tokens, chunk.texto)
        if score < score_minimo:
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

    # Ordena por score desc e retorna top_k
    candidatos.sort(key=lambda c: c.score, reverse=True)
    return candidatos[:top_k]
