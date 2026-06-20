"""
Configuração centralizada do backend.
Lê variáveis do .env e expõe como constantes.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
