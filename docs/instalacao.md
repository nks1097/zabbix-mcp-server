# Guia de Instalação do Zabbix MCP Server

O servidor pode ser instalado localmente via Python virtualenv, uv ou executado via container Docker.

## 1. Requisitos de Sistema

- Python 3.11, 3.12 ou superior.
- Acesso de rede à porta HTTP/HTTPS da interface web do Zabbix Server (`/api_jsonrpc.php`).
- Token de API gerado no Zabbix (ou usuário e senha com permissão de leitura/escrita).

## 2. Instalação Local (Recomendada)

### Usando venv e pip

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/zabbix-mcp-server.git
cd zabbix-mcp-server

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou no Windows:
.\.venv\Scripts\activate

# Instale o pacote e suas dependências
pip install --upgrade pip
pip install -e .
```

### Usando uv (Ultra-rápido)

```bash
uv venv .venv
source .venv/bin/activate  # ou .\.venv\Scripts\activate
uv pip install -e .
```

## 3. Configuração do `.env`

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
Preencha as variáveis principais:
```ini
ZABBIX_URL=http://seu-zabbix:8080/api_jsonrpc.php
ZABBIX_TOKEN=seu_token_gerado_no_zabbix
ZABBIX_MCP_MODE=somente_leitura
```

## 4. Teste de Conectividade e Validação

Execute a suíte de testes unitários e de integração:
```bash
pytest -v
```

## 5. Execução do Servidor MCP

### Modo STDIO (para Claude Desktop, Cursor, Antigravity IDE)
```bash
zabbix-mcp --transport stdio
```

### Modo SSE (para chamadas remotas HTTP)
```bash
zabbix-mcp --transport sse --host 0.0.0.0 --port 8000
```
