# Política de Segurança — Zabbix MCP Server

A segurança da informação e a proteção da infraestrutura de monitoramento são prioridades absolutas neste projeto.

## Versões Suportadas

| Versão | Suportada | Notas |
|---|---|---|
| 1.0.x | Sim | Versão ativa de produção |

## Relatando Vulnerabilidades

Se você identificar uma vulnerabilidade de segurança neste projeto:
1. **NÃO crie uma issue pública.**
2. Envie um e-mail confidencial para `security@example.com` (ou crie um Security Advisory privado no GitHub).
3. Inclua descrição do problema, prova de conceito (PoC) e passos para reprodução segura.
4. Nossa equipe responderá em até 48 horas úteis e disponibilizará um patch corretivo com crédito aos pesquisadores.

## Princípios de Segurança Implementados

1. **Princípio do Menor Privilégio (RBAC):**
   - O servidor opera por padrão no modo `somente_leitura`.
   - Modos `operacional` e `administrativo` exigem ativação deliberada via configuração de ambiente.
2. **Aprovação em Dois Passos para Operações Críticas:**
   - Remoção de hosts, templates, proxies e execução de automações exigem token criptográfico HMAC com expiração de 15 minutos vinculado aos parâmetros exatos.
3. **Proteção contra Vazamento de Segredos:**
   - Tokens, senhas e communities SNMP são redigidos automaticamente em logs e respostas (`[REDACTED]`).
4. **Proteção contra SSRF e Path Traversal:**
   - Varreduras de rede bloqueiam redes loopback (127.0.0.1) e sub-redes com mais de 1024 IPs.
   - Relatórios são gerados exclusivamente dentro do diretório configurado, com sanitização de nomes de arquivos.

