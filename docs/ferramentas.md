# Catálogo Técnico Definitivo das 100 Ferramentas do Zabbix MCP Server

Este documento é o **manual técnico oficial de referência** das 100 ferramentas disponíveis no **Zabbix MCP Server**.
Todas as ferramentas seguem a especificação oficial do **Model Context Protocol (MCP)**, nomes em `snake_case`, validação estrita com **Pydantic**, descrições em português e controle de permissões por perfil (**RBAC**).

Todas as ferramentas retornam a estrutura padrão `ToolResult` padronizada:
```json
{
  "sucesso": true,
  "dados": { ... },
  "erro": null,
  "avisos": [],
  "duracao_ms": 24.5,
  "versao_zabbix": "7.4.15",
  "truncado": false
}
```

---

## Índice das 10 Categorias de Ferramentas

- [Categoria 1 — Descoberta Automática de Dispositivos](#categoria-1-descoberta-automatica-de-dispositivos)
- [Categoria 2 — Hosts e Interfaces](#categoria-2-hosts-e-interfaces)
- [Categoria 3 — Coleta de Dados e Métricas](#categoria-3-coleta-de-dados-e-metricas)
- [Categoria 4 — Problemas, Triggers e Eventos](#categoria-4-problemas,-triggers-e-eventos)
- [Categoria 5 — Relatórios e Exportações](#categoria-5-relatorios-e-exportacões)
- [Categoria 6 — Alertas, Ações e Notificações](#categoria-6-alertas,-acões-e-notificacões)
- [Categoria 7 — Serviços de Negócio, Manutenções e Mapas](#categoria-7-servicos-de-negocio,-manutencões-e-mapas)
- [Categoria 8 — Inventário, Grupos e Templates](#categoria-8-inventario,-grupos-e-templates)
- [Categoria 9 — Descoberta Nativa, Proxies e Administração](#categoria-9-descoberta-nativa,-proxies-e-administracão)
- [Categoria 10 — Automação, Análise e Diagnóstico Holístico](#categoria-10-automacão,-analise-e-diagnostico-holistico)

---


## Categoria 1 — Descoberta Automática de Dispositivos

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 01 | [`zabbix_descobrir_rede`](#001-zabbix-descobrir-rede) | `Operacional` | Realiza uma varredura controlada e não-intrusiva em faixas de rede CIDR IPv4 explicitamente autorizadas. |
| 02 | [`zabbix_analisar_dispositivo`](#002-zabbix-analisar-dispositivo) | `Somente Leitura` | Analisa detalhadamente um endereço IP específico, coletando latência, hostname reverso via DNS (PTR), portas abertas fundamentais (22/SSH, 80/HTTP, 443/HTTPS, 161/SNMP, 10050/Agent, 3389/RDP, 445/SMB) e evidências preliminares de identificação. |
| 03 | [`zabbix_identificar_sistema_operacional`](#003-zabbix-identificar-sistema-operacional) | `Somente Leitura` | Infere o sistema operacional provável (Linux, Windows Server, Appliance de Rede, Servidor Web) a partir de assinaturas de portas e comportamento de rede, retornando o nome do SO e um percentual de confiança. |
| 04 | [`zabbix_identificar_servicos`](#004-zabbix-identificar-servicos) | `Somente Leitura` | Mapeia serviços monitoráveis em execução no host (servidores HTTP/Nginx/Apache, bancos de dados MySQL/PostgreSQL, SSH, Docker, SNMP) através de sondagens não-invasivas em portas bem conhecidas. |
| 05 | [`zabbix_deduplicar_dispositivos`](#005-zabbix-deduplicar-dispositivos) | `Somente Leitura` | Verifica se um dispositivo descoberto já se encontra cadastrado no Zabbix Server, comparando endereços IP de interfaces, nomes visíveis, nomes técnicos e resolução DNS. |
| 06 | [`zabbix_comparar_dispositivos_cadastrados`](#006-zabbix-comparar-dispositivos-cadastrados) | `Somente Leitura` | Cruza uma lista de IPs descobertos com todos os hosts atualmente cadastrados no Zabbix, gerando um balanço categorizado: novos nós a cadastrar, nós já monitorados e possíveis divergências de configuração. |
| 07 | [`zabbix_recomendar_templates`](#007-zabbix-recomendar-templates) | `Somente Leitura` | Cruza o sistema operacional e serviços detectados com o acervo de templates instalados no Zabbix, recomendando os templates oficiais mais indicados com seus respectivos IDs. |
| 08 | [`zabbix_previsualizar_cadastro`](#008-zabbix-previsualizar-cadastro) | `Somente Leitura` | Simula a criação do host no Zabbix (Dry-Run), apresentando a estrutura JSON exata dos parâmetros: nome técnico, nome visível, interfaces, grupos, templates vinculados e macros, sem gravar alterações. |
| 09 | [`zabbix_cadastrar_dispositivos_em_lote`](#009-zabbix-cadastrar-dispositivos-em-lote) | `Operacional` | Cria múltiplos hosts aprovados no Zabbix de forma transacional e segura. |
| 10 | [`zabbix_verificar_descoberta`](#010-zabbix-verificar-descoberta) | `Somente Leitura` | Audita o estado pós-implantação dos hosts criados: confirma se a interface está ativa, se os templates foram herdados, se os itens estão criados e se os primeiros dados de telemetria já chegaram. |


### 001. `zabbix_descobrir_rede`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Realiza uma varredura controlada e não-intrusiva em faixas de rede CIDR IPv4 explicitamente autorizadas. Utiliza testes rápidos de ICMP e conectividade TCP nas portas essenciais de infraestrutura para descobrir quais nós estão vivos e respondendo.
- **Quando usar:** Utilize na etapa inicial de mapeamento de novos ambientes, expansão de datacenters ou auditorias programadas de inventário de rede.
- **Exemplo Prático / Cenário:** Descobrir todos os dispositivos ativos no segmento do datacenter '192.168.0.0/24' com limite de 50 pacotes por segundo.

**Parâmetros de Entrada:**
- `faixa_cidr` (*str*, **Obrigatório**)
- `confirmar_escopo_autorizado` (*bool*, Opcional, Padrão: `False`)
- `portas` (*Optional*, Opcional)
- `limite_hosts` (*int*, Opcional, Padrão: `64`)

---

### 002. `zabbix_analisar_dispositivo`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Analisa detalhadamente um endereço IP específico, coletando latência, hostname reverso via DNS (PTR), portas abertas fundamentais (22/SSH, 80/HTTP, 443/HTTPS, 161/SNMP, 10050/Agent, 3389/RDP, 445/SMB) e evidências preliminares de identificação.
- **Quando usar:** Logo após a descoberta de um IP vivo, antes de iniciar o cadastro, para entender a natureza técnica do ativo.
- **Exemplo Prático / Cenário:** Inspecionar o IP '192.168.0.107' para identificar se possui porta do Zabbix Agent (10050) ou porta SNMP (161) aberta.

**Parâmetros de Entrada:**
- `ip` (*str*, **Obrigatório**)
- `portas` (*Optional*, Opcional)

---

### 003. `zabbix_identificar_sistema_operacional`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Infere o sistema operacional provável (Linux, Windows Server, Appliance de Rede, Servidor Web) a partir de assinaturas de portas e comportamento de rede, retornando o nome do SO e um percentual de confiança.
- **Quando usar:** Para selecionar automaticamente a família correta de templates de monitoramento (ex: Linux by Zabbix agent vs Windows by Zabbix agent).
- **Exemplo Prático / Cenário:** Classificar um nó com portas 22 e 80 abertas como 'Linux' com 90% de confiança.

**Parâmetros de Entrada:**
- `ip` (*str*, **Obrigatório**)
- `portas_abertas` (*List*, **Obrigatório**)

---

### 004. `zabbix_identificar_servicos`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Mapeia serviços monitoráveis em execução no host (servidores HTTP/Nginx/Apache, bancos de dados MySQL/PostgreSQL, SSH, Docker, SNMP) através de sondagens não-invasivas em portas bem conhecidas.
- **Quando usar:** Para identificar quais templates de aplicação e serviços devem ser associados ao host além do sistema operacional base.
- **Exemplo Prático / Cenário:** Identificar se um servidor Linux possui o serviço 'MySQL (3306)' e 'HTTPS (443)' ativos.

**Parâmetros de Entrada:**
- `ip` (*str*, **Obrigatório**)
- `portas_abertas` (*List*, **Obrigatório**)

---

### 005. `zabbix_deduplicar_dispositivos`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Verifica se um dispositivo descoberto já se encontra cadastrado no Zabbix Server, comparando endereços IP de interfaces, nomes visíveis, nomes técnicos e resolução DNS.
- **Quando usar:** Imprescindível antes da criação de qualquer host para impedir a duplicação de cadastros e poluição do banco de dados.
- **Exemplo Prático / Cenário:** Verificar se o IP '192.168.0.107' já está associado ao host 'Zabbix server'.

**Parâmetros de Entrada:**
- `dispositivos` (*List*, **Obrigatório**)

---

### 006. `zabbix_comparar_dispositivos_cadastrados`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Cruza uma lista de IPs descobertos com todos os hosts atualmente cadastrados no Zabbix, gerando um balanço categorizado: novos nós a cadastrar, nós já monitorados e possíveis divergências de configuração.
- **Quando usar:** Em auditorias periódicas para identificar 'máquinas fantasmas' operando na rede sem monitoramento corporativo.
- **Exemplo Prático / Cenário:** Comparar uma lista de 50 IPs varridos no datacenter com os 45 hosts cadastrados no grupo 'Datacenter SP'.

**Parâmetros de Entrada:**
- `ips_descobertos` (*List*, **Obrigatório**)

---

### 007. `zabbix_recomendar_templates`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Cruza o sistema operacional e serviços detectados com o acervo de templates instalados no Zabbix, recomendando os templates oficiais mais indicados com seus respectivos IDs.
- **Quando usar:** Para automatizar a etapa de vinculação de templates (linking) sem necessidade de pesquisa manual pelo operador.
- **Exemplo Prático / Cenário:** Obter os templateids de 'Linux by Zabbix agent' e 'Nginx by HTTP' para um servidor web descoberto.

**Parâmetros de Entrada:**
- `sistema_operacional` (*str*, **Obrigatório**)
- `portas_abertas` (*List*, **Obrigatório**)
- `tipo_dispositivo` (*str*, Opcional, Padrão: `generico`)

---

### 008. `zabbix_previsualizar_cadastro`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Simula a criação do host no Zabbix (Dry-Run), apresentando a estrutura JSON exata dos parâmetros: nome técnico, nome visível, interfaces, grupos, templates vinculados e macros, sem gravar alterações.
- **Quando usar:** Para aprovação visual humana ou validação por agentes de IA antes de aplicar a gravação no ambiente de produção.
- **Exemplo Prático / Cenário:** Revisar previamente o payload de onboarding do host 'srv-app-prod01' antes de executar a criação.

**Parâmetros de Entrada:**
- `dispositivo` (*Dict*, **Obrigatório**)
- `grupo_destino` (*str*, Opcional, Padrão: `Discovered hosts`)
- `templates` (*Optional*, Opcional)

---

### 009. `zabbix_cadastrar_dispositivos_em_lote`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria múltiplos hosts aprovados no Zabbix de forma transacional e segura. Processa item por item registrando sucessos e capturando eventuais erros individuais sem interromper a fila.
- **Quando usar:** Na etapa final de onboarding de lotes de equipamentos após a conclusão e aprovação da descoberta de rede.
- **Exemplo Prático / Cenário:** Cadastrar 15 novos switches de borda configurando interface SNMP v2c e associando ao grupo 'Switches'.

**Parâmetros de Entrada:**
- `previsoes` (*List*, **Obrigatório**)
- `token_aprovacao` (*Optional*, Opcional)

---

### 010. `zabbix_verificar_descoberta`

- **Categoria:** Categoria 1 — Descoberta Automática de Dispositivos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Audita o estado pós-implantação dos hosts criados: confirma se a interface está ativa, se os templates foram herdados, se os itens estão criados e se os primeiros dados de telemetria já chegaram.
- **Quando usar:** Logo após o cadastro em lote (Estágio F) para atestar a conformidade da nova instalação e emitir o checklist de entrega.
- **Exemplo Prático / Cenário:** Validar se os 15 switches cadastrados já estão com a interface SNMP verde e coletando tráfego de interface.

**Parâmetros de Entrada:**
- `hostids` (*List*, **Obrigatório**)

---


## Categoria 2 — Hosts e Interfaces

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 11 | [`zabbix_listar_hosts`](#011-zabbix-listar-hosts) | `Somente Leitura` | Lista os hosts monitorados no Zabbix aplicando filtros flexíveis por nome, grupo de hosts, status de monitoramento (habilitado/desabilitado) e estado de disponibilidade de interface. |
| 12 | [`zabbix_consultar_host`](#012-zabbix-consultar-host) | `Somente Leitura` | Retorna o registro completo e detalhado de um host específico no Zabbix, incluindo interfaces de rede, grupos vinculados, templates herdados, macros, status e metadados de inventário. |
| 13 | [`zabbix_criar_host`](#013-zabbix-criar-host) | `Operacional` | Cria um novo host no Zabbix com parâmetros estritamente validados: nome técnico, nome visível, endereço IP ou DNS, porta, tipo de interface (Agent, SNMP, IPMI, JMX), grupos e templates. |
| 14 | [`zabbix_atualizar_host`](#014-zabbix-atualizar-host) | `Operacional` | Atualiza propriedades permitidas de um host existente, como nome visível, descrição, status de monitoramento, grupos associados e macros. |
| 15 | [`zabbix_remover_host`](#015-zabbix-remover-host) | `Administrativo (Exige Aprovação HMAC)` | Exclui permanentemente um host do Zabbix juntamente com todo o seu histórico de dados e configurações. |
| 16 | [`zabbix_ativar_desativar_host`](#016-zabbix-ativar-desativar-host) | `Operacional` | Altera o status operacional de monitoramento de um host entre 0 (Monitorado/Ativo) e 1 (Não monitorado/Desativado), pausando temporariamente todas as checagens e alertas. |
| 17 | [`zabbix_gerenciar_interfaces_host`](#017-zabbix-gerenciar-interfaces-host) | `Operacional` | Cria, consulta e atualiza interfaces de comunicação de um host (Zabbix Agent, SNMP v1/v2c/v3, IPMI, JMX), definindo porta, IP, DNS e interface primária. |
| 18 | [`zabbix_associar_templates_host`](#018-zabbix-associar-templates-host) | `Operacional` | Vincula um ou mais templates a um host existente no Zabbix preservando intactos todos os templates que já estavam previamente vinculados. |
| 19 | [`zabbix_desassociar_templates_host`](#019-zabbix-desassociar-templates-host) | `Operacional` | Remove a associação de templates de um host, oferecendo a opção de limpeza (unlink_and_clear) para remover do host os itens e gráficos herdados daquele template. |
| 20 | [`zabbix_consultar_disponibilidade_host`](#020-zabbix-consultar-disponibilidade-host) | `Somente Leitura` | Inspeciona o estado operacional das interfaces de comunicação do host (Agent, SNMP, IPMI, JMX): se estão disponíveis (1), indisponíveis com erro (2) ou desconhecidas (0), exibindo mensagens de erro de polling se houver. |


### 011. `zabbix_listar_hosts`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista os hosts monitorados no Zabbix aplicando filtros flexíveis por nome, grupo de hosts, status de monitoramento (habilitado/desabilitado) e estado de disponibilidade de interface.
- **Quando usar:** Para pesquisar servidores, listar ativos de um grupo específico ou obter um panorama de inventário.
- **Exemplo Prático / Cenário:** Listar todos os hosts ativos pertencentes ao grupo 'Linux servers'.

**Parâmetros de Entrada:**
- `nome` (*Optional*, Opcional)
- `grupo` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 012. `zabbix_consultar_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Retorna o registro completo e detalhado de um host específico no Zabbix, incluindo interfaces de rede, grupos vinculados, templates herdados, macros, status e metadados de inventário.
- **Quando usar:** Quando for necessário diagnosticar a configuração técnica profunda de um servidor ou equipamento.
- **Exemplo Prático / Cenário:** Consultar a configuração detalhada do hostid '10084' (Zabbix server).

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)
- `nome` (*Optional*, Opcional)

---

### 013. `zabbix_criar_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria um novo host no Zabbix com parâmetros estritamente validados: nome técnico, nome visível, endereço IP ou DNS, porta, tipo de interface (Agent, SNMP, IPMI, JMX), grupos e templates.
- **Quando usar:** Para cadastrar individualmente um servidor, roteador, switch ou máquina virtual no Zabbix.
- **Exemplo Prático / Cenário:** Criar o host 'db-postgres-01' com interface de Agente no IP 192.168.0.50 no grupo 'Database'.

**Parâmetros de Entrada:**
- `host` (*str*, **Obrigatório**)
- `ip` (*str*, **Obrigatório**)
- `grupos_ids` (*List*, **Obrigatório**)
- `nome_visivel` (*Optional*, Opcional)
- `porta` (*str*, Opcional, Padrão: `10050`)
- `tipo_interface` (*int*, Opcional, Padrão: `1`)
- `templates_ids` (*Optional*, Opcional)
- `campos_inventario` (*Optional*, Opcional)

---

### 014. `zabbix_atualizar_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Atualiza propriedades permitidas de um host existente, como nome visível, descrição, status de monitoramento, grupos associados e macros.
- **Quando usar:** Para atualizar descrições operacionais, renomear hosts ou reclassificar grupos sem recriar o ativo.
- **Exemplo Prático / Cenário:** Atualizar a descrição do host '10084' para 'Servidor Zabbix Central - Datacenter Principal'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `nome_visivel` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)
- `descricao` (*Optional*, Opcional)

---

### 015. `zabbix_remover_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Administrativo (Exige Aprovação HMAC)`
- **Para que serve:** Exclui permanentemente um host do Zabbix juntamente com todo o seu histórico de dados e configurações. Operação destrutiva protegida por token criptográfico de aprovação em dois passos.
- **Quando usar:** Para desativar e expurgar definitivamente da base de monitoramento servidores descomissionados.
- **Exemplo Prático / Cenário:** Excluir o host descomissionado '10650' mediante fornecimento de justificativa e token de confirmação HMAC.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `token_aprovacao` (*Optional*, Opcional)

---

### 016. `zabbix_ativar_desativar_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Altera o status operacional de monitoramento de um host entre 0 (Monitorado/Ativo) e 1 (Não monitorado/Desativado), pausando temporariamente todas as checagens e alertas.
- **Quando usar:** Durante manutenções emergenciais ou paradas prolongadas de servidores onde não se deseja disparar falsos alarmes.
- **Exemplo Prático / Cenário:** Desativar temporariamente o monitoramento do host '10084' para manutenção de hardware.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `status` (*int*, **Obrigatório**)

---

### 017. `zabbix_gerenciar_interfaces_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria, consulta e atualiza interfaces de comunicação de um host (Zabbix Agent, SNMP v1/v2c/v3, IPMI, JMX), definindo porta, IP, DNS e interface primária.
- **Quando usar:** Ao adicionar uma interface SNMP secundária em um servidor ou alterar o IP de gerenciamento de um equipamento.
- **Exemplo Prático / Cenário:** Adicionar interface SNMP v2c (porta 161) com community 'public' ao hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `acao` (*str*, **Obrigatório**)
- `interface_dados` (*Optional*, Opcional)

---

### 018. `zabbix_associar_templates_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Vincula um ou mais templates a um host existente no Zabbix preservando intactos todos os templates que já estavam previamente vinculados.
- **Quando usar:** Para adicionar monitoramento complementar em um host (ex: adicionar template de Docker ou MySQL em um servidor já monitorado por Linux).
- **Exemplo Prático / Cenário:** Vincular o templateid '10200' (MySQL by Zabbix agent) ao hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `templates_ids` (*List*, **Obrigatório**)

---

### 019. `zabbix_desassociar_templates_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Remove a associação de templates de um host, oferecendo a opção de limpeza (unlink_and_clear) para remover do host os itens e gráficos herdados daquele template.
- **Quando usar:** Ao remover um serviço obsoleto de um servidor ou trocar a estratégia de templates de monitoramento.
- **Exemplo Prático / Cenário:** Desvincular o template 'Apache by HTTP' e limpar seus itens após migração para Nginx.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `templates_ids` (*List*, **Obrigatório**)
- `limpar_itens_triggers` (*bool*, Opcional, Padrão: `False`)

---

### 020. `zabbix_consultar_disponibilidade_host`

- **Categoria:** Categoria 2 — Hosts e Interfaces
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Inspeciona o estado operacional das interfaces de comunicação do host (Agent, SNMP, IPMI, JMX): se estão disponíveis (1), indisponíveis com erro (2) ou desconhecidas (0), exibindo mensagens de erro de polling se houver.
- **Quando usar:** Para verificar rapidamente se o Zabbix Server consegue conversar com o agente ou SNMP do host monitorado.
- **Exemplo Prático / Cenário:** Verificar se a interface do Zabbix Agent no host '10084' está respondendo normalmente ou com erro de conexão.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)

---


## Categoria 3 — Coleta de Dados e Métricas

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 21 | [`zabbix_listar_itens`](#021-zabbix-listar-itens) | `Somente Leitura` | Lista os itens de telemetria cadastrados no Zabbix com filtros por host, chave de item (ex: system. |
| 22 | [`zabbix_consultar_item`](#022-zabbix-consultar-item) | `Somente Leitura` | Recupera a configuração completa de um item específico: chave, intervalo de atualização, período de retenção de histórico/trends, tipo de valor, pré-processamento e estado de erro. |
| 23 | [`zabbix_criar_item`](#023-zabbix-criar-item) | `Operacional` | Cria um novo item de coleta customizado em um host com chave, tipo de informação, intervalo de atualização e parâmetros validados. |
| 24 | [`zabbix_atualizar_item`](#024-zabbix-atualizar-item) | `Operacional` | Modifica parâmetros permitidos de um item de coleta, como intervalo de atualização (delay), período de histórico, status (habilitado/desabilitado) e descrição. |
| 25 | [`zabbix_consultar_historico`](#025-zabbix-consultar-historico) | `Somente Leitura` | Recupera os registros históricos pontuais de valores de um ou mais itens em uma janela temporal (numéricos float, inteiros, strings ou logs), com ordenação cronológica. |
| 26 | [`zabbix_consultar_tendencias`](#026-zabbix-consultar-tendencias) | `Somente Leitura` | Recupera dados consolidados por hora de tendências estatísticas (trends: valor mínimo, médio e máximo) calculados pelo Zabbix para longos períodos de tempo. |
| 27 | [`zabbix_ultimos_valores`](#027-zabbix-ultimos-valores) | `Somente Leitura` | Consulta a última leitura válida recebida (lastvalue), horário da última coleta e unidade de medida de todos os itens ou de itens filtrados de um host. |
| 28 | [`zabbix_verificar_coleta`](#028-zabbix-verificar-coleta) | `Somente Leitura` | Analisa se os itens habilitados estão realmente recebendo dados dentro do intervalo esperado (delay), identificando itens atrasados ou com erros de polling. |
| 29 | [`zabbix_detectar_lacunas_coleta`](#029-zabbix-detectar-lacunas-coleta) | `Somente Leitura` | Examina o histórico de um item e detecta 'buracos' ou lacunas temporais (gaps) onde dados deveriam ter sido coletados mas não foram, calculando a duração de cada falha. |
| 30 | [`zabbix_diagnosticar_coleta`](#030-zabbix-diagnosticar-coleta) | `Somente Leitura` | Produz um diagnóstico inteligente correlacionando erros de itens não suportados (unsupported items), indisponibilidade de interface e atrasos na fila de coleta do host. |


### 021. `zabbix_listar_itens`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista os itens de telemetria cadastrados no Zabbix com filtros por host, chave de item (ex: system.cpu.util), tipo de checagem e status de coleta.
- **Quando usar:** Para encontrar métricas específicas de um host ou auditar quais dados estão sendo coletados.
- **Exemplo Prático / Cenário:** Listar todos os itens de uso de CPU e memória pertencentes ao hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)
- `chave` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 022. `zabbix_consultar_item`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera a configuração completa de um item específico: chave, intervalo de atualização, período de retenção de histórico/trends, tipo de valor, pré-processamento e estado de erro.
- **Quando usar:** Para inspecionar por que determinado item não está coletando ou conferir seu intervalo de polling.
- **Exemplo Prático / Cenário:** Consultar a configuração do itemid '42240' (system.cpu.load).

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)

---

### 023. `zabbix_criar_item`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria um novo item de coleta customizado em um host com chave, tipo de informação, intervalo de atualização e parâmetros validados.
- **Quando usar:** Para adicionar métricas sob demanda que não façam parte de templates padrão (ex: checagem de script customizado ou UserParameter).
- **Exemplo Prático / Cenário:** Criar um item 'custom.app.health' com intervalo de 60s do tipo Zabbix Agent no host '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `name` (*str*, **Obrigatório**)
- `key_` (*str*, **Obrigatório**)
- `type` (*int*, Opcional, Padrão: `0`)
- `value_type` (*int*, Opcional, Padrão: `3`)
- `interfaceid` (*Optional*, Opcional)
- `delay` (*str*, Opcional, Padrão: `1m`)
- `units` (*Optional*, Opcional)

---

### 024. `zabbix_atualizar_item`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Modifica parâmetros permitidos de um item de coleta, como intervalo de atualização (delay), período de histórico, status (habilitado/desabilitado) e descrição.
- **Quando usar:** Para diminuir a frequência de coleta de um item muito pesado ou reativar um item suspenso.
- **Exemplo Prático / Cenário:** Aumentar o delay do item 'system.cpu.util' de 1m para 5m para poupar recursos.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `name` (*Optional*, Opcional)
- `delay` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)

---

### 025. `zabbix_consultar_historico`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera os registros históricos pontuais de valores de um ou mais itens em uma janela temporal (numéricos float, inteiros, strings ou logs), com ordenação cronológica.
- **Quando usar:** Para traçar gráficos, analisar comportamento de métricas em um incidente recente ou alimentar modelos de análise.
- **Exemplo Prático / Cenário:** Consultar os valores de uso de CPU do host '10084' nas últimas 2 horas.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `historico_tipo` (*int*, Opcional, Padrão: `0`)
- `limite` (*int*, Opcional, Padrão: `50`)
- `tempo_de` (*Optional*, Opcional)
- `tempo_ate` (*Optional*, Opcional)

---

### 026. `zabbix_consultar_tendencias`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera dados consolidados por hora de tendências estatísticas (trends: valor mínimo, médio e máximo) calculados pelo Zabbix para longos períodos de tempo.
- **Quando usar:** Para estudos de capacidade (capacity planning), relatórios mensais e análises de longo prazo (semanas/meses).
- **Exemplo Prático / Cenário:** Consultar o histórico mensal consolidado de consumo de disco dos últimos 90 dias.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `tempo_de` (*int*, **Obrigatório**)
- `tempo_ate` (*int*, **Obrigatório**)

---

### 027. `zabbix_ultimos_valores`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta a última leitura válida recebida (lastvalue), horário da última coleta e unidade de medida de todos os itens ou de itens filtrados de um host.
- **Quando usar:** Para obter a 'fotografia atual' de telemetria de um host (CPU atual, RAM livre, uptime atual) em tempo real.
- **Exemplo Prático / Cenário:** Descobrir o valor atual da métrica 'vm.memory.size[available]' no host '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `filtro_chave` (*Optional*, Opcional)

---

### 028. `zabbix_verificar_coleta`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Analisa se os itens habilitados estão realmente recebendo dados dentro do intervalo esperado (delay), identificando itens atrasados ou com erros de polling.
- **Quando usar:** Para auditar a saúde da ingestão de métricas e diagnosticar se algum agente travou ou perdeu comunicação.
- **Exemplo Prático / Cenário:** Verificar se há itens desatualizados ou sem coleta há mais de 10 minutos no hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)

---

### 029. `zabbix_detectar_lacunas_coleta`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Examina o histórico de um item e detecta 'buracos' ou lacunas temporais (gaps) onde dados deveriam ter sido coletados mas não foram, calculando a duração de cada falha.
- **Quando usar:** Para investigar instabilidades intermitentes de rede ou paradas não registradas de serviços.
- **Exemplo Prático / Cenário:** Detectar se houve perda de pacotes ou interrupção na coleta de tráfego de rede durante a madrugada.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `tempo_de` (*int*, **Obrigatório**)
- `tempo_ate` (*int*, **Obrigatório**)
- `tolerancia_multiplicador` (*float*, Opcional, Padrão: `3.0`)

---

### 030. `zabbix_diagnosticar_coleta`

- **Categoria:** Categoria 3 — Coleta de Dados e Métricas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Produz um diagnóstico inteligente correlacionando erros de itens não suportados (unsupported items), indisponibilidade de interface e atrasos na fila de coleta do host.
- **Quando usar:** Para troubleshooting rápido quando um host recém-cadastrado não começa a plotar gráficos ou apresenta itens em estado vermelho.
- **Exemplo Prático / Cenário:** Diagnosticar por que determinados itens de disco estão como 'Not supported' no host '10084'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)

---


## Categoria 4 — Problemas, Triggers e Eventos

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 31 | [`zabbix_listar_problemas`](#031-zabbix-listar-problemas) | `Somente Leitura` | Lista incidentes e problemas ativos no ambiente com suporte a filtros por severidade (Informational até Disaster), host, grupo, status de reconhecimento e tags. |
| 32 | [`zabbix_consultar_problema`](#032-zabbix-consultar-problema) | `Somente Leitura` | Retorna os detalhes analíticos completos de um problema específico: evento gerador, trigger associada, tags, tempo de duração, severidade e mensagens de reconhecimento. |
| 33 | [`zabbix_consultar_eventos`](#033-zabbix-consultar-eventos) | `Somente Leitura` | Consulta a linha do tempo de eventos de problemas (geração e recuperação) no Zabbix, permitindo filtrar por janela temporal, host e severidade. |
| 34 | [`zabbix_listar_triggers`](#034-zabbix-listar-triggers) | `Somente Leitura` | Lista as regras de alerta (triggers) configuradas no Zabbix com seus respectivos estados (0=OK, 1=Problem), expressões de gatilho, severidades e status (ativa/inativa). |
| 35 | [`zabbix_consultar_trigger`](#035-zabbix-consultar-trigger) | `Somente Leitura` | Recupera a definição técnica detalhada de uma trigger: expressão matemática exata, expressão de recuperação, prioridade, modo de geração de eventos e dependências. |
| 36 | [`zabbix_criar_trigger`](#036-zabbix-criar-trigger) | `Operacional` | Cria uma nova regra de trigger customizada vinculada a itens de um host com expressão sintaticamente validada e nível de severidade configurável. |
| 37 | [`zabbix_atualizar_trigger`](#037-zabbix-atualizar-trigger) | `Operacional` | Atualiza propriedades permitidas de uma trigger: expressão, severidade, status de habilitação, descrição e tags de correlação. |
| 38 | [`zabbix_reconhecer_problema`](#038-zabbix-reconhecer-problema) | `Operacional` | Registra o reconhecimento formal (Acknowledge) de um problema ativo no Zabbix, permitindo anexar uma mensagem de justificativa/chamado e opcionalmente alterar a severidade ou fechar o evento. |
| 39 | [`zabbix_obter_historico_problema`](#039-zabbix-obter-historico-problema) | `Somente Leitura` | Recupera o histórico completo de ações de um problema: quando iniciou, quem reconheceu, comentários adicionados, escalonamentos de notificação e horário de fechamento. |
| 40 | [`zabbix_investigar_incidente`](#040-zabbix-investigar-incidente) | `Somente Leitura` | Executa uma investigação holística de causa raiz para um incidente: correlaciona o problema com as métricas do host no exato momento da falha, eventos concomitantes e alertas relacionados. |


### 031. `zabbix_listar_problemas`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista incidentes e problemas ativos no ambiente com suporte a filtros por severidade (Informational até Disaster), host, grupo, status de reconhecimento e tags.
- **Quando usar:** Para operadores de NOC e equipes de SRE monitorarem a fila de alarmes ativos no ambiente.
- **Exemplo Prático / Cenário:** Listar todos os problemas não reconhecidos com severidade Alta ou Desastre no grupo 'Produção'.

**Parâmetros de Entrada:**
- `severidade_minima` (*Optional*, Opcional)
- `hostid` (*Optional*, Opcional)
- `reconhecido` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 032. `zabbix_consultar_problema`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Retorna os detalhes analíticos completos de um problema específico: evento gerador, trigger associada, tags, tempo de duração, severidade e mensagens de reconhecimento.
- **Quando usar:** Para aprofundar a investigação sobre um alarme específico disparado no painel.
- **Exemplo Prático / Cenário:** Consultar o histórico e causa raiz do problemid '55420'.

**Parâmetros de Entrada:**
- `eventid` (*str*, **Obrigatório**)

---

### 033. `zabbix_consultar_eventos`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta a linha do tempo de eventos de problemas (geração e recuperação) no Zabbix, permitindo filtrar por janela temporal, host e severidade.
- **Quando usar:** Para análise de pós-morte (Post-Mortem), auditorias de indisponibilidade e cálculo de MTTR (Mean Time to Resolve).
- **Exemplo Prático / Cenário:** Recuperar todos os eventos de queda de link ocorridos nas últimas 24 horas.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)
- `tempo_de` (*Optional*, Opcional)
- `tempo_ate` (*Optional*, Opcional)
- `severidade` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)

---

### 034. `zabbix_listar_triggers`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista as regras de alerta (triggers) configuradas no Zabbix com seus respectivos estados (0=OK, 1=Problem), expressões de gatilho, severidades e status (ativa/inativa).
- **Quando usar:** Para auditar regras de alerta configuradas em um host ou template.
- **Exemplo Prático / Cenário:** Listar todas as triggers associadas ao hostid '10084' que monitoram espaço em disco.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 035. `zabbix_consultar_trigger`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera a definição técnica detalhada de uma trigger: expressão matemática exata, expressão de recuperação, prioridade, modo de geração de eventos e dependências.
- **Quando usar:** Para inspecionar a lógica exata de cálculo de um alerta ou verificar dependências entre triggers.
- **Exemplo Prático / Cenário:** Consultar a expressão da trigger 'High CPU utilization' (triggerid '15200').

**Parâmetros de Entrada:**
- `triggerid` (*str*, **Obrigatório**)

---

### 036. `zabbix_criar_trigger`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria uma nova regra de trigger customizada vinculada a itens de um host com expressão sintaticamente validada e nível de severidade configurável.
- **Quando usar:** Para implementar novos alertas de negócio ou limites específicos de infraestrutura.
- **Exemplo Prático / Cenário:** Criar trigger de alerta quando a fila de mensagens RabbitMQ ultrapassar 1000 mensagens por 5 minutos.

**Parâmetros de Entrada:**
- `description` (*str*, **Obrigatório**)
- `expression` (*str*, **Obrigatório**)
- `priority` (*int*, Opcional, Padrão: `3`)
- `comments` (*Optional*, Opcional)

---

### 037. `zabbix_atualizar_trigger`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Atualiza propriedades permitidas de uma trigger: expressão, severidade, status de habilitação, descrição e tags de correlação.
- **Quando usar:** Para ajustar limiares de alertas que estejam gerando falso-positivo ou silenciar temporariamente um gatilho.
- **Exemplo Prático / Cenário:** Elevar a severidade de uma trigger de 'Warning' para 'High' e atualizar seu threshold para 90%.

**Parâmetros de Entrada:**
- `triggerid` (*str*, **Obrigatório**)
- `priority` (*Optional*, Opcional)
- `status` (*Optional*, Opcional)
- `comments` (*Optional*, Opcional)

---

### 038. `zabbix_reconhecer_problema`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Registra o reconhecimento formal (Acknowledge) de um problema ativo no Zabbix, permitindo anexar uma mensagem de justificativa/chamado e opcionalmente alterar a severidade ou fechar o evento.
- **Quando usar:** Para que analistas de NOC indiquem que o incidente já está em atendimento pelo time técnico.
- **Exemplo Prático / Cenário:** Reconhecer o problemid '55420' com a mensagem 'Incidente em análise sob chamado INC-8921'.

**Parâmetros de Entrada:**
- `eventid` (*str*, **Obrigatório**)
- `mensagem` (*str*, **Obrigatório**)
- `acao` (*int*, Opcional, Padrão: `6`)

---

### 039. `zabbix_obter_historico_problema`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera o histórico completo de ações de um problema: quando iniciou, quem reconheceu, comentários adicionados, escalonamentos de notificação e horário de fechamento.
- **Quando usar:** Para auditoria de atendimento de chamados e conformidade de SLAs operacionais.
- **Exemplo Prático / Cenário:** Obter toda a trilha de comentários e escalonamentos do incidente '55420'.

**Parâmetros de Entrada:**
- `eventid` (*str*, **Obrigatório**)

---

### 040. `zabbix_investigar_incidente`

- **Categoria:** Categoria 4 — Problemas, Triggers e Eventos
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Executa uma investigação holística de causa raiz para um incidente: correlaciona o problema com as métricas do host no exato momento da falha, eventos concomitantes e alertas relacionados.
- **Quando usar:** Para que um agente de IA ou analista entenda instantaneamente o contexto completo de uma queda ou lentidão severa.
- **Exemplo Prático / Cenário:** Investigar o incidente '55420' correlacionando uso de CPU, I/O de disco e tráfego de rede no horário do evento.

**Parâmetros de Entrada:**
- `eventid` (*str*, **Obrigatório**)

---


## Categoria 5 — Relatórios e Exportações

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 41 | [`zabbix_gerar_relatorio_executivo`](#041-zabbix-gerar-relatorio-executivo) | `Somente Leitura` | Consolida indicadores executivos do ambiente: total de hosts monitorados, distribuição por severidade de problemas ativos, taxa geral de saúde e principais gargalos em formato de alto nível. |
| 42 | [`zabbix_gerar_relatorio_disponibilidade`](#042-zabbix-gerar-relatorio-disponibilidade) | `Somente Leitura` | Calcula a disponibilidade percentual (uptime vs downtime) de hosts e serviços no período selecionado, fundamentado em dados reais de triggers e eventos. |
| 43 | [`zabbix_gerar_relatorio_problemas`](#043-zabbix-gerar-relatorio-problemas) | `Somente Leitura` | Agrupa e analisa todos os incidentes ocorridos no período por severidade, tempo médio de duração, hosts mais incidentados (Top Problematic Hosts) e taxa de resolução. |
| 44 | [`zabbix_gerar_relatorio_desempenho`](#044-zabbix-gerar-relatorio-desempenho) | `Somente Leitura` | Analisa o perfil de consumo de recursos computacionais (CPU, memória RAM, tráfego de rede e espaço em disco) apontando picos, médias e desvios de capacidade. |
| 45 | [`zabbix_gerar_relatorio_inventario`](#045-zabbix-gerar-relatorio-inventario) | `Somente Leitura` | Mapeia todo o parque instalado: sistemas operacionais, localizações físicas/virtuais, números de série, versões de software e cobertura de monitoramento por grupo. |
| 46 | [`zabbix_gerar_relatorio_capacidade`](#046-zabbix-gerar-relatorio-capacidade) | `Somente Leitura` | Analisa tendências de consumo de armazenamento (disco) e memória para prever dias até a exaustão (Days Until Full / Runway) com base no crescimento histórico. |
| 47 | [`zabbix_gerar_relatorio_sla`](#047-zabbix-gerar-relatorio-sla) | `Somente Leitura` | Calcula os índices de cumprimento de acordos de nível de serviço (SLA) para serviços de negócio configurados, apontando tempo de conformidade e violações. |
| 48 | [`zabbix_exportar_relatorio_pdf`](#048-zabbix-exportar-relatorio-pdf) | `Somente Leitura` | Converte os dados de qualquer relatório estruturado em um documento PDF corporativo profissional, com cabeçalho, tabelas zebradas, sumário executivo e layout limpo. |
| 49 | [`zabbix_exportar_relatorio_excel`](#049-zabbix-exportar-relatorio-excel) | `Somente Leitura` | Gera planilhas nativas em formato Microsoft Excel (. |
| 50 | [`zabbix_agendar_relatorio`](#050-zabbix-agendar-relatorio) | `Operacional` | Configura agendamentos nativos de relatórios no Zabbix Server (Zabbix 6. |


### 041. `zabbix_gerar_relatorio_executivo`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consolida indicadores executivos do ambiente: total de hosts monitorados, distribuição por severidade de problemas ativos, taxa geral de saúde e principais gargalos em formato de alto nível.
- **Quando usar:** Para apresentações a diretorias, reuniões executivas e acompanhamento gerencial diário da infraestrutura.
- **Exemplo Prático / Cenário:** Gerar um resumo executivo em PDF com visão geral de saúde de toda a infraestrutura.

**Parâmetros de Entrada:**
- `periodo_dias` (*int*, Opcional, Padrão: `7`)
- `grupo_nome` (*Optional*, Opcional)

---

### 042. `zabbix_gerar_relatorio_disponibilidade`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Calcula a disponibilidade percentual (uptime vs downtime) de hosts e serviços no período selecionado, fundamentado em dados reais de triggers e eventos.
- **Quando usar:** Para comprovação de metas contratuais e relatórios formais de disponibilidade mensal ou semanal.
- **Exemplo Prático / Cenário:** Emitir relatório de disponibilidade dos servidores de banco de dados nos últimos 30 dias.

**Parâmetros de Entrada:**
- `periodo_dias` (*int*, Opcional, Padrão: `30`)
- `grupo_nome` (*Optional*, Opcional)

---

### 043. `zabbix_gerar_relatorio_problemas`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Agrupa e analisa todos os incidentes ocorridos no período por severidade, tempo médio de duração, hosts mais incidentados (Top Problematic Hosts) e taxa de resolução.
- **Quando usar:** Para análise de tendências de problemas e identificação dos ativos que mais geram instabilidade na operação.
- **Exemplo Prático / Cenário:** Gerar relatório de incidentes dos últimos 7 dias destacando os servidores mais instáveis.

**Parâmetros de Entrada:**
- `periodo_dias` (*int*, Opcional, Padrão: `7`)
- `severidade_minima` (*int*, Opcional, Padrão: `2`)

---

### 044. `zabbix_gerar_relatorio_desempenho`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Analisa o perfil de consumo de recursos computacionais (CPU, memória RAM, tráfego de rede e espaço em disco) apontando picos, médias e desvios de capacidade.
- **Quando usar:** Para dimensionamento de máquinas virtuais, detecção de gargalos de processamento e auditoria de performance.
- **Exemplo Prático / Cenário:** Gerar relatório de consumo de CPU e RAM dos clusters de aplicação.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)

---

### 045. `zabbix_gerar_relatorio_inventario`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Mapeia todo o parque instalado: sistemas operacionais, localizações físicas/virtuais, números de série, versões de software e cobertura de monitoramento por grupo.
- **Quando usar:** Em auditorias de ativos de TI, renovações de contratos e compliance de segurança da informação.
- **Exemplo Prático / Cenário:** Exportar o inventário completo de todos os servidores Linux cadastrados.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 046. `zabbix_gerar_relatorio_capacidade`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Analisa tendências de consumo de armazenamento (disco) e memória para prever dias até a exaustão (Days Until Full / Runway) com base no crescimento histórico.
- **Quando usar:** Para planejamento de expansão de storage, previsão orçamentária e prevenção de paradas por disco cheio.
- **Exemplo Prático / Cenário:** Gerar relatório preditivo de esgotamento de disco dos volumes de banco de dados para os próximos 6 meses.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)

---

### 047. `zabbix_gerar_relatorio_sla`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Calcula os índices de cumprimento de acordos de nível de serviço (SLA) para serviços de negócio configurados, apontando tempo de conformidade e violações.
- **Quando usar:** Para prestação de contas a clientes internos ou externos sobre serviços críticos (ERP, E-commerce, APIs).
- **Exemplo Prático / Cenário:** Emitir relatório mensal de SLA do serviço 'Portal do Cliente' contra a meta de 99.9% de disponibilidade.

**Parâmetros de Entrada:**
- `slaid` (*Optional*, Opcional)

---

### 048. `zabbix_exportar_relatorio_pdf`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Converte os dados de qualquer relatório estruturado em um documento PDF corporativo profissional, com cabeçalho, tabelas zebradas, sumário executivo e layout limpo.
- **Quando usar:** Quando for necessário enviar um relatório formal por e-mail para diretores, clientes ou equipes de auditoria.
- **Exemplo Prático / Cenário:** Exportar o relatório de disponibilidade mensal diretamente para o arquivo 'disponibilidade_outubro.pdf'.

**Parâmetros de Entrada:**
- `tipo_relatorio` (*str*, Opcional, Padrão: `executivo`)
- `periodo_dias` (*int*, Opcional, Padrão: `7`)
- `nome_arquivo` (*str*, Opcional, Padrão: `relatorio_zabbix.pdf`)

---

### 049. `zabbix_exportar_relatorio_excel`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Gera planilhas nativas em formato Microsoft Excel (.xlsx) com múltiplas abas, cabeçalhos estilizados, filtros e formatação numérica adequada.
- **Quando usar:** Para analistas de dados e engenheiros que precisam manipular, filtrar e cruzar métricas em planilhas.
- **Exemplo Prático / Cenário:** Exportar todos os dados brutos de inventário e problemas para 'inventario_geral.xlsx'.

**Parâmetros de Entrada:**
- `tipo_relatorio` (*str*, Opcional, Padrão: `executivo`)
- `periodo_dias` (*int*, Opcional, Padrão: `7`)
- `nome_arquivo` (*str*, Opcional, Padrão: `relatorio_zabbix.xlsx`)

---

### 050. `zabbix_agendar_relatorio`

- **Categoria:** Categoria 5 — Relatórios e Exportações
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Configura agendamentos nativos de relatórios no Zabbix Server (Zabbix 6.0+) definindo periodicidade, destinatários e parâmetros de envio.
- **Quando usar:** Para automatizar a entrega semanal ou mensal de relatórios gerenciais diretamente na caixa de entrada dos gestores.
- **Exemplo Prático / Cenário:** Agendar o envio semanal do relatório de disponibilidade toda segunda-feira às 08:00.

**Parâmetros de Entrada:**
- `nome` (*str*, **Obrigatório**)
- `periodo` (*str*, Opcional, Padrão: `semanal`)
- `email_destinatario` (*Optional*, Opcional)

---


## Categoria 6 — Alertas, Ações e Notificações

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 51 | [`zabbix_listar_alertas`](#051-zabbix-listar-alertas) | `Somente Leitura` | Consulta a fila de alertas gerados pelo Zabbix, permitindo filtrar por destinatário, período, canal de mídia (E-mail, Telegram, Slack) e status de envio (enviado/falhou). |
| 52 | [`zabbix_consultar_acoes`](#052-zabbix-consultar-acoes) | `Somente Leitura` | Lista as regras de ações (actions) configuradas no Zabbix para tratamento de triggers, descoberta de rede, autorregistro ou serviços internos. |
| 53 | [`zabbix_consultar_historico_notificacoes`](#053-zabbix-consultar-historico-notificacoes) | `Somente Leitura` | Recupera o histórico cronológico de notificações enviadas para um determinado usuário ou host, facilitando a correlação de alertas. |
| 54 | [`zabbix_listar_canais_notificacao`](#054-zabbix-listar-canais-notificacao) | `Somente Leitura` | Lista os tipos de mídia (media types) configurados no Zabbix Server (SMTP, SMS, Webhooks para Jira/ServiceNow/Teams/Slack, scripts personalizados). |
| 55 | [`zabbix_testar_canal_notificacao`](#055-zabbix-testar-canal-notificacao) | `Operacional` | Dispara um teste controlado de envio através de um tipo de mídia específico para validar a conectividade e integridade das credenciais configuradas. |
| 56 | [`zabbix_gerenciar_acoes`](#056-zabbix-gerenciar-acoes) | `Operacional` | Habilita, desabilita ou atualiza as propriedades operacionais de uma regra de ação do Zabbix. |
| 57 | [`zabbix_consultar_regras_escalonamento`](#057-zabbix-consultar-regras-escalonamento) | `Somente Leitura` | Consulta a árvore de escalonamento configurada em uma ação (ex: Passo 1: notificar NOC; Passo 2 após 30m: notificar Coordenador; Passo 3 após 1h: notificar Gerente). |
| 58 | [`zabbix_suprimir_notificacoes`](#058-zabbix-suprimir-notificacoes) | `Operacional` | Aplica supressão temporária manual de notificações para um problema específico ou host, impedindo o envio de novos alertas sem desativar a coleta. |
| 59 | [`zabbix_analisar_falsos_positivos`](#059-zabbix-analisar-falsos-positivos) | `Somente Leitura` | Examina o histórico recente de eventos para identificar triggers com comportamento de 'flapping' (oscilação contínua entre Problem e OK em curtos intervalos). |
| 60 | [`zabbix_recomendar_ajustes_alertas`](#060-zabbix-recomendar-ajustes-alertas) | `Somente Leitura` | Com base no histórico e nas oscilações de métricas, propõe ajustes técnicos fundamentados em triggers (ex: adicionar função min() ou max(), aumentar tempo de avaliação de 1m para 5m). |


### 051. `zabbix_listar_alertas`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta a fila de alertas gerados pelo Zabbix, permitindo filtrar por destinatário, período, canal de mídia (E-mail, Telegram, Slack) e status de envio (enviado/falhou).
- **Quando usar:** Para auditar se as notificações estão sendo devidamente entregues ou identificar falhas de comunicação com servidores de correio/webhooks.
- **Exemplo Prático / Cenário:** Verificar todos os alertas de e-mail disparados na última hora.

**Parâmetros de Entrada:**
- `eventid` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 052. `zabbix_consultar_acoes`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista as regras de ações (actions) configuradas no Zabbix para tratamento de triggers, descoberta de rede, autorregistro ou serviços internos.
- **Quando usar:** Para auditar quais regras de automação disparam notificações quando determinados alarmes ocorrem.
- **Exemplo Prático / Cenário:** Listar todas as ações ativas responsáveis pelo envio de mensagens para o Telegram do plantão.

**Parâmetros de Entrada:**
- `eventsource` (*int*, Opcional, Padrão: `0`)

---

### 053. `zabbix_consultar_historico_notificacoes`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera o histórico cronológico de notificações enviadas para um determinado usuário ou host, facilitando a correlação de alertas.
- **Quando usar:** Para investigar por que um plantonista alega não ter recebido notificação de um incidente crítico.
- **Exemplo Prático / Cenário:** Consultar todas as notificações enviadas para o usuário 'Admin' nos últimos 3 dias.

**Parâmetros de Entrada:**
- `tempo_de` (*Optional*, Opcional)
- `tempo_ate` (*Optional*, Opcional)
- `apenas_falhas` (*bool*, Opcional, Padrão: `False`)

---

### 054. `zabbix_listar_canais_notificacao`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista os tipos de mídia (media types) configurados no Zabbix Server (SMTP, SMS, Webhooks para Jira/ServiceNow/Teams/Slack, scripts personalizados).
- **Quando usar:** Para verificar quais canais de comunicação estão disponíveis e ativos no ambiente.
- **Exemplo Prático / Cenário:** Listar os webhooks configurados para integração com o sistema de tickets da empresa.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 055. `zabbix_testar_canal_notificacao`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Dispara um teste controlado de envio através de um tipo de mídia específico para validar a conectividade e integridade das credenciais configuradas.
- **Quando usar:** Ao configurar uma nova integração com Telegram, Discord ou servidor SMTP corporativo.
- **Exemplo Prático / Cenário:** Testar o canal de webhook do Slack enviando uma mensagem de teste controlada.

**Parâmetros de Entrada:**
- `mediatypeid` (*str*, **Obrigatório**)
- `destinatario` (*str*, **Obrigatório**)
- `mensagem` (*str*, Opcional, Padrão: `Teste controlado de envio via Zabbix MCP Server`)
- `confirmar_envio` (*bool*, Opcional, Padrão: `False`)

---

### 056. `zabbix_gerenciar_acoes`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Habilita, desabilita ou atualiza as propriedades operacionais de uma regra de ação do Zabbix.
- **Quando usar:** Para pausar temporariamente ações de disparo de tickets em massa durante uma janela de manutenção geral.
- **Exemplo Prático / Cenário:** Desabilitar a ação 'Notificar Plantão por SMS' durante a manutenção programada de rede.

**Parâmetros de Entrada:**
- `acao_tipo` (*str*, **Obrigatório**)
- `actionid` (*str*, **Obrigatório**)
- `nome` (*Optional*, Opcional)

---

### 057. `zabbix_consultar_regras_escalonamento`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta a árvore de escalonamento configurada em uma ação (ex: Passo 1: notificar NOC; Passo 2 após 30m: notificar Coordenador; Passo 3 após 1h: notificar Gerente).
- **Quando usar:** Para validar fluxos de escalonamento de incidentes e garantir conformidade com as diretrizes de governança.
- **Exemplo Prático / Cenário:** Auditar a regra de escalonamento da ação de alarmes de nível 'Desastre'.

**Parâmetros de Entrada:**
- `actionid` (*str*, **Obrigatório**)

---

### 058. `zabbix_suprimir_notificacoes`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Aplica supressão temporária manual de notificações para um problema específico ou host, impedindo o envio de novos alertas sem desativar a coleta.
- **Quando usar:** Quando um incidente conhecido já está sendo trabalhado e não se deseja sobrecarregar a caixa postal do time com alertas repetidos.
- **Exemplo Prático / Cenário:** Suprimir alertas do problemid '55420' por 2 horas durante a aplicação de um patch.

**Parâmetros de Entrada:**
- `eventids` (*List*, **Obrigatório**)
- `suprimir_ate` (*int*, **Obrigatório**)

---

### 059. `zabbix_analisar_falsos_positivos`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Examina o histórico recente de eventos para identificar triggers com comportamento de 'flapping' (oscilação contínua entre Problem e OK em curtos intervalos).
- **Quando usar:** Em rotinas de higiene do monitoramento para erradicar a 'fadiga de alertas' gerada por gatilhos excessivamente sensíveis.
- **Exemplo Prático / Cenário:** Descobrir quais triggers geraram mais de 50 transições de estado nas últimas 24 horas.

**Parâmetros de Entrada:**
- `periodo_dias` (*int*, Opcional, Padrão: `7`)

---

### 060. `zabbix_recomendar_ajustes_alertas`

- **Categoria:** Categoria 6 — Alertas, Ações e Notificações
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Com base no histórico e nas oscilações de métricas, propõe ajustes técnicos fundamentados em triggers (ex: adicionar função min() ou max(), aumentar tempo de avaliação de 1m para 5m).
- **Quando usar:** Para otimizar e calibrar triggers barulhentas sem alterar a infraestrutura sem revisão prévia.
- **Exemplo Prático / Cenário:** Obter recomendação de calibração para a trigger de latência de link WAN.

**Parâmetros de Entrada:**
- `triggerid` (*str*, **Obrigatório**)

---


## Categoria 7 — Serviços de Negócio, Manutenções e Mapas

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 61 | [`zabbix_listar_servicos`](#061-zabbix-listar-servicos) | `Somente Leitura` | Lista a árvore de Business Services (Serviços de Negócio) configurada no Zabbix, exibindo hierarquia pai-filho e status de saúde consolidado. |
| 62 | [`zabbix_consultar_servico`](#062-zabbix-consultar-servico) | `Somente Leitura` | Retorna os detalhes de um serviço de negócio específico: regras de propagação de status, triggers filhas associadas, pesos e tags de correlação. |
| 63 | [`zabbix_criar_servico`](#063-zabbix-criar-servico) | `Operacional` | Cria um novo serviço de negócio no catálogo de serviços do Zabbix, definindo seu algoritmo de cálculo de status (qualquer filho falha, todos falham, etc. |
| 64 | [`zabbix_atualizar_servico`](#064-zabbix-atualizar-servico) | `Operacional` | Atualiza propriedades, regras de avaliação e dependências de um serviço de negócio existente. |
| 65 | [`zabbix_consultar_sla_servico`](#065-zabbix-consultar-sla-servico) | `Somente Leitura` | Calcula os indicadores SLI (Service Level Indicator) e o cumprimento de metas de SLA para um serviço em períodos específicos (semanal, mensal, anual). |
| 66 | [`zabbix_listar_manutencoes`](#066-zabbix-listar-manutencoes) | `Somente Leitura` | Lista todas as janelas de manutenção cadastradas no Zabbix (ativas, agendadas ou expiradas) com tipo de manutenção (com ou sem coleta de dados) e hosts afetados. |
| 67 | [`zabbix_criar_manutencao`](#067-zabbix-criar-manutencao) | `Operacional` | Cria uma nova janela de manutenção com horários de início e término estritos, escopo de hosts/grupos e definição se a coleta de dados deve ser mantida ou suspensa. |
| 68 | [`zabbix_atualizar_manutencao`](#068-zabbix-atualizar-manutencao) | `Operacional` | Modifica o período ou a lista de hosts contemplados em uma janela de manutenção já existente. |
| 69 | [`zabbix_consultar_mapas`](#069-zabbix-consultar-mapas) | `Somente Leitura` | Recupera as configurações e nós de mapas de topologia visual cadastrados no Zabbix. |
| 70 | [`zabbix_gerar_mapa_monitoramento`](#070-zabbix-gerar-mapa-monitoramento) | `Somente Leitura` | Gera dinamicamente uma representação gráfica de mapa em formato Markdown/Mermaid a partir dos hosts, grupos e status reais consultados na API do Zabbix. |


### 061. `zabbix_listar_servicos`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista a árvore de Business Services (Serviços de Negócio) configurada no Zabbix, exibindo hierarquia pai-filho e status de saúde consolidado.
- **Quando usar:** Para visões focadas no negócio (ex: 'Sistema ERP', 'Gateway de Pagamentos') em vez de focar apenas no servidor físico isolado.
- **Exemplo Prático / Cenário:** Listar todos os serviços de topo (root services) e seus status atuais.

**Parâmetros de Entrada:**
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 062. `zabbix_consultar_servico`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Retorna os detalhes de um serviço de negócio específico: regras de propagação de status, triggers filhas associadas, pesos e tags de correlação.
- **Quando usar:** Para entender qual componente subjacente está impactando a disponibilidade de um serviço de negócio.
- **Exemplo Prático / Cenário:** Consultar por que o serviço de negócio 'Portal Web' está em estado de alerta.

**Parâmetros de Entrada:**
- `serviceid` (*str*, **Obrigatório**)

---

### 063. `zabbix_criar_servico`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria um novo serviço de negócio no catálogo de serviços do Zabbix, definindo seu algoritmo de cálculo de status (qualquer filho falha, todos falham, etc.) e serviço pai.
- **Quando usar:** Ao modelar a arquitetura de monitoramento de uma nova aplicação corporativa.
- **Exemplo Prático / Cenário:** Criar o serviço 'Cluster Kubernetes de Produção' associado ao serviço pai 'Infraestrutura Cloud'.

**Parâmetros de Entrada:**
- `name` (*str*, **Obrigatório**)
- `algorithm` (*int*, Opcional, Padrão: `1`)
- `sortorder` (*int*, Opcional, Padrão: `0`)
- `parent_serviceid` (*Optional*, Opcional)

---

### 064. `zabbix_atualizar_servico`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Atualiza propriedades, regras de avaliação e dependências de um serviço de negócio existente.
- **Quando usar:** Ao adicionar novos microserviços à composição de um serviço corporativo.
- **Exemplo Prático / Cenário:** Alterar a regra de cálculo de status do serviço 'E-commerce' para exigir 2 falhas simultâneas.

**Parâmetros de Entrada:**
- `serviceid` (*str*, **Obrigatório**)
- `name` (*Optional*, Opcional)
- `algorithm` (*Optional*, Opcional)

---

### 065. `zabbix_consultar_sla_servico`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Calcula os indicadores SLI (Service Level Indicator) e o cumprimento de metas de SLA para um serviço em períodos específicos (semanal, mensal, anual).
- **Quando usar:** Para avaliar o consumo de Error Budget (Orçamento de Erro) e atestar a qualidade contratual de entrega.
- **Exemplo Prático / Cenário:** Consultar o SLA consolidado do serviço 'API Gateway' no mês corrente.

**Parâmetros de Entrada:**
- `serviceid` (*str*, **Obrigatório**)
- `periodo_dias` (*int*, Opcional, Padrão: `30`)

---

### 066. `zabbix_listar_manutencoes`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista todas as janelas de manutenção cadastradas no Zabbix (ativas, agendadas ou expiradas) com tipo de manutenção (com ou sem coleta de dados) e hosts afetados.
- **Quando usar:** Para verificar se há janelas de manutenção ativas no ambiente ou consultar agendamentos futuros.
- **Exemplo Prático / Cenário:** Listar janelas de manutenção programadas para o próximo fim de semana.

**Parâmetros de Entrada:**
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 067. `zabbix_criar_manutencao`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria uma nova janela de manutenção com horários de início e término estritos, escopo de hosts/grupos e definição se a coleta de dados deve ser mantida ou suspensa.
- **Quando usar:** Antes de iniciar uma atualização de software, troca de hardware ou janela de homologação.
- **Exemplo Prático / Cenário:** Agendar manutenção no grupo 'Servidores de Banco' das 22:00 às 04:00 com supressão de alertas.

**Parâmetros de Entrada:**
- `name` (*str*, **Obrigatório**)
- `active_since` (*int*, **Obrigatório**)
- `active_till` (*int*, **Obrigatório**)
- `hostids` (*Optional*, Opcional)
- `groupids` (*Optional*, Opcional)
- `description` (*Optional*, Opcional)

---

### 068. `zabbix_atualizar_manutencao`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Modifica o período ou a lista de hosts contemplados em uma janela de manutenção já existente.
- **Quando usar:** Para prorrogar uma janela de manutenção cujo procedimento técnico demorou mais que o previsto.
- **Exemplo Prático / Cenário:** Estender a janela de manutenção 'Upgrade de Storage' por mais 2 horas.

**Parâmetros de Entrada:**
- `maintenanceid` (*str*, **Obrigatório**)
- `active_till` (*Optional*, Opcional)
- `description` (*Optional*, Opcional)

---

### 069. `zabbix_consultar_mapas`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera as configurações e nós de mapas de topologia visual cadastrados no Zabbix.
- **Quando usar:** Para inspecionar diagramas de infraestrutura cadastrados pelos administradores do Zabbix.
- **Exemplo Prático / Cenário:** Consultar os elementos e conexões do mapa 'Topologia Datacenter SP'.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 070. `zabbix_gerar_mapa_monitoramento`

- **Categoria:** Categoria 7 — Serviços de Negócio, Manutenções e Mapas
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Gera dinamicamente uma representação gráfica de mapa em formato Markdown/Mermaid a partir dos hosts, grupos e status reais consultados na API do Zabbix.
- **Quando usar:** Para visualizar visualmente e instantaneamente a relação entre servidores, banco de dados e switches na documentação ou relatórios.
- **Exemplo Prático / Cenário:** Gerar um diagrama Mermaid da topologia atual dos servidores do grupo 'Produção'.

**Parâmetros de Entrada:**
- `grupo_nome` (*Optional*, Opcional)

---


## Categoria 8 — Inventário, Grupos e Templates

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 71 | [`zabbix_consultar_inventario`](#071-zabbix-consultar-inventario) | `Somente Leitura` | Recupera os campos detalhados de inventário de um host (hardware, sistema operacional, localização geográfica, responsável técnico, número de série, vendor, notas). |
| 72 | [`zabbix_atualizar_inventario`](#072-zabbix-atualizar-inventario) | `Operacional` | Atualiza campos de inventário permitidos de um host (modo de inventário manual/automático, tags, local físico, notas de suporte, etc. |
| 73 | [`zabbix_listar_grupos_hosts`](#073-zabbix-listar-grupos-hosts) | `Somente Leitura` | Lista todos os grupos de hosts (hostgroups) cadastrados no Zabbix com seus respectivos IDs e nomes. |
| 74 | [`zabbix_gerenciar_grupos_hosts`](#074-zabbix-gerenciar-grupos-hosts) | `Operacional` | Cria, renomeia ou remove grupos de hosts no Zabbix, validando a não-existência de hosts dependentes antes de qualquer exclusão. |
| 75 | [`zabbix_listar_templates`](#075-zabbix-listar-templates) | `Somente Leitura` | Lista os templates disponíveis no Zabbix, permitindo filtrar por nome ou grupo de templates. |
| 76 | [`zabbix_consultar_template`](#076-zabbix-consultar-template) | `Somente Leitura` | Inspeciona profundamente um template específico: itens, triggers, protótipos de descoberta (LLD), gráficos, dashboards e macros herdadas. |
| 77 | [`zabbix_criar_template`](#077-zabbix-criar-template) | `Operacional` | Cria um novo template no Zabbix com parâmetros validados, associando-o ao grupo de templates adequado. |
| 78 | [`zabbix_atualizar_template`](#078-zabbix-atualizar-template) | `Operacional` | Atualiza propriedades, nome visível, descrição e macros de um template existente. |
| 79 | [`zabbix_gerenciar_grupos_templates`](#079-zabbix-gerenciar-grupos-templates) | `Operacional` | Gerencia a criação e listagem de grupos de templates, compatível com a separação entre hostgroups e templategroups introduzida a partir do Zabbix 6. |
| 80 | [`zabbix_auditar_cobertura_templates`](#080-zabbix-auditar-cobertura-templates) | `Somente Leitura` | Audita todo o Zabbix em busca de falhas de governança: hosts ativos sem nenhum template vinculado, templates órfãos sem nenhum host e discrepâncias de padronização. |


### 071. `zabbix_consultar_inventario`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera os campos detalhados de inventário de um host (hardware, sistema operacional, localização geográfica, responsável técnico, número de série, vendor, notas).
- **Quando usar:** Para consultar dados cadastrais e patrimoniais vinculados ao servidor monitorado.
- **Exemplo Prático / Cenário:** Consultar a localização de rack e contato do responsável do hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 072. `zabbix_atualizar_inventario`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Atualiza campos de inventário permitidos de um host (modo de inventário manual/automático, tags, local físico, notas de suporte, etc.).
- **Quando usar:** Para manter o CMDB atualizado com dados de novos responsáveis, mudanças de rack ou informações de suporte.
- **Exemplo Prático / Cenário:** Atualizar o campo 'location' para 'Rack A4 - Datacenter Curitiba' e 'contact' para 'suporte@empresa.com'.

**Parâmetros de Entrada:**
- `hostid` (*str*, **Obrigatório**)
- `campos_inventario` (*Dict*, **Obrigatório**)
- `modo_inventario` (*int*, Opcional, Padrão: `1`)

---

### 073. `zabbix_listar_grupos_hosts`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista todos os grupos de hosts (hostgroups) cadastrados no Zabbix com seus respectivos IDs e nomes.
- **Quando usar:** Para pesquisar os grupos existentes antes de criar novos servidores ou associar permissões.
- **Exemplo Prático / Cenário:** Listar todos os grupos de hosts cadastrados no ambiente.

**Parâmetros de Entrada:**
- `nome` (*Optional*, Opcional)

---

### 074. `zabbix_gerenciar_grupos_hosts`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria, renomeia ou remove grupos de hosts no Zabbix, validando a não-existência de hosts dependentes antes de qualquer exclusão.
- **Quando usar:** Para criar novas estruturas organizacionais (ex: criar grupo 'Cloud AWS / EKS') ou reorganizar a taxonomia da empresa.
- **Exemplo Prático / Cenário:** Criar o novo grupo de hosts 'Datacenter Secundário - Brasília'.

**Parâmetros de Entrada:**
- `acao` (*str*, **Obrigatório**)
- `nome` (*Optional*, Opcional)
- `groupid` (*Optional*, Opcional)
- `token_aprovacao` (*Optional*, Opcional)

---

### 075. `zabbix_listar_templates`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista os templates disponíveis no Zabbix, permitindo filtrar por nome ou grupo de templates.
- **Quando usar:** Para descobrir quais templates de sistema operacional, banco de dados ou rede estão instalados e prontos para uso.
- **Exemplo Prático / Cenário:** Pesquisar templates disponíveis contendo 'PostgreSQL' ou 'Nginx'.

**Parâmetros de Entrada:**
- `nome` (*Optional*, Opcional)
- `limite` (*int*, Opcional, Padrão: `50`)
- `offset` (*int*, Opcional, Padrão: `0`)

---

### 076. `zabbix_consultar_template`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Inspeciona profundamente um template específico: itens, triggers, protótipos de descoberta (LLD), gráficos, dashboards e macros herdadas.
- **Quando usar:** Para analisar o que um template irá monitorar antes de vinculá-lo a servidores de produção.
- **Exemplo Prático / Cenário:** Consultar todas as macros e regras de descoberta do template 'Linux by Zabbix agent'.

**Parâmetros de Entrada:**
- `templateid` (*str*, **Obrigatório**)

---

### 077. `zabbix_criar_template`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Cria um novo template no Zabbix com parâmetros validados, associando-o ao grupo de templates adequado.
- **Quando usar:** Para iniciar a criação de um template customizado para monitoramento de uma aplicação proprietária.
- **Exemplo Prático / Cenário:** Criar o template 'Custom ERP Microservices Template' no grupo de templates corporativos.

**Parâmetros de Entrada:**
- `host` (*str*, **Obrigatório**)
- `name` (*Optional*, Opcional)
- `grupos_ids` (*Optional*, Opcional)
- `description` (*Optional*, Opcional)

---

### 078. `zabbix_atualizar_template`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Atualiza propriedades, nome visível, descrição e macros de um template existente.
- **Quando usar:** Para atualizar a documentação ou padrões de um template compartilhado entre várias equipes.
- **Exemplo Prático / Cenário:** Atualizar a descrição e valor padrão de macros no template 'Custom ERP'.

**Parâmetros de Entrada:**
- `templateid` (*str*, **Obrigatório**)
- `name` (*Optional*, Opcional)
- `description` (*Optional*, Opcional)

---

### 079. `zabbix_gerenciar_grupos_templates`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Gerencia a criação e listagem de grupos de templates, compatível com a separação entre hostgroups e templategroups introduzida a partir do Zabbix 6.2+.
- **Quando usar:** Para organizar o repositório de templates por fabricante, área de negócio ou tecnologia.
- **Exemplo Prático / Cenário:** Listar os grupos específicos de templates no Zabbix 7.0.

**Parâmetros de Entrada:**
- `acao` (*str*, Opcional, Padrão: `listar`)
- `nome` (*Optional*, Opcional)

---

### 080. `zabbix_auditar_cobertura_templates`

- **Categoria:** Categoria 8 — Inventário, Grupos e Templates
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Audita todo o Zabbix em busca de falhas de governança: hosts ativos sem nenhum template vinculado, templates órfãos sem nenhum host e discrepâncias de padronização.
- **Quando usar:** Em auditorias periódicas de qualidade para garantir que nenhum ativo fique desprotegido.
- **Exemplo Prático / Cenário:** Identificar todos os hosts da empresa que estão cadastrados mas não possuem nenhum template associado.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---


## Categoria 9 — Descoberta Nativa, Proxies e Administração

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 81 | [`zabbix_listar_regras_descoberta`](#081-zabbix-listar-regras-descoberta) | `Somente Leitura` | Lista as regras nativas de Descoberta de Rede (Network Discovery Rules - drule) configuradas no Zabbix Server/Proxy. |
| 82 | [`zabbix_gerenciar_regras_descoberta`](#082-zabbix-gerenciar-regras-descoberta) | `Operacional` | Habilita, desabilita ou altera propriedades de regras nativas de descoberta de rede (drule). |
| 83 | [`zabbix_consultar_descoberta_baixo_nivel`](#083-zabbix-consultar-descoberta-baixo-nivel) | `Somente Leitura` | Consulta as regras LLD (Low-Level Discovery) e protótipos de itens, triggers e gráficos de um host ou template. |
| 84 | [`zabbix_listar_proxies`](#084-zabbix-listar-proxies) | `Somente Leitura` | Lista todos os proxies de monitoramento distribuído cadastrados no Zabbix, indicando se operam em modo Ativo ou Passivo e seus respectivos status. |
| 85 | [`zabbix_consultar_proxy`](#085-zabbix-consultar-proxy) | `Somente Leitura` | Inspeciona detalhadamente o estado operacional de um proxy: última comunicação (lastaccess), lista de hosts atribuídos e endereço de conexão. |
| 86 | [`zabbix_gerenciar_proxies`](#086-zabbix-gerenciar-proxies) | `Administrativo (Exige Aprovação HMAC para exclusão)` | Cadastra, atualiza ou remove configurações de proxies no Zabbix Server. |
| 87 | [`zabbix_consultar_usuarios`](#087-zabbix-consultar-usuarios) | `Somente Leitura` | Lista os usuários cadastrados no Zabbix com seus respectivos grupos e funções de acesso, com redação automática e mascaramento estrito de senhas ou tokens. |
| 88 | [`zabbix_consultar_funcoes_usuario`](#088-zabbix-consultar-funcoes-usuario) | `Somente Leitura` | Consulta os papéis de acesso (User Roles) e conjuntos de permissões configurados no Zabbix (Admin, Super Admin, User). |
| 89 | [`zabbix_consultar_auditoria`](#089-zabbix-consultar-auditoria) | `Somente Leitura` | Consulta os logs de auditoria nativos do Zabbix (Audit Log), registrando quem alterou, criou ou excluiu qualquer objeto no ambiente com IP de origem e timestamp. |
| 90 | [`zabbix_consultar_estado_sistema`](#090-zabbix-consultar-estado-sistema) | `Somente Leitura` | Recupera a versão da API do Zabbix, nós do cluster de Alta Disponibilidade (HA nodes se habilitado), tamanho da fila de itens atrasados e integridade geral do servidor. |


### 081. `zabbix_listar_regras_descoberta`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista as regras nativas de Descoberta de Rede (Network Discovery Rules - drule) configuradas no Zabbix Server/Proxy.
- **Quando usar:** Para consultar as regras periódicas nativas de varredura de sub-redes configuradas no Zabbix.
- **Exemplo Prático / Cenário:** Listar as regras nativas de descoberta de rede configuradas no Zabbix.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 082. `zabbix_gerenciar_regras_descoberta`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Habilita, desabilita ou altera propriedades de regras nativas de descoberta de rede (drule).
- **Quando usar:** Para ativar ou pausar a varredura nativa do Zabbix em determinadas sub-redes.
- **Exemplo Prático / Cenário:** Pausar a regra nativa de descoberta de rede da filial para manutenção.

**Parâmetros de Entrada:**
- `acao` (*str*, **Obrigatório**)
- `druleid` (*str*, **Obrigatório**)
- `iprange` (*Optional*, Opcional)

---

### 083. `zabbix_consultar_descoberta_baixo_nivel`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta as regras LLD (Low-Level Discovery) e protótipos de itens, triggers e gráficos de um host ou template.
- **Quando usar:** Para diagnosticar regras LLD que criam dinamicamente interfaces de rede, sistemas de arquivos ou containers.
- **Exemplo Prático / Cenário:** Inspecionar a regra LLD 'Network interface discovery' no hostid '10084'.

**Parâmetros de Entrada:**
- `hostid` (*Optional*, Opcional)

---

### 084. `zabbix_listar_proxies`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista todos os proxies de monitoramento distribuído cadastrados no Zabbix, indicando se operam em modo Ativo ou Passivo e seus respectivos status.
- **Quando usar:** Para verificar a topologia de monitoramento em filiais, clientes externos ou zonas desmilitarizadas (DMZ).
- **Exemplo Prático / Cenário:** Listar todos os Zabbix Proxies e confirmar quais filiais possuem coletores ativos.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 085. `zabbix_consultar_proxy`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Inspeciona detalhadamente o estado operacional de um proxy: última comunicação (lastaccess), lista de hosts atribuídos e endereço de conexão.
- **Quando usar:** Para diagnosticar atrasos de coleta ou perda de comunicação com coletores remotos.
- **Exemplo Prático / Cenário:** Verificar se o proxy da filial 'proxy-filial-rj' está se comunicando normalmente ou com atraso de sincronização.

**Parâmetros de Entrada:**
- `proxyid` (*str*, **Obrigatório**)

---

### 086. `zabbix_gerenciar_proxies`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Administrativo (Exige Aprovação HMAC para exclusão)`
- **Para que serve:** Cadastra, atualiza ou remove configurações de proxies no Zabbix Server.
- **Quando usar:** Ao instalar um novo proxy em uma nova filial ou atualizar o IP de conexão de um coletor.
- **Exemplo Prático / Cenário:** Cadastrar o proxy 'proxy-datacenter-02' em modo Ativo.

**Parâmetros de Entrada:**
- `acao` (*str*, **Obrigatório**)
- `nome` (*Optional*, Opcional)
- `proxyid` (*Optional*, Opcional)
- `operating_mode` (*int*, Opcional, Padrão: `0`)
- `token_aprovacao` (*Optional*, Opcional)

---

### 087. `zabbix_consultar_usuarios`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Lista os usuários cadastrados no Zabbix com seus respectivos grupos e funções de acesso, com redação automática e mascaramento estrito de senhas ou tokens.
- **Quando usar:** Para auditorias de acesso, controle de contas ativas e conformidade de segurança da informação.
- **Exemplo Prático / Cenário:** Listar os usuários com privilégio de Super Administrador no Zabbix.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 088. `zabbix_consultar_funcoes_usuario`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta os papéis de acesso (User Roles) e conjuntos de permissões configurados no Zabbix (Admin, Super Admin, User).
- **Quando usar:** Para verificar quais módulos e permissões de API cada perfil de usuário possui.
- **Exemplo Prático / Cenário:** Auditar as permissões concedidas ao perfil 'NOC Read-Only'.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 089. `zabbix_consultar_auditoria`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta os logs de auditoria nativos do Zabbix (Audit Log), registrando quem alterou, criou ou excluiu qualquer objeto no ambiente com IP de origem e timestamp.
- **Quando usar:** Para perícias forenses, investigação de alterações indevidas e rastreamento de mudanças administrativas.
- **Exemplo Prático / Cenário:** Consultar quem excluiu o host 'srv-legado' nos registros de auditoria das últimas 48 horas.

**Parâmetros de Entrada:**
- `limite` (*int*, Opcional, Padrão: `50`)

---

### 090. `zabbix_consultar_estado_sistema`

- **Categoria:** Categoria 9 — Descoberta Nativa, Proxies e Administração
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Recupera a versão da API do Zabbix, nós do cluster de Alta Disponibilidade (HA nodes se habilitado), tamanho da fila de itens atrasados e integridade geral do servidor.
- **Quando usar:** Para monitorar o próprio Zabbix Server (monitoramento do monitorador) e garantir que a infraestrutura central está saudável.
- **Exemplo Prático / Cenário:** Verificar a versão do Zabbix, nó HA ativo e o volume de itens na fila de espera.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---


## Categoria 10 — Automação, Análise e Diagnóstico Holístico

| # | Ferramenta | Permissão | Para que serve (Resumo) |
|---|---|---|---|
| 91 | [`zabbix_validar_conexao`](#091-zabbix-validar-conexao) | `Somente Leitura` | Testa de ponta a ponta a comunicação com a API JSON-RPC do Zabbix: valida resolução de URL, certificado SSL/TLS, conectividade HTTP, autenticação via Token/Bearer e versão suportada. |
| 92 | [`zabbix_converter_pergunta_para_consulta`](#092-zabbix-converter-pergunta-para-consulta) | `Somente Leitura` | Traduz uma necessidade expressa em linguagem natural (ex: 'Quais servidores Linux tiveram consumo de CPU acima de 90% ontem?') em um plano estruturado de chamadas da API do Zabbix. |
| 93 | [`zabbix_explicar_metricas`](#093-zabbix-explicar-metricas) | `Somente Leitura` | Analisa estatisticamente a série temporal de um item e gera uma explicação compreensível em linguagem natural: média, volatilidade, desvio padrão, tendência de subida ou descida e limites de segurança. |
| 94 | [`zabbix_comparar_periodos`](#094-zabbix-comparar-periodos) | `Somente Leitura` | Compara matematicamente o comportamento de uma métrica em dois períodos temporais distintos (ex: hoje vs mesmo dia da semana passada; este mês vs mês anterior), calculando variação percentual. |
| 95 | [`zabbix_detectar_anomalias`](#095-zabbix-detectar-anomalias) | `Somente Leitura` | Aplica modelos estatísticos de Z-Score sobre os dados históricos da métrica para identificar valores atípicos (outliers) que fogem do comportamento padrão do host. |
| 96 | [`zabbix_planejar_automacao`](#096-zabbix-planejar-automacao) | `Somente Leitura` | Gera um plano de execução completo passo a passo para automações complexas (onboarding, migração de templates, expurgo de hosts), detalhando pré-requisitos, validações e plano de rollback. |
| 97 | [`zabbix_executar_fluxo_aprovado`](#097-zabbix-executar-fluxo-aprovado) | `Operacional` | Executa sequencialmente um plano de automação previamente validado e autorizado, com checagem estrita de pré-condições em cada estágio e interrupção segura em caso de imprevisto. |
| 98 | [`zabbix_previsualizar_alteracao`](#098-zabbix-previsualizar-alteracao) | `Somente Leitura` | Gera uma visualização em formato de Diff (Antes vs Depois) de qualquer alteração proposta em hosts, templates, triggers ou itens, destacando claramente impactos esperados. |
| 99 | [`zabbix_consultar_auditoria_mcp`](#099-zabbix-consultar-auditoria-mcp) | `Somente Leitura` | Consulta o arquivo local de auditoria (`audit_mcp. |
| 100 | [`zabbix_diagnosticar_ambiente`](#100-zabbix-diagnosticar-ambiente) | `Somente Leitura` | Produz um diagnóstico holístico 360° do ecossistema Zabbix: valida conectividade da API, saúde da fila de coleta, integridade dos proxies, proporção de problemas críticos e hosts desprotegidos. |


### 091. `zabbix_validar_conexao`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Testa de ponta a ponta a comunicação com a API JSON-RPC do Zabbix: valida resolução de URL, certificado SSL/TLS, conectividade HTTP, autenticação via Token/Bearer e versão suportada.
- **Quando usar:** Logo na inicialização do servidor MCP ou ao trocar credenciais para certificar que o Zabbix está respondendo perfeitamente.
- **Exemplo Prático / Cenário:** Testar a conectividade com 'http://192.168.0.107:8080/api_jsonrpc.php' e validar o token de acesso.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---

### 092. `zabbix_converter_pergunta_para_consulta`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Traduz uma necessidade expressa em linguagem natural (ex: 'Quais servidores Linux tiveram consumo de CPU acima de 90% ontem?') em um plano estruturado de chamadas da API do Zabbix.
- **Quando usar:** Como assistente de planejamento para agentes de IA estruturarem sequências otimizadas de consultas sem tentativas cegas.
- **Exemplo Prático / Cenário:** Converter a pergunta 'Quais hosts estão com disco crítico?' nos métodos `host.get` e `problem.get` correspondentes.

**Parâmetros de Entrada:**
- `pergunta_em_portugues` (*str*, **Obrigatório**)

---

### 093. `zabbix_explicar_metricas`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Analisa estatisticamente a série temporal de um item e gera uma explicação compreensível em linguagem natural: média, volatilidade, desvio padrão, tendência de subida ou descida e limites de segurança.
- **Quando usar:** Para transformar números e gráficos frios em insights claros e acionáveis para relatórios e respostas a gestores.
- **Exemplo Prático / Cenário:** Explicar o comportamento do uso de memória de um nó durante um teste de carga.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)

---

### 094. `zabbix_comparar_periodos`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Compara matematicamente o comportamento de uma métrica em dois períodos temporais distintos (ex: hoje vs mesmo dia da semana passada; este mês vs mês anterior), calculando variação percentual.
- **Quando usar:** Para validar o impacto de novas versões de software ou comparar a infraestrutura antes e depois de uma migração.
- **Exemplo Prático / Cenário:** Comparar o tráfego de rede da Black Friday deste ano com o tráfego da Black Friday do ano anterior.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `periodo_1_inicio` (*int*, **Obrigatório**)
- `periodo_1_fim` (*int*, **Obrigatório**)
- `periodo_2_inicio` (*int*, **Obrigatório**)
- `periodo_2_fim` (*int*, **Obrigatório**)

---

### 095. `zabbix_detectar_anomalias`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Aplica modelos estatísticos de Z-Score sobre os dados históricos da métrica para identificar valores atípicos (outliers) que fogem do comportamento padrão do host.
- **Quando usar:** Para detecção proativa de anomalias operacionais antes que elas atinjam os limiares rígidos de disparo de triggers.
- **Exemplo Prático / Cenário:** Detectar um pico anômalo de conexões concorrentes no banco de dados fora do horário comercial.

**Parâmetros de Entrada:**
- `itemid` (*str*, **Obrigatório**)
- `limite_amostras` (*int*, Opcional, Padrão: `100`)
- `desvios_padrao` (*float*, Opcional, Padrão: `2.5`)

---

### 096. `zabbix_planejar_automacao`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Gera um plano de execução completo passo a passo para automações complexas (onboarding, migração de templates, expurgo de hosts), detalhando pré-requisitos, validações e plano de rollback.
- **Quando usar:** Antes de iniciar grandes mudanças automatizadas para obter alinhamento e autorização formal da equipe de infraestrutura.
- **Exemplo Prático / Cenário:** Planejar o fluxo de migração de 100 servidores do agente Zabbix legada para o novo Zabbix Agent 2.

**Parâmetros de Entrada:**
- `descricao_objetivo` (*str*, **Obrigatório**)
- `etapas_propostas` (*List*, **Obrigatório**)

---

### 097. `zabbix_executar_fluxo_aprovado`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Operacional`
- **Para que serve:** Executa sequencialmente um plano de automação previamente validado e autorizado, com checagem estrita de pré-condições em cada estágio e interrupção segura em caso de imprevisto.
- **Quando usar:** Para orquestrar fluxos compostos (descoberta -> identificação -> criação -> vinculação -> checagem de telemetria) de forma autônoma e segura.
- **Exemplo Prático / Cenário:** Disparar a execução do plano aprovado de onboarding da filial Rio de Janeiro.

**Parâmetros de Entrada:**
- `plano` (*Dict*, **Obrigatório**)
- `token_aprovacao` (*str*, **Obrigatório**)

---

### 098. `zabbix_previsualizar_alteracao`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Gera uma visualização em formato de Diff (Antes vs Depois) de qualquer alteração proposta em hosts, templates, triggers ou itens, destacando claramente impactos esperados.
- **Quando usar:** Como barreira preventiva de segurança para evitar mudanças incorretas no ambiente de monitoramento.
- **Exemplo Prático / Cenário:** Visualizar as diferenças de configuração antes de alterar a expressão de uma trigger crítica de produção.

**Parâmetros de Entrada:**
- `objeto_tipo` (*str*, **Obrigatório**)
- `acao` (*str*, **Obrigatório**)
- `parametros` (*Dict*, **Obrigatório**)

---

### 099. `zabbix_consultar_auditoria_mcp`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Consulta o arquivo local de auditoria (`audit_mcp.jsonl`) mantido pelo servidor MCP, registrando todas as ferramentas invocadas por agentes de IA, parâmetros recebidos, duração e sucesso.
- **Quando usar:** Para auditoria de segurança das operações executadas pelo próprio servidor MCP e acompanhamento de conformidade DevSecOps.
- **Exemplo Prático / Cenário:** Verificar todas as ferramentas invocadas nas últimas 24 horas e quem solicitou operações com aprovação HMAC.

**Parâmetros de Entrada:**
- `limite` (*int*, Opcional, Padrão: `50`)
- `apenas_erros` (*bool*, Opcional, Padrão: `False`)

---

### 100. `zabbix_diagnosticar_ambiente`

- **Categoria:** Categoria 10 — Automação, Análise e Diagnóstico Holístico
- **Nível de Permissão:** `Somente Leitura`
- **Para que serve:** Produz um diagnóstico holístico 360° do ecossistema Zabbix: valida conectividade da API, saúde da fila de coleta, integridade dos proxies, proporção de problemas críticos e hosts desprotegidos.
- **Quando usar:** Para um check-up geral e confiável do estado da observabilidade da empresa.
- **Exemplo Prático / Cenário:** Executar um diagnóstico 360° para gerar um panorama consolidado de integridade da infraestrutura de monitoramento.

**Parâmetros de Entrada:**
- *Nenhum parâmetro obrigatório ou opcional requerido.*

---
