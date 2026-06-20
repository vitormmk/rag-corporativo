# RAG Corporativo

Sistema de perguntas e respostas sobre documentos corporativos. Cada assistente tem acesso restrito a documentos da sua área (TI, RH, Processos) com controle de acesso por classificação.

## Status

Em desenvolvimento. Fase atual: infraestrutura.

## O que faz

- Multi-assistente por domínio com escopo restrito de documentos
- Controle de acesso por classificação aplicado no banco vetorial
- Threshold de similaridade que retorna "não sei" quando contexto é insuficiente
- Pipeline de ingestão com conversão de PDF/DOCX para Markdown
- Logs estruturados de cada query e resposta para auditoria

## Stack

| Camada | Tecnologia |
|---|---|
| LLM | Anthropic Claude |
| Embeddings | BAAI/bge-m3 (local) |
| Banco vetorial | ChromaDB |
| Backend | FastAPI |
| Frontend | Next.js |
| Auth | JWT |

## Estrutura

\`\`\`
.
├── backend/              API FastAPI
├── frontend/             Interface Next.js
├── corpus/
│   ├── raw/              Documentos originais (não versionados)
│   ├── markdown/         Versão convertida para indexação (não versionados)
│   └── metadata/         Inventário e governança
├── docs/                 Documentação
└── scripts/              Utilitários
\`\`\`

## Versões planejadas

- V1.0 — MVP: RAG documental, multi-assistente, auth, deploy local
- V1.1 — Evals, observability, ingestão robusta
- V1.2 — Reranking, contextual retrieval, suporte a imagens
- V1.3 — Caching, model routing
- V2.0 — Tool use, code execution, SSO

## Licença

MIT
