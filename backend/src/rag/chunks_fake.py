"""
Chunks fake hardcoded para validar lógica de retrieval e permissões
antes de substituir por embeddings + ChromaDB.

Cada chunk simula um pedaço de documento, com texto, fonte e classificação.
A classificação determina QUEM pode ver o chunk (controle de acesso).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkFake:
    id: str
    texto: str
    fonte: str
    classificacao: str


CHUNKS: list[ChunkFake] = [
    # === publico (qualquer funcionário) ===
    ChunkFake(
        id="pub-001",
        texto=(
            "O horário comercial padrão da empresa é das 9h às 18h, "
            "de segunda a sexta. Recesso para almoço de 1 hora."
        ),
        fonte="manual_funcionario.md",
        classificacao="publico",
    ),
    ChunkFake(
        id="pub-002",
        texto=(
            "Para abrir um chamado, acesse o portal interno em "
            "chamados.empresa.local e selecione a categoria adequada."
        ),
        fonte="manual_funcionario.md",
        classificacao="publico",
    ),
    ChunkFake(
        id="pub-003",
        texto=(
            "O código de conduta da empresa proíbe assédio, discriminação "
            "e uso indevido de recursos corporativos."
        ),
        fonte="codigo_conduta.md",
        classificacao="publico",
    ),

    # === ti-publico (qualquer funcionário, mas escopo TI) ===
    ChunkFake(
        id="tip-001",
        texto=(
            "Para conectar na VPN corporativa, instale o cliente WireGuard "
            "e importe o arquivo de configuração enviado pelo TI no primeiro dia."
        ),
        fonte="guia_vpn.md",
        classificacao="ti-publico",
    ),
    ChunkFake(
        id="tip-002",
        texto=(
            "O Wi-Fi corporativo usa autenticação WPA Enterprise. "
            "Use seu usuário do Google Workspace para conectar."
        ),
        fonte="guia_wifi.md",
        classificacao="ti-publico",
    ),
    ChunkFake(
        id="tip-003",
        texto=(
            "Trocar senha do Google Workspace: acesse myaccount.google.com, "
            "vá em Segurança, Senha. Mínimo 12 caracteres com símbolo."
        ),
        fonte="guia_senha.md",
        classificacao="ti-publico",
    ),

    # === ti-interno (apenas TI) ===
    ChunkFake(
        id="tii-001",
        texto=(
            "Firewall principal: pfSense em 10.0.0.1. Acesso restrito por VPN "
            "e MFA obrigatório. Logs centralizados em syslog.empresa.local."
        ),
        fonte="topologia_rede.md",
        classificacao="ti-interno",
    ),
    ChunkFake(
        id="tii-002",
        texto=(
            "Servidor de autenticação FreeRADIUS: 10.0.0.10. Integrado ao "
            "OpenLDAP que sincroniza com Google Workspace a cada 15 minutos."
        ),
        fonte="topologia_rede.md",
        classificacao="ti-interno",
    ),
    ChunkFake(
        id="tii-003",
        texto=(
            "Proxmox VE em 10.0.0.20 hospeda VMs de produção. Backup diário "
            "via Proxmox Backup Server em storage dedicado 10.0.0.21."
        ),
        fonte="infraestrutura.md",
        classificacao="ti-interno",
    ),

    # === rh-publico (qualquer funcionário, escopo RH) ===
    ChunkFake(
        id="rhp-001",
        texto=(
            "Direito a férias: 30 dias por ano após 12 meses de trabalho. "
            "Pode ser dividido em até 3 períodos, sendo um deles de no "
            "mínimo 14 dias corridos."
        ),
        fonte="politica_ferias.md",
        classificacao="rh-publico",
    ),
    ChunkFake(
        id="rhp-002",
        texto=(
            "Benefícios: plano de saúde Unimed, vale-refeição R$40/dia útil, "
            "auxílio home office R$150/mês, day-off no aniversário."
        ),
        fonte="beneficios.md",
        classificacao="rh-publico",
    ),

    # === rh-confidencial (apenas RH e diretoria) ===
    ChunkFake(
        id="rhc-001",
        texto=(
            "Tabela salarial 2026: Analista Júnior R$4.500-6.000, "
            "Analista Pleno R$6.500-9.000, Analista Sênior R$10.000-14.000, "
            "Especialista R$15.000-22.000."
        ),
        fonte="tabela_salarial_2026.md",
        classificacao="rh-confidencial",
    ),
    ChunkFake(
        id="rhc-002",
        texto=(
            "Processo de desligamento confidencial: alinhamento com gestor, "
            "aprovação da diretoria, comunicação formal pelo RH, "
            "desativação de acessos via ticket no GLPI."
        ),
        fonte="processo_desligamento.md",
        classificacao="rh-confidencial",
    ),
]
