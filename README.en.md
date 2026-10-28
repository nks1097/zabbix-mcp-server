# Zabbix MCP Server Universal

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0%2B%20%2F%202.x-green)](https://modelcontextprotocol.io/)
[![Zabbix](https://img.shields.io/badge/Zabbix-6.0%20%7C%206.4%20%7C%207.0%20LTS%20%7C%207.4-red)](https://www.zabbix.com/)

Production-grade **Model Context Protocol (MCP)** server for **Zabbix Enterprise Monitoring**, featuring **100 tools** (with Portuguese descriptions), automated 6-stage device discovery and onboarding, a professional report engine (PDF, XLSX, CSV, JSON, Markdown), Role-Based Access Control (RBAC), two-phase cryptographic approvals, and multi-version compatibility.

---

## 🚀 Key Capabilities

- **100 Dedicated Tools:** Stable `snake_case` tool names, Pydantic data validation, and structured `ToolResult` outputs covering all Zabbix capabilities.
- **Automated 6-Stage Device Onboarding (Stages A to F):**
  1. *Controlled Discovery:* Scope-authorized CIDR scanning with rate limiting.
  2. *OS Fingerprinting:* OS classification (Linux, Windows, Network Appliances) with confidence scoring.
  3. *Reconciliation & Deduplication:* Matches against current Zabbix interfaces to prevent duplicates.
  4. *Planning & Preview:* Detailed preview with interfaces, host groups, and template linkage before committing.
  5. *Transactional Batch Creation:* Individual host creation with granular failure isolation.
  6. *Post-Onboarding Verification:* Validates interface status, enabled items, and initial metric arrival.
- **Enterprise Reporting Engine:** Direct export to corporate **PDF** documents (ReportLab tables and charts), multi-sheet **Excel (.xlsx)** spreadsheets, **CSV**, **JSON**, and **Markdown**.
- **Enterprise DevSecOps Security:**
  - RBAC modes: `somente_leitura` (default read-only), `operacional` (write/create), and `administrativo` (delete/users).
  - **Two-Phase Confirmation:** Destructive operations (host deletion, trigger purge) require parameter-bound HMAC-SHA256 tokens with a 15-minute TTL.
  - **Automatic Secret Redaction:** API tokens, passwords, and SNMP communities are masked as `[REDACTED]`.
  - **SSRF Prevention:** Blocks loopback subnets (`127.0.0.1`) and scans exceeding 1024 IPs.
  - **Local Immutable Audit Log:** Structured JSON Lines logging for all MCP calls (`audit_mcp.jsonl`).
- **Dynamic Version Compatibility:** Auto-detects Zabbix version via `apiinfo.version`, adapting HTTP headers (`Authorization: Bearer <token>` for Zabbix 7.0+ and body auth for <= 6.4).

---

## 🛠️ Complete 100 Tools Catalog (Purpose & Use Cases)

Below is the categorized reference list of all 100 tools available in the server. For complete parameter specifications and input schemas, see the [Technical Tools Reference](docs/ferramentas.md).


### Categoria 1 — Descoberta Automática de Dispositivos

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 01 | [`zabbix_descobrir_rede`](docs/ferramentas.md#001-zabbix-descobrir-rede) | `Operacional` | Realiza uma varredura controlada e não-intrusiva em faixas de rede CIDR IPv4 explicitamente autorizadas. Utiliza testes rápidos de ICMP e conectividade TCP nas portas essenciais de infraestrutura para descobrir quais nós estão vivos e respondendo. | Utilize na etapa inicial de mapeamento de novos ambientes, expansão de datacenters ou auditorias programadas de inventário de rede. |
| 02 | [`zabbix_analisar_dispositivo`](docs/ferramentas.md#002-zabbix-analisar-dispositivo) | `Somente Leitura` | Analisa detalhadamente um endereço IP específico, coletando latência, hostname reverso via DNS (PTR), portas abertas fundamentais (22/SSH, 80/HTTP, 443/HTTPS, 161/SNMP, 10050/Agent, 3389/RDP, 445/SMB) e evidências preliminares de identificação. | Logo após a descoberta de um IP vivo, antes de iniciar o cadastro, para entender a natureza técnica do ativo. |
| 03 | [`zabbix_identificar_sistema_operacional`](docs/ferramentas.md#003-zabbix-identificar-sistema-operacional) | `Somente Leitura` | Infere o sistema operacional provável (Linux, Windows Server, Appliance de Rede, Servidor Web) a partir de assinaturas de portas e comportamento de rede, retornando o nome do SO e um percentual de confiança. | Para selecionar automaticamente a família correta de templates de monitoramento (ex: Linux by Zabbix agent vs Windows by Zabbix agent). |
| 04 | [`zabbix_identificar_servicos`](docs/ferramentas.md#004-zabbix-identificar-servicos) | `Somente Leitura` | Mapeia serviços monitoráveis em execução no host (servidores HTTP/Nginx/Apache, bancos de dados MySQL/PostgreSQL, SSH, Docker, SNMP) através de sondagens não-invasivas em portas bem conhecidas. | Para identificar quais templates de aplicação e serviços devem ser associados ao host além do sistema operacional base. |
| 05 | [`zabbix_deduplicar_dispositivos`](docs/ferramentas.md#005-zabbix-deduplicar-dispositivos) | `Somente Leitura` | Verifica se um dispositivo descoberto já se encontra cadastrado no Zabbix Server, comparando endereços IP de interfaces, nomes visíveis, nomes técnicos e resolução DNS. | Imprescindível antes da criação de qualquer host para impedir a duplicação de cadastros e poluição do banco de dados. |
| 06 | [`zabbix_comparar_dispositivos_cadastrados`](docs/ferramentas.md#006-zabbix-comparar-dispositivos-cadastrados) | `Somente Leitura` | Cruza uma lista de IPs descobertos com todos os hosts atualmente cadastrados no Zabbix, gerando um balanço categorizado: novos nós a cadastrar, nós já monitorados e possíveis divergências de configuração. | Em auditorias periódicas para identificar 'máquinas fantasmas' operando na rede sem monitoramento corporativo. |
| 07 | [`zabbix_recomendar_templates`](docs/ferramentas.md#007-zabbix-recomendar-templates) | `Somente Leitura` | Cruza o sistema operacional e serviços detectados com o acervo de templates instalados no Zabbix, recomendando os templates oficiais mais indicados com seus respectivos IDs. | Para automatizar a etapa de vinculação de templates (linking) sem necessidade de pesquisa manual pelo operador. |
| 08 | [`zabbix_previsualizar_cadastro`](docs/ferramentas.md#008-zabbix-previsualizar-cadastro) | `Somente Leitura` | Simula a criação do host no Zabbix (Dry-Run), apresentando a estrutura JSON exata dos parâmetros: nome técnico, nome visível, interfaces, grupos, templates vinculados e macros, sem gravar alterações. | Para aprovação visual humana ou validação por agentes de IA antes de aplicar a gravação no ambiente de produção. |
| 09 | [`zabbix_cadastrar_dispositivos_em_lote`](docs/ferramentas.md#009-zabbix-cadastrar-dispositivos-em-lote) | `Operacional` | Cria múltiplos hosts aprovados no Zabbix de forma transacional e segura. Processa item por item registrando sucessos e capturando eventuais erros individuais sem interromper a fila. | Na etapa final de onboarding de lotes de equipamentos após a conclusão e aprovação da descoberta de rede. |
| 10 | [`zabbix_verificar_descoberta`](docs/ferramentas.md#010-zabbix-verificar-descoberta) | `Somente Leitura` | Audita o estado pós-implantação dos hosts criados: confirma se a interface está ativa, se os templates foram herdados, se os itens estão criados e se os primeiros dados de telemetria já chegaram. | Logo após o cadastro em lote (Estágio F) para atestar a conformidade da nova instalação e emitir o checklist de entrega. |

### Categoria 2 — Hosts e Interfaces

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 11 | [`zabbix_listar_hosts`](docs/ferramentas.md#011-zabbix-listar-hosts) | `Somente Leitura` | Lista os hosts monitorados no Zabbix aplicando filtros flexíveis por nome, grupo de hosts, status de monitoramento (habilitado/desabilitado) e estado de disponibilidade de interface. | Para pesquisar servidores, listar ativos de um grupo específico ou obter um panorama de inventário. |
| 12 | [`zabbix_consultar_host`](docs/ferramentas.md#012-zabbix-consultar-host) | `Somente Leitura` | Retorna o registro completo e detalhado de um host específico no Zabbix, incluindo interfaces de rede, grupos vinculados, templates herdados, macros, status e metadados de inventário. | Quando for necessário diagnosticar a configuração técnica profunda de um servidor ou equipamento. |
| 13 | [`zabbix_criar_host`](docs/ferramentas.md#013-zabbix-criar-host) | `Operacional` | Cria um novo host no Zabbix com parâmetros estritamente validados: nome técnico, nome visível, endereço IP ou DNS, porta, tipo de interface (Agent, SNMP, IPMI, JMX), grupos e templates. | Para cadastrar individualmente um servidor, roteador, switch ou máquina virtual no Zabbix. |
| 14 | [`zabbix_atualizar_host`](docs/ferramentas.md#014-zabbix-atualizar-host) | `Operacional` | Atualiza propriedades permitidas de um host existente, como nome visível, descrição, status de monitoramento, grupos associados e macros. | Para atualizar descrições operacionais, renomear hosts ou reclassificar grupos sem recriar o ativo. |
| 15 | [`zabbix_remover_host`](docs/ferramentas.md#015-zabbix-remover-host) | `Administrativo (Exige Aprovação HMAC)` | Exclui permanentemente um host do Zabbix juntamente com todo o seu histórico de dados e configurações. Operação destrutiva protegida por token criptográfico de aprovação em dois passos. | Para desativar e expurgar definitivamente da base de monitoramento servidores descomissionados. |
| 16 | [`zabbix_ativar_desativar_host`](docs/ferramentas.md#016-zabbix-ativar-desativar-host) | `Operacional` | Altera o status operacional de monitoramento de um host entre 0 (Monitorado/Ativo) e 1 (Não monitorado/Desativado), pausando temporariamente todas as checagens e alertas. | Durante manutenções emergenciais ou paradas prolongadas de servidores onde não se deseja disparar falsos alarmes. |
| 17 | [`zabbix_gerenciar_interfaces_host`](docs/ferramentas.md#017-zabbix-gerenciar-interfaces-host) | `Operacional` | Cria, consulta e atualiza interfaces de comunicação de um host (Zabbix Agent, SNMP v1/v2c/v3, IPMI, JMX), definindo porta, IP, DNS e interface primária. | Ao adicionar uma interface SNMP secundária em um servidor ou alterar o IP de gerenciamento de um equipamento. |
| 18 | [`zabbix_associar_templates_host`](docs/ferramentas.md#018-zabbix-associar-templates-host) | `Operacional` | Vincula um ou mais templates a um host existente no Zabbix preservando intactos todos os templates que já estavam previamente vinculados. | Para adicionar monitoramento complementar em um host (ex: adicionar template de Docker ou MySQL em um servidor já monitorado por Linux). |
| 19 | [`zabbix_desassociar_templates_host`](docs/ferramentas.md#019-zabbix-desassociar-templates-host) | `Operacional` | Remove a associação de templates de um host, oferecendo a opção de limpeza (unlink_and_clear) para remover do host os itens e gráficos herdados daquele template. | Ao remover um serviço obsoleto de um servidor ou trocar a estratégia de templates de monitoramento. |
| 20 | [`zabbix_consultar_disponibilidade_host`](docs/ferramentas.md#020-zabbix-consultar-disponibilidade-host) | `Somente Leitura` | Inspeciona o estado operacional das interfaces de comunicação do host (Agent, SNMP, IPMI, JMX): se estão disponíveis (1), indisponíveis com erro (2) ou desconhecidas (0), exibindo mensagens de erro de polling se houver. | Para verificar rapidamente se o Zabbix Server consegue conversar com o agente ou SNMP do host monitorado. |

### Categoria 3 — Coleta de Dados e Métricas

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 21 | [`zabbix_listar_itens`](docs/ferramentas.md#021-zabbix-listar-itens) | `Somente Leitura` | Lista os itens de telemetria cadastrados no Zabbix com filtros por host, chave de item (ex: system.cpu.util), tipo de checagem e status de coleta. | Para encontrar métricas específicas de um host ou auditar quais dados estão sendo coletados. |
| 22 | [`zabbix_consultar_item`](docs/ferramentas.md#022-zabbix-consultar-item) | `Somente Leitura` | Recupera a configuração completa de um item específico: chave, intervalo de atualização, período de retenção de histórico/trends, tipo de valor, pré-processamento e estado de erro. | Para inspecionar por que determinado item não está coletando ou conferir seu intervalo de polling. |
| 23 | [`zabbix_criar_item`](docs/ferramentas.md#023-zabbix-criar-item) | `Operacional` | Cria um novo item de coleta customizado em um host com chave, tipo de informação, intervalo de atualização e parâmetros validados. | Para adicionar métricas sob demanda que não façam parte de templates padrão (ex: checagem de script customizado ou UserParameter). |
| 24 | [`zabbix_atualizar_item`](docs/ferramentas.md#024-zabbix-atualizar-item) | `Operacional` | Modifica parâmetros permitidos de um item de coleta, como intervalo de atualização (delay), período de histórico, status (habilitado/desabilitado) e descrição. | Para diminuir a frequência de coleta de um item muito pesado ou reativar um item suspenso. |
| 25 | [`zabbix_consultar_historico`](docs/ferramentas.md#025-zabbix-consultar-historico) | `Somente Leitura` | Recupera os registros históricos pontuais de valores de um ou mais itens em uma janela temporal (numéricos float, inteiros, strings ou logs), com ordenação cronológica. | Para traçar gráficos, analisar comportamento de métricas em um incidente recente ou alimentar modelos de análise. |
| 26 | [`zabbix_consultar_tendencias`](docs/ferramentas.md#026-zabbix-consultar-tendencias) | `Somente Leitura` | Recupera dados consolidados por hora de tendências estatísticas (trends: valor mínimo, médio e máximo) calculados pelo Zabbix para longos períodos de tempo. | Para estudos de capacidade (capacity planning), relatórios mensais e análises de longo prazo (semanas/meses). |
| 27 | [`zabbix_ultimos_valores`](docs/ferramentas.md#027-zabbix-ultimos-valores) | `Somente Leitura` | Consulta a última leitura válida recebida (lastvalue), horário da última coleta e unidade de medida de todos os itens ou de itens filtrados de um host. | Para obter a 'fotografia atual' de telemetria de um host (CPU atual, RAM livre, uptime atual) em tempo real. |
| 28 | [`zabbix_verificar_coleta`](docs/ferramentas.md#028-zabbix-verificar-coleta) | `Somente Leitura` | Analisa se os itens habilitados estão realmente recebendo dados dentro do intervalo esperado (delay), identificando itens atrasados ou com erros de polling. | Para auditar a saúde da ingestão de métricas e diagnosticar se algum agente travou ou perdeu comunicação. |
| 29 | [`zabbix_detectar_lacunas_coleta`](docs/ferramentas.md#029-zabbix-detectar-lacunas-coleta) | `Somente Leitura` | Examina o histórico de um item e detecta 'buracos' ou lacunas temporais (gaps) onde dados deveriam ter sido coletados mas não foram, calculando a duração de cada falha. | Para investigar instabilidades intermitentes de rede ou paradas não registradas de serviços. |
| 30 | [`zabbix_diagnosticar_coleta`](docs/ferramentas.md#030-zabbix-diagnosticar-coleta) | `Somente Leitura` | Produz um diagnóstico inteligente correlacionando erros de itens não suportados (unsupported items), indisponibilidade de interface e atrasos na fila de coleta do host. | Para troubleshooting rápido quando um host recém-cadastrado não começa a plotar gráficos ou apresenta itens em estado vermelho. |

### Categoria 4 — Problemas, Triggers e Eventos

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 31 | [`zabbix_listar_problemas`](docs/ferramentas.md#031-zabbix-listar-problemas) | `Somente Leitura` | Lista incidentes e problemas ativos no ambiente com suporte a filtros por severidade (Informational até Disaster), host, grupo, status de reconhecimento e tags. | Para operadores de NOC e equipes de SRE monitorarem a fila de alarmes ativos no ambiente. |
| 32 | [`zabbix_consultar_problema`](docs/ferramentas.md#032-zabbix-consultar-problema) | `Somente Leitura` | Retorna os detalhes analíticos completos de um problema específico: evento gerador, trigger associada, tags, tempo de duração, severidade e mensagens de reconhecimento. | Para aprofundar a investigação sobre um alarme específico disparado no painel. |
| 33 | [`zabbix_consultar_eventos`](docs/ferramentas.md#033-zabbix-consultar-eventos) | `Somente Leitura` | Consulta a linha do tempo de eventos de problemas (geração e recuperação) no Zabbix, permitindo filtrar por janela temporal, host e severidade. | Para análise de pós-morte (Post-Mortem), auditorias de indisponibilidade e cálculo de MTTR (Mean Time to Resolve). |
| 34 | [`zabbix_listar_triggers`](docs/ferramentas.md#034-zabbix-listar-triggers) | `Somente Leitura` | Lista as regras de alerta (triggers) configuradas no Zabbix com seus respectivos estados (0=OK, 1=Problem), expressões de gatilho, severidades e status (ativa/inativa). | Para auditar regras de alerta configuradas em um host ou template. |
| 35 | [`zabbix_consultar_trigger`](docs/ferramentas.md#035-zabbix-consultar-trigger) | `Somente Leitura` | Recupera a definição técnica detalhada de uma trigger: expressão matemática exata, expressão de recuperação, prioridade, modo de geração de eventos e dependências. | Para inspecionar a lógica exata de cálculo de um alerta ou verificar dependências entre triggers. |
| 36 | [`zabbix_criar_trigger`](docs/ferramentas.md#036-zabbix-criar-trigger) | `Operacional` | Cria uma nova regra de trigger customizada vinculada a itens de um host com expressão sintaticamente validada e nível de severidade configurável. | Para implementar novos alertas de negócio ou limites específicos de infraestrutura. |
| 37 | [`zabbix_atualizar_trigger`](docs/ferramentas.md#037-zabbix-atualizar-trigger) | `Operacional` | Atualiza propriedades permitidas de uma trigger: expressão, severidade, status de habilitação, descrição e tags de correlação. | Para ajustar limiares de alertas que estejam gerando falso-positivo ou silenciar temporariamente um gatilho. |
| 38 | [`zabbix_reconhecer_problema`](docs/ferramentas.md#038-zabbix-reconhecer-problema) | `Operacional` | Registra o reconhecimento formal (Acknowledge) de um problema ativo no Zabbix, permitindo anexar uma mensagem de justificativa/chamado e opcionalmente alterar a severidade ou fechar o evento. | Para que analistas de NOC indiquem que o incidente já está em atendimento pelo time técnico. |
| 39 | [`zabbix_obter_historico_problema`](docs/ferramentas.md#039-zabbix-obter-historico-problema) | `Somente Leitura` | Recupera o histórico completo de ações de um problema: quando iniciou, quem reconheceu, comentários adicionados, escalonamentos de notificação e horário de fechamento. | Para auditoria de atendimento de chamados e conformidade de SLAs operacionais. |
| 40 | [`zabbix_investigar_incidente`](docs/ferramentas.md#040-zabbix-investigar-incidente) | `Somente Leitura` | Executa uma investigação holística de causa raiz para um incidente: correlaciona o problema com as métricas do host no exato momento da falha, eventos concomitantes e alertas relacionados. | Para que um agente de IA ou analista entenda instantaneamente o contexto completo de uma queda ou lentidão severa. |

### Categoria 5 — Relatórios e Exportações

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 41 | [`zabbix_gerar_relatorio_executivo`](docs/ferramentas.md#041-zabbix-gerar-relatorio-executivo) | `Somente Leitura` | Consolida indicadores executivos do ambiente: total de hosts monitorados, distribuição por severidade de problemas ativos, taxa geral de saúde e principais gargalos em formato de alto nível. | Para apresentações a diretorias, reuniões executivas e acompanhamento gerencial diário da infraestrutura. |
| 42 | [`zabbix_gerar_relatorio_disponibilidade`](docs/ferramentas.md#042-zabbix-gerar-relatorio-disponibilidade) | `Somente Leitura` | Calcula a disponibilidade percentual (uptime vs downtime) de hosts e serviços no período selecionado, fundamentado em dados reais de triggers e eventos. | Para comprovação de metas contratuais e relatórios formais de disponibilidade mensal ou semanal. |
| 43 | [`zabbix_gerar_relatorio_problemas`](docs/ferramentas.md#043-zabbix-gerar-relatorio-problemas) | `Somente Leitura` | Agrupa e analisa todos os incidentes ocorridos no período por severidade, tempo médio de duração, hosts mais incidentados (Top Problematic Hosts) e taxa de resolução. | Para análise de tendências de problemas e identificação dos ativos que mais geram instabilidade na operação. |
| 44 | [`zabbix_gerar_relatorio_desempenho`](docs/ferramentas.md#044-zabbix-gerar-relatorio-desempenho) | `Somente Leitura` | Analisa o perfil de consumo de recursos computacionais (CPU, memória RAM, tráfego de rede e espaço em disco) apontando picos, médias e desvios de capacidade. | Para dimensionamento de máquinas virtuais, detecção de gargalos de processamento e auditoria de performance. |
| 45 | [`zabbix_gerar_relatorio_inventario`](docs/ferramentas.md#045-zabbix-gerar-relatorio-inventario) | `Somente Leitura` | Mapeia todo o parque instalado: sistemas operacionais, localizações físicas/virtuais, números de série, versões de software e cobertura de monitoramento por grupo. | Em auditorias de ativos de TI, renovações de contratos e compliance de segurança da informação. |
| 46 | [`zabbix_gerar_relatorio_capacidade`](docs/ferramentas.md#046-zabbix-gerar-relatorio-capacidade) | `Somente Leitura` | Analisa tendências de consumo de armazenamento (disco) e memória para prever dias até a exaustão (Days Until Full / Runway) com base no crescimento histórico. | Para planejamento de expansão de storage, previsão orçamentária e prevenção de paradas por disco cheio. |
| 47 | [`zabbix_gerar_relatorio_sla`](docs/ferramentas.md#047-zabbix-gerar-relatorio-sla) | `Somente Leitura` | Calcula os índices de cumprimento de acordos de nível de serviço (SLA) para serviços de negócio configurados, apontando tempo de conformidade e violações. | Para prestação de contas a clientes internos ou externos sobre serviços críticos (ERP, E-commerce, APIs). |
| 48 | [`zabbix_exportar_relatorio_pdf`](docs/ferramentas.md#048-zabbix-exportar-relatorio-pdf) | `Somente Leitura` | Converte os dados de qualquer relatório estruturado em um documento PDF corporativo profissional, com cabeçalho, tabelas zebradas, sumário executivo e layout limpo. | Quando for necessário enviar um relatório formal por e-mail para diretores, clientes ou equipes de auditoria. |
| 49 | [`zabbix_exportar_relatorio_excel`](docs/ferramentas.md#049-zabbix-exportar-relatorio-excel) | `Somente Leitura` | Gera planilhas nativas em formato Microsoft Excel (.xlsx) com múltiplas abas, cabeçalhos estilizados, filtros e formatação numérica adequada. | Para analistas de dados e engenheiros que precisam manipular, filtrar e cruzar métricas em planilhas. |
| 50 | [`zabbix_agendar_relatorio`](docs/ferramentas.md#050-zabbix-agendar-relatorio) | `Operacional` | Configura agendamentos nativos de relatórios no Zabbix Server (Zabbix 6.0+) definindo periodicidade, destinatários e parâmetros de envio. | Para automatizar a entrega semanal ou mensal de relatórios gerenciais diretamente na caixa de entrada dos gestores. |

### Categoria 6 — Alertas, Ações e Notificações

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 51 | [`zabbix_listar_alertas`](docs/ferramentas.md#051-zabbix-listar-alertas) | `Somente Leitura` | Consulta a fila de alertas gerados pelo Zabbix, permitindo filtrar por destinatário, período, canal de mídia (E-mail, Telegram, Slack) e status de envio (enviado/falhou). | Para auditar se as notificações estão sendo devidamente entregues ou identificar falhas de comunicação com servidores de correio/webhooks. |
| 52 | [`zabbix_consultar_acoes`](docs/ferramentas.md#052-zabbix-consultar-acoes) | `Somente Leitura` | Lista as regras de ações (actions) configuradas no Zabbix para tratamento de triggers, descoberta de rede, autorregistro ou serviços internos. | Para auditar quais regras de automação disparam notificações quando determinados alarmes ocorrem. |
| 53 | [`zabbix_consultar_historico_notificacoes`](docs/ferramentas.md#053-zabbix-consultar-historico-notificacoes) | `Somente Leitura` | Recupera o histórico cronológico de notificações enviadas para um determinado usuário ou host, facilitando a correlação de alertas. | Para investigar por que um plantonista alega não ter recebido notificação de um incidente crítico. |
| 54 | [`zabbix_listar_canais_notificacao`](docs/ferramentas.md#054-zabbix-listar-canais-notificacao) | `Somente Leitura` | Lista os tipos de mídia (media types) configurados no Zabbix Server (SMTP, SMS, Webhooks para Jira/ServiceNow/Teams/Slack, scripts personalizados). | Para verificar quais canais de comunicação estão disponíveis e ativos no ambiente. |
| 55 | [`zabbix_testar_canal_notificacao`](docs/ferramentas.md#055-zabbix-testar-canal-notificacao) | `Operacional` | Dispara um teste controlado de envio através de um tipo de mídia específico para validar a conectividade e integridade das credenciais configuradas. | Ao configurar uma nova integração com Telegram, Discord ou servidor SMTP corporativo. |
| 56 | [`zabbix_gerenciar_acoes`](docs/ferramentas.md#056-zabbix-gerenciar-acoes) | `Operacional` | Habilita, desabilita ou atualiza as propriedades operacionais de uma regra de ação do Zabbix. | Para pausar temporariamente ações de disparo de tickets em massa durante uma janela de manutenção geral. |
| 57 | [`zabbix_consultar_regras_escalonamento`](docs/ferramentas.md#057-zabbix-consultar-regras-escalonamento) | `Somente Leitura` | Consulta a árvore de escalonamento configurada em uma ação (ex: Passo 1: notificar NOC; Passo 2 após 30m: notificar Coordenador; Passo 3 após 1h: notificar Gerente). | Para validar fluxos de escalonamento de incidentes e garantir conformidade com as diretrizes de governança. |
| 58 | [`zabbix_suprimir_notificacoes`](docs/ferramentas.md#058-zabbix-suprimir-notificacoes) | `Operacional` | Aplica supressão temporária manual de notificações para um problema específico ou host, impedindo o envio de novos alertas sem desativar a coleta. | Quando um incidente conhecido já está sendo trabalhado e não se deseja sobrecarregar a caixa postal do time com alertas repetidos. |
| 59 | [`zabbix_analisar_falsos_positivos`](docs/ferramentas.md#059-zabbix-analisar-falsos-positivos) | `Somente Leitura` | Examina o histórico recente de eventos para identificar triggers com comportamento de 'flapping' (oscilação contínua entre Problem e OK em curtos intervalos). | Em rotinas de higiene do monitoramento para erradicar a 'fadiga de alertas' gerada por gatilhos excessivamente sensíveis. |
| 60 | [`zabbix_recomendar_ajustes_alertas`](docs/ferramentas.md#060-zabbix-recomendar-ajustes-alertas) | `Somente Leitura` | Com base no histórico e nas oscilações de métricas, propõe ajustes técnicos fundamentados em triggers (ex: adicionar função min() ou max(), aumentar tempo de avaliação de 1m para 5m). | Para otimizar e calibrar triggers barulhentas sem alterar a infraestrutura sem revisão prévia. |

### Categoria 7 — Serviços de Negócio, Manutenções e Mapas

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 61 | [`zabbix_listar_servicos`](docs/ferramentas.md#061-zabbix-listar-servicos) | `Somente Leitura` | Lista a árvore de Business Services (Serviços de Negócio) configurada no Zabbix, exibindo hierarquia pai-filho e status de saúde consolidado. | Para visões focadas no negócio (ex: 'Sistema ERP', 'Gateway de Pagamentos') em vez de focar apenas no servidor físico isolado. |
| 62 | [`zabbix_consultar_servico`](docs/ferramentas.md#062-zabbix-consultar-servico) | `Somente Leitura` | Retorna os detalhes de um serviço de negócio específico: regras de propagação de status, triggers filhas associadas, pesos e tags de correlação. | Para entender qual componente subjacente está impactando a disponibilidade de um serviço de negócio. |
| 63 | [`zabbix_criar_servico`](docs/ferramentas.md#063-zabbix-criar-servico) | `Operacional` | Cria um novo serviço de negócio no catálogo de serviços do Zabbix, definindo seu algoritmo de cálculo de status (qualquer filho falha, todos falham, etc.) e serviço pai. | Ao modelar a arquitetura de monitoramento de uma nova aplicação corporativa. |
| 64 | [`zabbix_atualizar_servico`](docs/ferramentas.md#064-zabbix-atualizar-servico) | `Operacional` | Atualiza propriedades, regras de avaliação e dependências de um serviço de negócio existente. | Ao adicionar novos microserviços à composição de um serviço corporativo. |
| 65 | [`zabbix_consultar_sla_servico`](docs/ferramentas.md#065-zabbix-consultar-sla-servico) | `Somente Leitura` | Calcula os indicadores SLI (Service Level Indicator) e o cumprimento de metas de SLA para um serviço em períodos específicos (semanal, mensal, anual). | Para avaliar o consumo de Error Budget (Orçamento de Erro) e atestar a qualidade contratual de entrega. |
| 66 | [`zabbix_listar_manutencoes`](docs/ferramentas.md#066-zabbix-listar-manutencoes) | `Somente Leitura` | Lista todas as janelas de manutenção cadastradas no Zabbix (ativas, agendadas ou expiradas) com tipo de manutenção (com ou sem coleta de dados) e hosts afetados. | Para verificar se há janelas de manutenção ativas no ambiente ou consultar agendamentos futuros. |
| 67 | [`zabbix_criar_manutencao`](docs/ferramentas.md#067-zabbix-criar-manutencao) | `Operacional` | Cria uma nova janela de manutenção com horários de início e término estritos, escopo de hosts/grupos e definição se a coleta de dados deve ser mantida ou suspensa. | Antes de iniciar uma atualização de software, troca de hardware ou janela de homologação. |
| 68 | [`zabbix_atualizar_manutencao`](docs/ferramentas.md#068-zabbix-atualizar-manutencao) | `Operacional` | Modifica o período ou a lista de hosts contemplados em uma janela de manutenção já existente. | Para prorrogar uma janela de manutenção cujo procedimento técnico demorou mais que o previsto. |
| 69 | [`zabbix_consultar_mapas`](docs/ferramentas.md#069-zabbix-consultar-mapas) | `Somente Leitura` | Recupera as configurações e nós de mapas de topologia visual cadastrados no Zabbix. | Para inspecionar diagramas de infraestrutura cadastrados pelos administradores do Zabbix. |
| 70 | [`zabbix_gerar_mapa_monitoramento`](docs/ferramentas.md#070-zabbix-gerar-mapa-monitoramento) | `Somente Leitura` | Gera dinamicamente uma representação gráfica de mapa em formato Markdown/Mermaid a partir dos hosts, grupos e status reais consultados na API do Zabbix. | Para visualizar visualmente e instantaneamente a relação entre servidores, banco de dados e switches na documentação ou relatórios. |

### Categoria 8 — Inventário, Grupos e Templates

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 71 | [`zabbix_consultar_inventario`](docs/ferramentas.md#071-zabbix-consultar-inventario) | `Somente Leitura` | Recupera os campos detalhados de inventário de um host (hardware, sistema operacional, localização geográfica, responsável técnico, número de série, vendor, notas). | Para consultar dados cadastrais e patrimoniais vinculados ao servidor monitorado. |
| 72 | [`zabbix_atualizar_inventario`](docs/ferramentas.md#072-zabbix-atualizar-inventario) | `Operacional` | Atualiza campos de inventário permitidos de um host (modo de inventário manual/automático, tags, local físico, notas de suporte, etc.). | Para manter o CMDB atualizado com dados de novos responsáveis, mudanças de rack ou informações de suporte. |
| 73 | [`zabbix_listar_grupos_hosts`](docs/ferramentas.md#073-zabbix-listar-grupos-hosts) | `Somente Leitura` | Lista todos os grupos de hosts (hostgroups) cadastrados no Zabbix com seus respectivos IDs e nomes. | Para pesquisar os grupos existentes antes de criar novos servidores ou associar permissões. |
| 74 | [`zabbix_gerenciar_grupos_hosts`](docs/ferramentas.md#074-zabbix-gerenciar-grupos-hosts) | `Operacional` | Cria, renomeia ou remove grupos de hosts no Zabbix, validando a não-existência de hosts dependentes antes de qualquer exclusão. | Para criar novas estruturas organizacionais (ex: criar grupo 'Cloud AWS / EKS') ou reorganizar a taxonomia da empresa. |
| 75 | [`zabbix_listar_templates`](docs/ferramentas.md#075-zabbix-listar-templates) | `Somente Leitura` | Lista os templates disponíveis no Zabbix, permitindo filtrar por nome ou grupo de templates. | Para descobrir quais templates de sistema operacional, banco de dados ou rede estão instalados e prontos para uso. |
| 76 | [`zabbix_consultar_template`](docs/ferramentas.md#076-zabbix-consultar-template) | `Somente Leitura` | Inspeciona profundamente um template específico: itens, triggers, protótipos de descoberta (LLD), gráficos, dashboards e macros herdadas. | Para analisar o que um template irá monitorar antes de vinculá-lo a servidores de produção. |
| 77 | [`zabbix_criar_template`](docs/ferramentas.md#077-zabbix-criar-template) | `Operacional` | Cria um novo template no Zabbix com parâmetros validados, associando-o ao grupo de templates adequado. | Para iniciar a criação de um template customizado para monitoramento de uma aplicação proprietária. |
| 78 | [`zabbix_atualizar_template`](docs/ferramentas.md#078-zabbix-atualizar-template) | `Operacional` | Atualiza propriedades, nome visível, descrição e macros de um template existente. | Para atualizar a documentação ou padrões de um template compartilhado entre várias equipes. |
| 79 | [`zabbix_gerenciar_grupos_templates`](docs/ferramentas.md#079-zabbix-gerenciar-grupos-templates) | `Operacional` | Gerencia a criação e listagem de grupos de templates, compatível com a separação entre hostgroups e templategroups introduzida a partir do Zabbix 6.2+. | Para organizar o repositório de templates por fabricante, área de negócio ou tecnologia. |
| 80 | [`zabbix_auditar_cobertura_templates`](docs/ferramentas.md#080-zabbix-auditar-cobertura-templates) | `Somente Leitura` | Audita todo o Zabbix em busca de falhas de governança: hosts ativos sem nenhum template vinculado, templates órfãos sem nenhum host e discrepâncias de padronização. | Em auditorias periódicas de qualidade para garantir que nenhum ativo fique desprotegido. |

### Categoria 9 — Descoberta Nativa, Proxies e Administração

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 81 | [`zabbix_listar_regras_descoberta`](docs/ferramentas.md#081-zabbix-listar-regras-descoberta) | `Somente Leitura` | Lista as regras nativas de Descoberta de Rede (Network Discovery Rules - drule) configuradas no Zabbix Server/Proxy. | Para consultar as regras periódicas nativas de varredura de sub-redes configuradas no Zabbix. |
| 82 | [`zabbix_gerenciar_regras_descoberta`](docs/ferramentas.md#082-zabbix-gerenciar-regras-descoberta) | `Operacional` | Habilita, desabilita ou altera propriedades de regras nativas de descoberta de rede (drule). | Para ativar ou pausar a varredura nativa do Zabbix em determinadas sub-redes. |
| 83 | [`zabbix_consultar_descoberta_baixo_nivel`](docs/ferramentas.md#083-zabbix-consultar-descoberta-baixo-nivel) | `Somente Leitura` | Consulta as regras LLD (Low-Level Discovery) e protótipos de itens, triggers e gráficos de um host ou template. | Para diagnosticar regras LLD que criam dinamicamente interfaces de rede, sistemas de arquivos ou containers. |
| 84 | [`zabbix_listar_proxies`](docs/ferramentas.md#084-zabbix-listar-proxies) | `Somente Leitura` | Lista todos os proxies de monitoramento distribuído cadastrados no Zabbix, indicando se operam em modo Ativo ou Passivo e seus respectivos status. | Para verificar a topologia de monitoramento em filiais, clientes externos ou zonas desmilitarizadas (DMZ). |
| 85 | [`zabbix_consultar_proxy`](docs/ferramentas.md#085-zabbix-consultar-proxy) | `Somente Leitura` | Inspeciona detalhadamente o estado operacional de um proxy: última comunicação (lastaccess), lista de hosts atribuídos e endereço de conexão. | Para diagnosticar atrasos de coleta ou perda de comunicação com coletores remotos. |
| 86 | [`zabbix_gerenciar_proxies`](docs/ferramentas.md#086-zabbix-gerenciar-proxies) | `Administrativo (Exige Aprovação HMAC para exclusão)` | Cadastra, atualiza ou remove configurações de proxies no Zabbix Server. | Ao instalar um novo proxy em uma nova filial ou atualizar o IP de conexão de um coletor. |
| 87 | [`zabbix_consultar_usuarios`](docs/ferramentas.md#087-zabbix-consultar-usuarios) | `Somente Leitura` | Lista os usuários cadastrados no Zabbix com seus respectivos grupos e funções de acesso, com redação automática e mascaramento estrito de senhas ou tokens. | Para auditorias de acesso, controle de contas ativas e conformidade de segurança da informação. |
| 88 | [`zabbix_consultar_funcoes_usuario`](docs/ferramentas.md#088-zabbix-consultar-funcoes-usuario) | `Somente Leitura` | Consulta os papéis de acesso (User Roles) e conjuntos de permissões configurados no Zabbix (Admin, Super Admin, User). | Para verificar quais módulos e permissões de API cada perfil de usuário possui. |
| 89 | [`zabbix_consultar_auditoria`](docs/ferramentas.md#089-zabbix-consultar-auditoria) | `Somente Leitura` | Consulta os logs de auditoria nativos do Zabbix (Audit Log), registrando quem alterou, criou ou excluiu qualquer objeto no ambiente com IP de origem e timestamp. | Para perícias forenses, investigação de alterações indevidas e rastreamento de mudanças administrativas. |
| 90 | [`zabbix_consultar_estado_sistema`](docs/ferramentas.md#090-zabbix-consultar-estado-sistema) | `Somente Leitura` | Recupera a versão da API do Zabbix, nós do cluster de Alta Disponibilidade (HA nodes se habilitado), tamanho da fila de itens atrasados e integridade geral do servidor. | Para monitorar o próprio Zabbix Server (monitoramento do monitorador) e garantir que a infraestrutura central está saudável. |

### Categoria 10 — Automação, Análise e Diagnóstico Holístico

| # | Tool | Level | Purpose | When to use |
|---|---|---|---|---|
| 91 | [`zabbix_validar_conexao`](docs/ferramentas.md#091-zabbix-validar-conexao) | `Somente Leitura` | Testa de ponta a ponta a comunicação com a API JSON-RPC do Zabbix: valida resolução de URL, certificado SSL/TLS, conectividade HTTP, autenticação via Token/Bearer e versão suportada. | Logo na inicialização do servidor MCP ou ao trocar credenciais para certificar que o Zabbix está respondendo perfeitamente. |
| 92 | [`zabbix_converter_pergunta_para_consulta`](docs/ferramentas.md#092-zabbix-converter-pergunta-para-consulta) | `Somente Leitura` | Traduz uma necessidade expressa em linguagem natural (ex: 'Quais servidores Linux tiveram consumo de CPU acima de 90% ontem?') em um plano estruturado de chamadas da API do Zabbix. | Como assistente de planejamento para agentes de IA estruturarem sequências otimizadas de consultas sem tentativas cegas. |
| 93 | [`zabbix_explicar_metricas`](docs/ferramentas.md#093-zabbix-explicar-metricas) | `Somente Leitura` | Analisa estatisticamente a série temporal de um item e gera uma explicação compreensível em linguagem natural: média, volatilidade, desvio padrão, tendência de subida ou descida e limites de segurança. | Para transformar números e gráficos frios em insights claros e acionáveis para relatórios e respostas a gestores. |
| 94 | [`zabbix_comparar_periodos`](docs/ferramentas.md#094-zabbix-comparar-periodos) | `Somente Leitura` | Compara matematicamente o comportamento de uma métrica em dois períodos temporais distintos (ex: hoje vs mesmo dia da semana passada; este mês vs mês anterior), calculando variação percentual. | Para validar o impacto de novas versões de software ou comparar a infraestrutura antes e depois de uma migração. |
| 95 | [`zabbix_detectar_anomalias`](docs/ferramentas.md#095-zabbix-detectar-anomalias) | `Somente Leitura` | Aplica modelos estatísticos de Z-Score sobre os dados históricos da métrica para identificar valores atípicos (outliers) que fogem do comportamento padrão do host. | Para detecção proativa de anomalias operacionais antes que elas atinjam os limiares rígidos de disparo de triggers. |
| 96 | [`zabbix_planejar_automacao`](docs/ferramentas.md#096-zabbix-planejar-automacao) | `Somente Leitura` | Gera um plano de execução completo passo a passo para automações complexas (onboarding, migração de templates, expurgo de hosts), detalhando pré-requisitos, validações e plano de rollback. | Antes de iniciar grandes mudanças automatizadas para obter alinhamento e autorização formal da equipe de infraestrutura. |
| 97 | [`zabbix_executar_fluxo_aprovado`](docs/ferramentas.md#097-zabbix-executar-fluxo-aprovado) | `Operacional` | Executa sequencialmente um plano de automação previamente validado e autorizado, com checagem estrita de pré-condições em cada estágio e interrupção segura em caso de imprevisto. | Para orquestrar fluxos compostos (descoberta -> identificação -> criação -> vinculação -> checagem de telemetria) de forma autônoma e segura. |
| 98 | [`zabbix_previsualizar_alteracao`](docs/ferramentas.md#098-zabbix-previsualizar-alteracao) | `Somente Leitura` | Gera uma visualização em formato de Diff (Antes vs Depois) de qualquer alteração proposta em hosts, templates, triggers ou itens, destacando claramente impactos esperados. | Como barreira preventiva de segurança para evitar mudanças incorretas no ambiente de monitoramento. |
| 99 | [`zabbix_consultar_auditoria_mcp`](docs/ferramentas.md#099-zabbix-consultar-auditoria-mcp) | `Somente Leitura` | Consulta o arquivo local de auditoria (`audit_mcp.jsonl`) mantido pelo servidor MCP, registrando todas as ferramentas invocadas por agentes de IA, parâmetros recebidos, duração e sucesso. | Para auditoria de segurança das operações executadas pelo próprio servidor MCP e acompanhamento de conformidade DevSecOps. |
| 100 | [`zabbix_diagnosticar_ambiente`](docs/ferramentas.md#100-zabbix-diagnosticar-ambiente) | `Somente Leitura` | Produz um diagnóstico holístico 360° do ecossistema Zabbix: valida conectividade da API, saúde da fila de coleta, integridade dos proxies, proporção de problemas críticos e hosts desprotegidos. | Para um check-up geral e confiável do estado da observabilidade da empresa. |


---

## 📂 Repository Structure

```text
zabbix-mcp-server/
├── src/zabbix_mcp/
│   ├── server.py              # FastMCP / MCPServer entrypoint (100 registered tools)
│   ├── config.py              # Pydantic Settings & environment validation
│   ├── client.py              # Async httpx client with JSON-RPC 2.0 & retries
│   ├── api_compatibility.py   # Version detection & capability matrix
│   ├── models.py              # Pydantic contracts & ToolResult envelope
│   ├── security.py            # Secret redaction & SSRF prevention
│   ├── authorization.py       # RBAC authorization modes
│   ├── policies.py            # Two-phase HMAC approval tokens
│   ├── audit.py               # Local JSONL audit logger
│   ├── discovery/             # 6-Stage automated onboarding (A through F)
│   ├── reports/               # PDF, Excel, CSV, JSON and MD reporting engine
│   └── tools/                 # 100 tools across 10 modular categories
├── tests/
│   ├── unit/                  # Unit test suite
│   └── integration/           # Integration tests against live Zabbix
├── docs/                      # 9 Comprehensive guides on architecture, tools, security
├── Dockerfile                 # Rootless production container image
├── compose.yaml               # Docker compose configuration with SSE support
└── pyproject.toml             # Project metadata & dependencies
```

---

## 📦 Quick Installation

```bash
git clone https://github.com/nks1097/zabbix-mcp-server.git
cd zabbix-mcp-server

python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\activate

pip install --upgrade pip
pip install -e ".[dev]"
```

### Configuration (`.env`)

```ini
ZABBIX_URL=http://your-zabbix-host:8080/api_jsonrpc.php
ZABBIX_TOKEN=your_token_here
ZABBIX_MCP_MODE=somente_leitura
```

### Running the MCP Server

Via STDIO:
```bash
python -m zabbix_mcp.server --transport stdio
```

Via SSE:
```bash
python -m zabbix_mcp.server --transport sse --port 8000
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
