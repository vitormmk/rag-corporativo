"use client";

import { useEffect, useState } from "react";

type Assistente = "ti" | "rh" | "processos";

type Usuario = {
  username: string;
  nome: string;
  grupos: string[];
  permissoes: string[];
};

type RespostaAPI = {
  resposta: string;
  fontes: string[];
  confianca: "alta" | "baixa" | "sem_resposta";
  assistente_id: string;
  permissoes_aplicadas: string[];
};

const ASSISTENTES: { id: Assistente; nome: string; descricao: string }[] = [
  { id: "ti", nome: "TI", descricao: "Infraestrutura, redes, sistemas" },
  { id: "rh", nome: "RH", descricao: "Políticas, benefícios, processos" },
  { id: "processos", nome: "Processos", descricao: "Procedimentos gerais" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const STORAGE_KEY = "rag.usuario";

export default function Home() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  // Restaura sessão do localStorage no carregamento
  useEffect(() => {
    const salvo = localStorage.getItem(STORAGE_KEY);
    if (salvo) {
      try {
        setUsuario(JSON.parse(salvo));
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setCarregando(false);
  }, []);

  function aoLogar(u: Usuario) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    setUsuario(u);
  }

  function aoSair() {
    localStorage.removeItem(STORAGE_KEY);
    setUsuario(null);
  }

  if (carregando) {
    return (
      <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex items-center justify-center">
        <p className="text-zinc-500 text-sm">Carregando...</p>
      </main>
    );
  }

  if (!usuario) {
    return <TelaLogin aoLogar={aoLogar} />;
  }

  return <TelaChat usuario={usuario} aoSair={aoSair} />;
}

// ============================================================
// Tela de Login
// ============================================================

function TelaLogin({ aoLogar }: { aoLogar: (u: Usuario) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function enviar() {
    if (!username.trim() || !password.trim()) return;

    setLoading(true);
    setErro(null);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Erro ${res.status}`);
      }

      const data: Usuario = await res.json();
      aoLogar(data);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      enviar();
    }
  }

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex items-center justify-center p-8">
      <div className="w-full max-w-sm">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
          RAG Corporativo
        </h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-6">
          Entre com seu usuário
        </p>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              Usuário
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
              autoComplete="username"
              className="w-full p-2 rounded border border-zinc-300 bg-white text-zinc-900 focus:outline-none focus:border-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:focus:border-zinc-100"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              Senha
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              autoComplete="current-password"
              className="w-full p-2 rounded border border-zinc-300 bg-white text-zinc-900 focus:outline-none focus:border-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:focus:border-zinc-100"
            />
          </div>

          <button
            onClick={enviar}
            disabled={loading || !username.trim() || !password.trim()}
            className="w-full px-4 py-2 rounded bg-zinc-900 text-zinc-50 text-sm font-medium hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>

          {erro && (
            <div className="text-sm text-red-700 dark:text-red-400">{erro}</div>
          )}
        </div>

        <div className="mt-8 pt-6 border-t border-zinc-200 dark:border-zinc-800 text-xs text-zinc-500 dark:text-zinc-400">
          <p className="mb-1 font-medium">Usuários de teste:</p>
          <ul className="space-y-0.5">
            <li>alice / senha123 — funcionária comum</li>
            <li>bob / senha123 — TI</li>
            <li>carol / senha123 — RH</li>
          </ul>
        </div>
      </div>
    </main>
  );
}

// ============================================================
// Tela de Chat
// ============================================================

function TelaChat({
  usuario,
  aoSair,
}: {
  usuario: Usuario;
  aoSair: () => void;
}) {
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
        headers: {
          "Content-Type": "application/json",
          "X-Username": usuario.username,
        },
        body: JSON.stringify({
          pergunta: pergunta.trim(),
          assistente_id: assistente,
        }),
      });

      if (res.status === 401) {
        aoSair();
        return;
      }

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
        <header className="mb-6 flex items-start justify-between">
          <div>
            <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
              RAG Corporativo
            </h1>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
              {usuario.nome}
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-500 mt-1">
              Acesso: {usuario.permissoes.join(", ")}
            </p>
          </div>
          <button
            onClick={aoSair}
            className="text-xs text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
          >
            Sair
          </button>
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
            <div className="mt-4 pt-3 border-t border-zinc-200 dark:border-zinc-800">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Permissões aplicadas: {resposta.permissoes_aplicadas.join(", ")}
              </p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
