# Guia de Configuração e Parâmetros

Todas as configurações do Zabbix MCP Server são controladas por variáveis de ambiente ou arquivo `.env`.

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `ZABBIX_URL` | string | `http://localhost/api_jsonrpc.php` | URL completa do endpoint da API do Zabbix. |
| `ZABBIX_TOKEN` | string | `None` | Token de API gerado no Zabbix (recomendado). |
| `ZABBIX_USER` | string | `Admin` | Usuário para login legado caso token não seja informado. |
| `ZABBIX_PASSWORD` | string | `None` | Senha de login caso token não seja informado. |
| `ZABBIX_MCP_MODE` | enum | `somente_leitura` | Nível de autorização: `somente_leitura`, `operacional` ou `administrativo`. |
| `ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE` | bool | `true` | Exige token de aprovação em 2 passos para remoções e modificações críticas. |
| `ZABBIX_APPROVAL_TOKEN_SECRET` | string | `segredo-padrao` | Chave HMAC para validação dos tokens de aprovação. |
| `ZABBIX_TIMEOUT` | float | `30.0` | Timeout em segundos para requisições HTTP à API Zabbix. |
| `ZABBIX_VERIFY_SSL` | bool | `true` | Validação de certificado TLS/SSL da API Zabbix. |
| `ZABBIX_MAX_RETRIES` | int | `3` | Tentativas de retry com backoff exponencial para falhas transitórias de rede. |
| `ZABBIX_BACKOFF_FACTOR` | float | `0.5` | Fator multiplicador para o cálculo do backoff exponencial. |
| `ZABBIX_MAX_CONCURRENCY` | int | `10` | Quantidade máxima de chamadas HTTP simultâneas ao Zabbix. |
| `ZABBIX_PAGE_SIZE` | int | `100` | Quantidade padrão de registros por página em consultas volumosas. |
| `ZABBIX_REPORTS_DIR` | path | `./reports_output` | Diretório de gravação de relatórios gerados (PDF, XLSX, etc.). |
| `ZABBIX_AUDIT_LOG_PATH` | path | `./audit_mcp.jsonl` | Caminho do arquivo JSONL onde todas as chamadas MCP são auditadas. |

## Configuração em Clientes MCP

### Configuração no Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "C:\\Users\\SeuUsuario\\.gemini\\antigravity-ide\\mcp\\zabbix\\.venv\\Scripts\\zabbix-mcp.exe",
      "args": ["--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### Configuração no Antigravity IDE (`mcp_config.json`)

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "cwd": "C:\\Users\\Natanael Krindges\\.gemini\\antigravity-ide\\mcp\\zabbix",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

