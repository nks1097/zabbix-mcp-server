# Guia de Segurança e Conformidade

O Zabbix MCP Server foi projetado seguindo as melhores práticas de DevSecOps e segurança defensiva para monitoramento de missão crítica.

## 1. Princípio do Menor Privilégio (RBAC)

O servidor possui três modos de autorização (`ZABBIX_MCP_MODE`):

1. **`somente_leitura` (Padrão):**
   - O servidor permite unicamente operações de consulta (`host.get`, `item.get`, `problem.get`, relatórios e prévias).
   - Qualquer tentativa de criar, modificar ou excluir objetos resulta em `ZabbixPermissionError`.
2. **`operacional`:**
   - Permite consultas e ações operacionais cotidianas: criação de hosts, adição de interfaces, associação de templates, criação de janelas de manutenção e reconhecimento de problemas.
   - Bloqueia exclusões e alterações administrativas.
3. **`administrativo`:**
   - Habilita controle total, incluindo remoção de hosts, gerenciamento de proxies e execução de automações completas.

## 2. Aprovação em Dois Passos para Ações Destrutivas

Quando `ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE=true` (padrão):
- Ações como `zabbix_remover_host` ou `zabbix_executar_fluxo_aprovado` recusam a execução direta sem um token de aprovação válido.
- O token é gerado via HMAC-SHA256 combinando a ação, os parâmetros exatos e um timestamp com validade máxima de 15 minutos:
  ```text
  apr_<timestamp>_<assinatura_hmac>
  ```
- **Invalidação imediata:** Qualquer alteração nos parâmetros (ex: trocar o `hostid` de 10084 para 10085) invalida o token anterior, prevenindo ataques de confusão de parâmetros.

## 3. Redação Automática de Segredos

Todas as estruturas de dados retornadas e registradas em log passam pela função `redact_sensitive_data`.
Chaves como `password`, `token`, `auth`, `secret`, `privatekey` e `community` têm seus valores substituídos por `[REDACTED]`.

## 4. Proteção contra SSRF e Path Traversal

- **Validação de Rede:** Varreduras de rede bloqueiam o escopo local de loopback (`127.0.0.1`, `::1`), endereços multicast e blocos CIDR maiores que `/22` (1024 IPs).
- **Diretório Seguro de Arquivos:** Relatórios são gravados estritamente dentro de `ZABBIX_REPORTS_DIR`. Nomes de arquivos são sanitizados contra caracteres de quebra de diretório (`..`, `/`, `\`).

## 5. Auditoria Imutável Local

Todas as chamadas MCP são registradas no arquivo JSON Lines configurado em `ZABBIX_AUDIT_LOG_PATH` contendo:
- Timestamp UTC.
- ID único da requisição (`req_...`).
- Nome da ferramenta invocada.
- Parâmetros higienizados (sem senhas).
- Duração da execução em milissegundos.
- Status de sucesso ou mensagem de erro.
- IDs de recursos afetados.

