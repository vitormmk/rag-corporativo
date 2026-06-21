"""
Configuração centralizada do backend.
Lê variáveis do .env e expõe como constantes.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# === Ambiente ===
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# === LLM ===
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

# === RAG / Retrieval ===
# Score mínimo para um chunk ser considerado relevante.
# Abaixo disso, é descartado.
RETRIEVAL_SCORE_MINIMO: float = float(
    os.getenv("RETRIEVAL_SCORE_MINIMO", "0.2")
)

# Score do TOP chunk acima do qual classificamos como "alta confiança".
RETRIEVAL_THRESHOLD_ALTA: float = float(
    os.getenv("RETRIEVAL_THRESHOLD_ALTA", "0.6")
)

# Número máximo de chunks recuperados por consulta.
RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
