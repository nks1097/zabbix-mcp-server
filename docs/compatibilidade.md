# Matriz de Compatibilidade de Versões do Zabbix

O Zabbix MCP Server possui detecção automática de versão via `apiinfo.version` e adapta chamadas e cabeçalhos para diferentes versões do Zabbix Server.

## Matriz de Suporte Oficial

| Versão do Zabbix | Status | Autenticação Recomendada | Notas de Compatibilidade |
|---|---|---|---|
| **Zabbix 7.4.x** | **Testado e Homologado** | `Authorization: Bearer <token>` | Versão utilizada no ambiente de validação. Suporte completo a todas as 100 ferramentas. |
| **Zabbix 7.0 LTS** | **Compatível** | `Authorization: Bearer <token>` | Exige cabeçalho HTTP Bearer. Proíbe auth no corpo JSON. Suporte a Proxy Groups e Alta Disponibilidade. |
| **Zabbix 6.4.x** | **Compatível** | Token ou Login de Usuário | Suporte a Bearer ou auth no payload JSON. |
| **Zabbix 6.0 LTS** | **Compatível** | Token ou Login de Usuário | Suporte à API moderna de SLA e HA Cluster. |
| **Zabbix 5.x / 4.x** | Suporte Parcial | Usuário e Senha | Métodos modernos de SLA e novos tipos de templates requerem Zabbix 6.0+. |

## Principais Diferenças Estruturais Tratadas

1. **Autenticação em Tokens de API no Zabbix 7.0+:**
   - No Zabbix 7.0+, passar `"auth": "<token>"` no corpo do JSON resulta no erro:
     `Invalid parameter "/": unexpected parameter "auth"`.
   - O cliente `ZabbixClient` envia o cabeçalho HTTP `Authorization: Bearer <token>` automaticamente.
2. **Grupos de Templates (`templategroup` vs `hostgroup`):**
   - No Zabbix 6.2+, templates possuem grupo próprio (`templategroup`).
   - A ferramenta `zabbix_gerar_grupos_templates` possui fallback transparente para `hostgroup` em versões anteriores.
3. **Módulo de Alta Disponibilidade (`ha.get`):**
   - Disponível a partir do Zabbix 6.0 LTS.
