"use client";

import { useState } from "react";

type Assistente = "ti" | "rh" | "processos";

type RespostaAPI = {
  resposta: string;
  fontes: string[];
  confianca: "alta" | "baixa" | "sem_resposta";
  assistente_id: string;
};

const ASSISTENTES: { id: Assistente; nome: string; descricao: string }[] = [
  { id: "ti", nome: "TI", descricao: "Infraestrutura, redes, VPN, sistemas" },
  { id: "rh", nome: "RH", descricao: "Políticas, benefícios, processos internos" },
  { id: "processos", nome: "Processos", descricao: "Procedimentos gerais da empresa" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [assistente, setAssistente] = useState<Assistente>("ti");
  const [pergunta, setPergunta] = useState("");
  const [resposta, setResposta] = useState<RespostaAPI | null>(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function enviar() {
    if (!pergunta.trim()) return;

    setLoading(true);
    setErro(null);
    setResposta(null);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pergunta: pergunta.trim(),
          assistente_id: assistente,
        }),
      });

      if (!res.ok) {
        throw new Error(`Erro ${res.status}: ${res.statusText}`);
      }

      const data: RespostaAPI = await res.json();
      setResposta(data);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      enviar();
    }
  }

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            RAG Corporativo
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
            Selecione um assistente e faça sua pergunta.
          </p>
        </header>

        <section className="mb-6">
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
            Assistente
          </label>
          <div className="grid grid-cols-3 gap-2">
            {ASSISTENTES.map((a) => (
              <button
                key={a.id}
                onClick={() => setAssistente(a.id)}
                className={`p-3 rounded border text-left transition ${
                  assistente === a.id
                    ? "border-zinc-900 bg-zinc-900 text-zinc-50 dark:border-zinc-100 dark:bg-zinc-100 dark:text-zinc-900"
                    : "border-zinc-300 bg-white text-zinc-900 hover:border-zinc-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:border-zinc-500"
                }`}
              >
                <div className="font-medium text-sm">{a.nome}</div>
                <div className="text-xs opacity-75 mt-1">{a.descricao}</div>
              </button>
            ))}
          </div>
        </section>

        <section className="mb-4">
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
            Pergunta
          </label>
          <textarea
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta... (Cmd+Enter para enviar)"
            rows={3}
            className="w-full p-3 rounded border border-zinc-300 bg-white text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder-zinc-600 dark:focus:border-zinc-100"
          />
          <button
            onClick={enviar}
            disabled={loading || !pergunta.trim()}
            className="mt-3 px-4 py-2 rounded bg-zinc-900 text-zinc-50 text-sm font-medium hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            {loading ? "Buscando..." : "Enviar"}
          </button>
        </section>

        {erro && (
          <section className="mb-4 p-3 rounded border border-red-300 bg-red-50 text-red-900 text-sm dark:border-red-900 dark:bg-red-950 dark:text-red-200">
            {erro}
          </section>
        )}

        {resposta && (
          <section className="p-4 rounded border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                Resposta — {resposta.assistente_id}
              </span>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  resposta.confianca === "alta"
                    ? "bg-green-100 text-green-900 dark:bg-green-950 dark:text-green-200"
                    : resposta.confianca === "baixa"
                    ? "bg-yellow-100 text-yellow-900 dark:bg-yellow-950 dark:text-yellow-200"
                    : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                }`}
              >
                confiança: {resposta.confianca}
              </span>
            </div>
            <p className="text-zinc-900 dark:text-zinc-100 whitespace-pre-wrap">
              {resposta.resposta}
            </p>
            {resposta.fontes.length > 0 && (
              <div className="mt-4 pt-3 border-t border-zinc-200 dark:border-zinc-800">
                <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
                  Fontes:
                </span>
                <ul className="mt-1 text-xs text-zinc-700 dark:text-zinc-300">
                  {resposta.fontes.map((f, i) => (
                    <li key={i}>• {f}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
