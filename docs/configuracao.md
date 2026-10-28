# Guia de Configuração e Parâmetros

Todas as configurações do **Zabbix MCP Server** são gerenciadas de forma declarativa através de variáveis de ambiente ou arquivo `.env`, com validação rigorosa de tipos via **Pydantic Settings**.

---

## 1. Tabela Completa de Variáveis de Ambiente

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `ZABBIX_URL` | string | `http://localhost/api_jsonrpc.php` | URL completa do endpoint da API JSON-RPC do Zabbix Server. |
| `ZABBIX_TOKEN` | string | `None` | Token de API de 64 caracteres gerado no Zabbix (método preferido). |
| `ZABBIX_USER` | string | `Admin` | Nome de usuário legado para autenticação por login/senha caso o token não seja fornecido. |
| `ZABBIX_PASSWORD` | string | `None` | Senha de usuário caso o token não seja fornecido. |
| `ZABBIX_MCP_MODE` | enum | `somente_leitura` | Perfil de permissão RBAC: `somente_leitura`, `operacional` ou `administrativo`. |
| `ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE` | bool | `true` | Exige token criptográfico HMAC para ações destrutivas (exclusão de hosts, desassociação com clear, alteração de triggers). |
| `ZABBIX_APPROVAL_TOKEN_SECRET` | string | `segredo-padrao` | Chave secreta compartilhada para geração e validação dos tokens HMAC de aprovação. |
| `ZABBIX_TIMEOUT` | float | `30.0` | Tempo limite em segundos para cada chamada HTTP JSON-RPC antes de timeout. |
| `ZABBIX_VERIFY_SSL` | bool | `true` | Habilita/desabilita a validação de certificados TLS/SSL (defina `false` para certificados autoassinados). |
| `ZABBIX_MAX_RETRIES` | int | `3` | Quantidade máxima de retries com backoff exponencial para falhas transitórias de rede. |
| `ZABBIX_BACKOFF_FACTOR` | float | `0.5` | Fator multiplicador para o cálculo de backoff exponencial entre retries. |
| `ZABBIX_MAX_CONCURRENCY` | int | `10` | Quantidade máxima de conexões HTTP simultâneas enviadas ao Zabbix Server (semáforo assíncrono). |
| `ZABBIX_PAGE_SIZE` | int | `100` | Quantidade padrão de registros por página em consultas volumosas (`limit`). |
| `ZABBIX_REPORTS_DIR` | path | `./reports_output` | Diretório no disco onde relatórios gerados (PDF, XLSX, CSV, JSON) são persistidos. |
| `ZABBIX_AUDIT_LOG_PATH` | path | `./audit_mcp.jsonl` | Caminho do arquivo JSON Lines imutável onde todas as chamadas do MCP são auditadas localmente. |

---

## 2. Perfis de Segurança e Permissões (RBAC)

O servidor possui 3 modos de governança definidos por `ZABBIX_MCP_MODE`:

### 1. `somente_leitura` (Padrão de Fábrica - Máxima Segurança)
- Bloqueia **qualquer** chamada que tente alterar o banco de dados do Zabbix.
- Permite apenas ferramentas de consulta, histórico, tendências, listagens, diagnósticos e relatórios.
- Se uma IA tentar invocar `zabbix_criar_host` ou `zabbix_atualizar_item`, o servidor responde com erro `PermissaoNegadaError` e bloqueia a execução.

### 2. `operacional` (Ambiente de Trabalho e NOC)
- Permite operações de rotina: criação de hosts, atualização de interfaces, vinculação de templates, agendamento de manutenções e reconhecimento formal de problemas (`zabbix_reconhecer_problema`).
- Ações destrutivas (excluir hosts ou excluir proxies) continuam bloqueadas ou exigem confirmação explícita.

### 3. `administrativo` (Automação Completa e DevSecOps)
- Libera o conjunto completo das 100 ferramentas, incluindo gerenciamento de proxies, regras de descoberta nativa, usuários e auditoria.
- **Aprovação em Dois Passos (HMAC):** Para operações de exclusão irreversível, a ferramenta gera um token de aprovação assinado vinculado aos parâmetros exatos com validade de 15 minutos, exigindo que o operador confirme a execução com esse token.

---

## 3. Configuração nos Clientes MCP

### 3.1. Claude Desktop
Adicione ao arquivo de configuração:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "C:/Users/SEU_USUARIO/zabbix-mcp-server/.venv/Scripts/python.exe",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "cwd": "C:/Users/SEU_USUARIO/zabbix-mcp-server",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional",
        "ZABBIX_VERIFY_SSL": "false"
      }
    }
  }
}
```

### 3.2. Antigravity IDE (`mcp_config.json`)
Localizado em `~/.gemini/config/mcp_config.json` ou no painel de ferramentas MCP:

```json
{
  "mcpServers": {
    "zabbix-mcp": {
      "command": "C:\Users\Natanael Krindges\.gemini\antigravity-ide\mcp\zabbix\.venv\Scripts\python.exe",
      "args": [
        "-m",
        "zabbix_mcp.server",
        "--transport",
        "stdio"
      ],
      "cwd": "C:\Users\Natanael Krindges\.gemini\antigravity-ide\mcp\zabbix",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### 3.3. Cursor IDE (`.cursor/mcp.json`)
No arquivo `.cursor/mcp.json` na raiz do seu workspace ou nas configurações globais:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "cwd": "/caminho/para/zabbix-mcp-server",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### 3.4. VS Code (com Cline / Roo Code / Claude Dev)
Nas configurações da extensão ou em `settings.json`:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### 3.5. Windsurf / Cascade (`mcp_config.json`)
No arquivo `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "/caminho/para/zabbix-mcp-server/.venv/bin/python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```
