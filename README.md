# Zabbix MCP Server Universal

[![CI - Integracao Continua](https://github.com/seu-usuario/zabbix-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/seu-usuario/zabbix-mcp-server/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0%2B%20%2F%202.x-green)](https://modelcontextprotocol.io/)
[![Zabbix](https://img.shields.io/badge/Zabbix-6.0%20%7C%206.4%20%7C%207.0%20LTS%20%7C%207.4-red)](https://www.zabbix.com/)

Servidor MCP (**Model Context Protocol**) corporativo para gerenciamento inteligente do **Zabbix Enterprise Monitoring**, com **100 ferramentas em português**, automação completa de descoberta e cadastro de dispositivos em 6 estágios, motor profissional de relatórios (PDF, XLSX, CSV, JSON, Markdown), controles de acesso baseados em funções (RBAC), aprovação em dois passos e compatibilidade universal.

*Read this in English: [README.en.md](README.en.md)*

---

## 🚀 Destaques do Projeto

- **100 Ferramentas Oficiais:** Nomes estáveis em `snake_case`, contratos Pydantic estritos e descrições em português cobrindo todas as categorias do Zabbix.
- **Onboarding Automatizado de Dispositivos (Estágios A ao F):**
  1. *Descoberta Controlada:* Varredura de sub-redes autorizadas com taxa limitada e sem risco de saturação.
  2. *Identificação & Fingerprinting:* Inferência de Sistema Operacional (Linux, Windows, Network Appliance) com score de confiança e portas de serviço.
  3. *Reconciliação & Deduplicação:* Checagem contra o inventário existente para evitar hosts duplicados.
  4. *Planejamento & Prévia:* Exibição de interfaces, grupos e templates antes de qualquer gravação.
  5. *Cadastro em Lote Transacional:* Criação segura com tratamento individual de falhas.
  6. *Verificação Pós-Cadastro:* Confirmação de interfaces sem erros, itens ativos e chegada do primeiro ciclo de métricas.
- **Motor Profissional de Relatórios:** Geração direta de documentos em **PDF** corporativo (com tabelas e layout executivo), **Planilhas Excel (.xlsx)** multi-abas, **CSV**, **JSON** e **Markdown**.
- **Segurança Produtiva (DevSecOps):**
  - Modos de autorização RBAC: `somente_leitura` (padrão), `operacional` e `administrativo`.
  - **Aprovação em Dois Passos:** Ações destrutivas (excluir hosts, alterar regras) exigem token criptográfico HMAC vinculado aos parâmetros exatos com expiração de 15 minutos.
  - **Redação Automática de Segredos:** Tokens, senhas e communities SNMP são mascarados como `[REDACTED]`.
  - **Proteção contra SSRF:** Bloqueio de loopback (`127.0.0.1`) e limitação de escopos a no máximo 1024 IPs.
  - **Trilha de Auditoria Local:** Registro imutável em JSON Lines (`audit_mcp.jsonl`) de todas as invocações.
- **Compatibilidade Inteligente de Versões:** Identificação dinâmica via `apiinfo.version` com suporte a autenticação por cabeçalho Bearer no Zabbix 7.0+ e suporte a Zabbix 6.0 LTS / 6.4.

---

## 📁 Estrutura do Repositório

```text
zabbix-mcp-server/
├── src/zabbix_mcp/
│   ├── server.py              # Ponto de entrada FastMCP / MCPServer (100 ferramentas)
│   ├── config.py              # Pydantic Settings e variáveis de ambiente
│   ├── client.py              # Cliente assíncrono httpx com JSON-RPC 2.0 e retries
│   ├── api_compatibility.py   # Detecção de versão e matriz de recursos
│   ├── models.py              # Contratos Pydantic de entrada e saída (ToolResult)
│   ├── security.py            # Redação de segredos e prevenção de SSRF/Path Traversal
│   ├── authorization.py       # Modos de autorização RBAC
│   ├── policies.py            # Tokens de aprovação HMAC em 2 passos
│   ├── audit.py               # Motor de auditoria local em JSONL
│   ├── discovery/             # Onboarding automatizado em 6 estágios (A ao F)
│   ├── reports/               # Motor de exportação PDF, Excel, CSV, JSON e MD
│   └── tools/                 # As 100 ferramentas divididas em 10 categorias
├── tests/
│   ├── unit/                  # Testes unitários (inventário das 100 ferramentas, RBAC, etc.)
│   └── integration/           # Testes de integração contra Zabbix real
├── docs/                      # 9 Guias detalhados de arquitetura, ferramentas e segurança
├── .github/                   # Workflows de CI/CD e templates de issues/PR
├── Dockerfile                 # Imagem de produção sem privilégios de root
├── compose.yaml               # Docker Compose com suporte a transporte SSE
└── pyproject.toml             # Metadados e dependências do projeto
```

---

## 📦 Instalação e Configuração

### 1. Requisitos
- Python 3.11, 3.12 ou 3.13.
- Acesso à API do Zabbix (`/api_jsonrpc.php`).

### 2. Instalação Local com Virtualenv

```bash
git clone https://github.com/seu-usuario/zabbix-mcp-server.git
cd zabbix-mcp-server

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# No Windows:
.\.venv\Scripts\activate

pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Configuração do `.env`

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
Configure as variáveis principais:
```ini
ZABBIX_URL=http://192.168.0.107:8080/api_jsonrpc.php
ZABBIX_TOKEN=seu_token_aqui
ZABBIX_MCP_MODE=somente_leitura
```

---

## 🔌 Integração com Clientes MCP

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### Antigravity IDE (`mcp_config.json`)

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "cwd": "C:\\caminho\\para\\zabbix-mcp-server",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

---

## 🛠️ As 100 Ferramentas por Categoria

| Categoria | Faixa | Descrição |
|---|---|---|
| **1. Descoberta Automática** | 1 a 10 | Varredura não intrusiva, fingerprinting de SO, deduplicação, prévia e onboarding em lote. |
| **2. Hosts e Interfaces** | 11 a 20 | Listagem, consulta, criação, atualização, remoção com aprovação e interfaces (Agent/SNMP). |
| **3. Coleta e Métricas** | 21 a 30 | Itens de coleta, histórico, tendências, últimos valores, lacunas e diagnóstico de telemetria. |
| **4. Problemas e Triggers**| 31 a 40 | Problemas ativos, eventos, triggers, reconhecimento de alertas e investigação de causa raiz. |
| **5. Relatórios Técnicos** | 41 a 50 | Relatórios executivos, disponibilidade, capacidade, SLA e exportação para PDF e XLSX. |
| **6. Alertas e Ações** | 51 a 60 | Histórico de notificações, tipos de mídia, teste de canais e detecção de falsos positivos. |
| **7. Serviços e Mapas** | 61 a 70 | Serviços de negócio (SLO/SLA), janelas de manutenção e mapas de topologia em Mermaid. |
| **8. Inventário e Templates**| 71 a 80 | Dados de hardware/software, grupos de hosts, templates e auditoria de cobertura. |
| **9. Proxies e Administração**| 81 a 90 | Regras de rede nativas, LLD, proxies Zabbix, usuários, funções de acesso e auditoria nativa. |
| **10. Governança e IA** | 91 a 100 | Validação de conexão, PLN para consultas Zabbix, análise de anomalias e diagnóstico 360°. |

*Consulte o catálogo completo com parâmetros detalhados em [docs/ferramentas.md](docs/ferramentas.md).*

---

## 🧪 Testes Automatizados

O projeto conta com testes unitários cobrindo o inventário de ferramentas, validação de segurança e testes de integração reais:

```bash
# Executa todos os testes
pytest -v

# Executa lint com ruff
ruff check src tests
```

---

## 🐳 Executando com Docker e Docker Compose

```bash
# Build da imagem local
docker build -t zabbix-mcp-server .

# Execução com Docker Compose (Modo SSE na porta 8000)
docker compose up -d
```

---

## 📚 Documentação Adicional

- [Arquitetura e Fluxo de Dados](docs/arquitetura.md)
- [Guia de Instalação](docs/instalacao.md)
- [Guia de Configuração e Parâmetros](docs/configuracao.md)
- [Catálogo Detalhado das 100 Ferramentas](docs/ferramentas.md)
- [Descoberta Automática e Onboarding (A-F)](docs/descoberta-automatica.md)
- [Motor de Relatórios (PDF, Excel, etc.)](docs/relatorios.md)
- [Guia de Segurança e RBAC](docs/seguranca.md)
- [Matriz de Compatibilidade de Versões](docs/compatibilidade.md)
- [Solução de Problemas Comuns](docs/solucao-de-problemas.md)

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
