# Guia de Solução de Problemas e Diagnóstico de Erros

Guia prático e detalhado para solucionar os problemas mais comuns na instalação, configuração e operação do **Zabbix MCP Server**.

---

## 1. Erros de Instalação e Ambiente Virtual

### Erro: `Activate.ps1 cannot be loaded because running scripts is disabled on this system` (PowerShell)
- **Causa:** O Windows restringe por padrão a execução de scripts no PowerShell para proteger o sistema contra execuções acidentais.
- **Solução:** No terminal do PowerShell, libere a execução para o usuário atual executando:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Pressione `S` (Sim) para confirmar. Em seguida, reative o ambiente com `.\\.venv\\Scripts\\activate`.

### Erro: `No module named 'zabbix_mcp'` ao executar o servidor
- **Causa:** O pacote não foi instalado em modo editável ou o comando está sendo executado fora do virtualenv.
- **Solução:**
  1. Certifique-se de que o virtualenv está ativo (`(.venv)` no prompt).
  2. Instale o pacote executando `pip install -e .` na raiz do projeto.
  3. No arquivo de configuração do cliente MCP (`claude_desktop_config.json` ou `mcp_config.json`), configure o caminho absoluto do executável Python do virtualenv (ex: `C:\\caminho\\zabbix-mcp-server\\.venv\\Scripts\\python.exe`).

---

## 2. Erros de Conexão com o Zabbix

### Erro: `ConnectError` ou `TimeoutException`
- **Causa:** O endpoint do Zabbix não está respondendo na URL informada ou há um firewall/bloqueio de rede.
- **Soluções:**
  1. **Verifique a URL:** A URL no `.env` deve apontar para o arquivo `api_jsonrpc.php` (ex: `http://192.168.0.107:8080/api_jsonrpc.php`). Não informe apenas o IP ou porta raiz.
  2. **Teste a conectividade via curl:**
     ```bash
     curl -i http://192.168.0.107:8080/api_jsonrpc.php
     ```
     O Zabbix deve responder com HTTP 412 ou HTTP 200 JSON-RPC.
  3. **Aumente o timeout:** Se o Zabbix estiver em uma rede lenta ou VPN, aumente o timeout no `.env`:
     ```ini
     ZABBIX_TIMEOUT=60.0
     ```

### Erro: `SSLCertVerificationError` (Falha no Certificado SSL/TLS)
- **Causa:** O Zabbix Server utiliza um certificado SSL autoassinado ou corporativo não reconhecido pela autoridade padrão do sistema operacional.
- **Solução:** Desative temporariamente a validação SSL definindo no arquivo `.env`:
  ```ini
  ZABBIX_VERIFY_SSL=false
  ```

---

## 3. Erros de Autenticação e Protocolo JSON-RPC

### Erro: `unexpected parameter "auth"` (Código -32600)
- **Causa:** O Zabbix 7.0+ alterou a especificação da API: o parâmetro `"auth": "<token>"` não é mais aceito no corpo do JSON-RPC, exigindo obrigatoriamente o cabeçalho HTTP `Authorization: Bearer <token>`.
- **Solução:** O `zabbix-mcp-server` gerencia isso automaticamente. Basta configurar o seu token na variável `ZABBIX_TOKEN` no arquivo `.env`.

### Erro: `Not authorized` ou `Session terminated`
- **Causa:** O token de API informado expirou, foi revogado ou não possui privilégios de acesso ao Zabbix.
- **Solução:**
  1. Acesse o Zabbix Web em **Administração** ➔ **Tokens de API**.
  2. Verifique se o token está com status **Ativo** e se a data de expiração não foi ultrapassada.
  3. Se necessário, gere um novo token de 64 caracteres e atualize o `.env`.

---

## 4. Erros de Governança e Permissões (RBAC)

### Erro: `ZabbixPermissionError: Operação bloqueada pelo modo 'somente_leitura'`
- **Causa:** Uma ferramenta de escrita ou alteração (como `zabbix_criar_host`, `zabbix_cadastrar_dispositivos_em_lote` ou `zabbix_atualizar_host`) foi invocada, mas o servidor está operando no modo de segurança padrão `somente_leitura`.
- **Solução:** No arquivo `.env`, altere o nível de autorização para:
  ```ini
  ZABBIX_MCP_MODE=operacional
  ```
  Ou para comandos administrativos:
  ```ini
  ZABBIX_MCP_MODE=administrativo
  ```
  Reinicie o cliente MCP para recarregar as variáveis de ambiente.

### Erro: `ZabbixApprovalRequiredError: A operação requer aprovação explícita`
- **Causa:** Uma ação destrutiva irreversível (como `zabbix_remover_host` ou `zabbix_gerenciar_proxies` com exclusão) foi acionada sem o token de confirmação em 2 passos.
- **Solução:**
  1. Chame primeiro a ferramenta `zabbix_previsualizar_alteracao` ou consulte a prévia para gerar o token HMAC assinado (`apr_...`).
  2. Confirme o comando informando os mesmos parâmetros exatos e o argumento `token_aprovacao="apr_..."` antes que o token expire (15 minutos).
  3. Caso queira desativar a exigência de aprovação em ambiente de laboratório, defina:
     ```ini
     ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE=false
     ```

---

## 5. Erros nos Clientes MCP (Claude Desktop, Antigravity IDE, Cursor)

### Erro: O cliente MCP fecha imediatamente ou não lista as ferramentas
- **Causa:** Caminho incorreto do executável Python no arquivo de configuração do cliente (`claude_desktop_config.json` ou `mcp_config.json`), ou dependências ausentes.
- **Solução:**
  1. Teste o executável Python diretamente no terminal:
     ```bash
     C:\\caminho\\para\\zabbix-mcp-server\\.venv\\Scripts\\python.exe -m zabbix_mcp.server --transport stdio
     ```
  2. Se o comando abrir e aguardar entrada JSON via STDIN sem gerar exceções, o servidor está saudável.
  3. Use barras normais `/` ou barras duplas `\\\\` nos caminhos dentro de arquivos `.json` para evitar erros de escape no Windows.
