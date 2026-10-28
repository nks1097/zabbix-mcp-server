# Solução de Problemas e Diagnóstico de Erros

Guia prático para solucionar os erros mais comuns na integração entre o MCP e a API do Zabbix.

## 1. Erro JSON-RPC: `unexpected parameter "auth"` (-32600)
- **Causa:** A instalação é Zabbix 7.0+ e o token de API foi passado no corpo do JSON em vez do cabeçalho HTTP Bearer.
- **Solução:** O `zabbix-mcp-server` trata isso automaticamente enviando `Authorization: Bearer <token>`. Certifique-se de configurar a variável `ZABBIX_TOKEN` no `.env`.

## 2. Erro: `ZabbixPermissionError: Operação bloqueada pelo modo 'somente_leitura'`
- **Causa:** Foi chamada uma ferramenta de escrita (como `zabbix_criar_host` ou `zabbix_cadastrar_dispositivos_em_lote`), mas o servidor está no modo seguro padrão de leitura.
- **Solução:** Altere a variável de ambiente `ZABBIX_MCP_MODE=operacional` ou `ZABBIX_MCP_MODE=administrativo` e reinicie o servidor MCP.

## 3. Erro: `ZabbixApprovalRequiredError: A operação requer aprovação explícita`
- **Causa:** Ação de exclusão ou destrutiva invocada sem o parâmetro `token_aprovacao`.
- **Solução:**
  1. Chame primeiro `zabbix_previsualizar_alteracao` ou consulte a prévia do cadastro para obter o token de aprovação (`apr_...`).
  2. Reenvie o comando fornecendo exatamente os mesmos parâmetros e o `token_aprovacao` correspondente dentro de 15 minutos.

## 4. Erro: `ConnectError` ou `TimeoutException`
- **Causa:** O endpoint do Zabbix (`/api_jsonrpc.php`) não está acessível na rede ou o firewall bloqueou a conexão.
- **Solução:**
  - Verifique se a URL termina com `/api_jsonrpc.php`.
  - Teste a conectividade com `curl http://seu-zabbix:8080/api_jsonrpc.php`.
  - Aumente o timeout configurando `ZABBIX_TIMEOUT=60.0`.

## 5. Erro: `Invalid parameter "/recent": a boolean is expected` (-32602)
- **Causa:** Parâmetros booleanos no Zabbix 7.x exigem booleanos verdadeiros (`true` / `false` em JSON, `True` em Python), e não strings como `"true"`.
- **Solução:** O cliente do `zabbix-mcp` já trata todos os parâmetros como tipos estritos Pydantic.
