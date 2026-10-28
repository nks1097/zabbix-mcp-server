# Catálogo Oficial das 100 Ferramentas MCP do Zabbix

Todas as 100 ferramentas possuem nomes estáveis em `snake_case`, validação com Pydantic, respostas estruturadas em `ToolResult` e controle de permissões.

## Categoria 1 — Descoberta Automática de Dispositivos (1 a 10)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 1 | `zabbix_descobrir_rede` | Operacional | Descobrir dispositivos em uma faixa de rede explicitamente autorizada. |
| 2 | `zabbix_analisar_dispositivo` | Somente Leitura | Analisar endereço IP, DNS, portas permitidas e evidências de identificação. |
| 3 | `zabbix_identificar_sistema_operacional` | Somente Leitura | Inferir o sistema operacional a partir de dados confiáveis e grau de confiança. |
| 4 | `zabbix_identificar_servicos` | Somente Leitura | Identificar serviços monitoráveis usando métodos autorizados e não intrusivos. |
| 5 | `zabbix_deduplicar_dispositivos` | Somente Leitura | Identificar possíveis duplicidades entre dispositivos descobertos e hosts existentes. |
| 6 | `zabbix_comparar_dispositivos_cadastrados` | Somente Leitura | Comparar a descoberta com o inventário atual do Zabbix. |
| 7 | `zabbix_recomendar_templates` | Somente Leitura | Recomendar templates conforme sistema operacional, serviços e compatibilidade. |
| 8 | `zabbix_previsualizar_cadastro` | Somente Leitura | Apresentar todos os parâmetros propostos para cadastrar um dispositivo sem efetuar alterações. |
| 9 | `zabbix_cadastrar_dispositivos_em_lote` | Operacional | Cadastrar vários dispositivos aprovados, com validação individual e relatório de resultados. |
| 10 | `zabbix_verificar_descoberta` | Somente Leitura | Verificar o resultado da descoberta, identificando falhas, duplicidades e pendências. |

## Categoria 2 — Hosts e Interfaces (11 a 20)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 11 | `zabbix_listar_hosts` | Somente Leitura | Listar hosts com filtros por nome, grupo, status e disponibilidade. |
| 12 | `zabbix_consultar_host` | Somente Leitura | Consultar detalhes completos e configurações de um host. |
| 13 | `zabbix_criar_host` | Operacional | Criar um host com parâmetros validados, interfaces e grupos. |
| 14 | `zabbix_atualizar_host` | Operacional | Atualizar propriedades permitidas de um host. |
| 15 | `zabbix_remover_host` | Administrativo (Aprovação) | Remover um host somente após validação e confirmação explícita. |
| 16 | `zabbix_ativar_desativar_host` | Operacional | Alterar o status de monitoramento (0=monitorado, 1=desativado). |
| 17 | `zabbix_gerenciar_interfaces_host` | Operacional | Criar, consultar e atualizar interfaces suportadas (Agente, SNMP, IPMI, JMX). |
| 18 | `zabbix_associar_templates_host` | Operacional | Associar templates compatíveis ao host mantendo os existentes. |
| 19 | `zabbix_desassociar_templates_host` | Operacional | Remover associações de templates com opção de limpeza de itens herdados. |
| 20 | `zabbix_consultar_disponibilidade_host` | Somente Leitura | Consultar a disponibilidade e o estado observável das interfaces do host. |

## Categoria 3 — Coleta de Dados e Métricas (21 a 30)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 21 | `zabbix_listar_itens` | Somente Leitura | Listar itens de coleta com filtros por host, chave, tipo e status. |
| 22 | `zabbix_consultar_item` | Somente Leitura | Consultar configuração e metadados de um item específico. |
| 23 | `zabbix_criar_item` | Operacional | Criar itens de coleta customizados quando suportado e autorizado. |
| 24 | `zabbix_atualizar_item` | Operacional | Atualizar configurações permitidas de um item de coleta. |
| 25 | `zabbix_consultar_historico` | Somente Leitura | Consultar dados históricos de itens (números, strings, logs). |
| 26 | `zabbix_consultar_tendencias` | Somente Leitura | Recuperar tendências (trends) para períodos disponíveis. |
| 27 | `zabbix_ultimos_valores` | Somente Leitura | Consultar os últimos valores recebidos dos itens do host. |
| 28 | `zabbix_verificar_coleta` | Somente Leitura | Verificar se os itens ativos estão coletando dados dentro dos prazos. |
| 29 | `zabbix_detectar_lacunas_coleta` | Somente Leitura | Identificar lacunas temporais (gaps) na coleta de um item. |
| 30 | `zabbix_diagnosticar_coleta` | Somente Leitura | Correlacionar erros, disponibilidade, intervalos e dados ausentes. |

## Categoria 4 — Problemas, Triggers e Eventos (31 a 40)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 31 | `zabbix_listar_problemas` | Somente Leitura | Listar problemas ativos com filtros de severidade e status. |
| 32 | `zabbix_consultar_problema` | Somente Leitura | Consultar detalhes e tags de um problema específico. |
| 33 | `zabbix_consultar_eventos` | Somente Leitura | Consultar eventos por host, período, severidade ou objeto. |
| 34 | `zabbix_listar_triggers` | Somente Leitura | Listar triggers configuradas e seus status. |
| 35 | `zabbix_consultar_trigger` | Somente Leitura | Consultar expressão, estado e metadados de trigger. |
| 36 | `zabbix_criar_trigger` | Operacional | Criar trigger com validação da expressão e prioridade. |
| 37 | `zabbix_atualizar_trigger` | Operacional | Atualizar propriedades suportadas de uma trigger. |
| 38 | `zabbix_reconhecer_problema` | Operacional | Reconhecer (Acknowledge) um problema com mensagem de auditoria. |
| 39 | `zabbix_obter_historico_problema` | Somente Leitura | Recuperar o histórico completo de eventos e resoluções do problema. |
| 40 | `zabbix_investigar_incidente` | Somente Leitura | Correlacionar problemas, hosts, itens e eventos para produzir investigação fundamentada. |

## Categoria 5 — Relatórios e Geração de Documentos (41 a 50)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 41 | `zabbix_gerar_relatorio_executivo` | Somente Leitura | Gerar resumo executivo consolidado do ambiente de monitoramento. |
| 42 | `zabbix_gerar_relatorio_disponibilidade` | Somente Leitura | Gerar relatório de disponibilidade e uptime de hosts e serviços. |
| 43 | `zabbix_gerar_relatorio_problemas` | Somente Leitura | Consolidar problemas por período, host e severidade. |
| 44 | `zabbix_gerar_relatorio_desempenho` | Somente Leitura | Analisar métricas de CPU, memória, disco e rede quando disponíveis. |
| 45 | `zabbix_gerar_relatorio_inventario` | Somente Leitura | Gerar relatório de inventário e cobertura de monitoramento. |
| 46 | `zabbix_gerar_relatorio_capacidade` | Somente Leitura | Analisar tendências e indicadores de esgotamento de recursos. |
| 47 | `zabbix_gerar_relatorio_sla` | Somente Leitura | Gerar relatório de cumprimento de SLAs configurados. |
| 48 | `zabbix_exportar_relatorio_pdf` | Somente Leitura | Gerar documento PDF corporativo com cabeçalho, tabelas e conclusões. |
| 49 | `zabbix_exportar_relatorio_excel` | Somente Leitura | Gerar planilha XLSX estruturada em abas com formatação profissional. |
| 50 | `zabbix_agendar_relatorio` | Operacional | Criar ou atualizar agendamento de relatório nativo do Zabbix. |

## Categoria 6 — Alertas e Notificações (51 a 60)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 51 | `zabbix_listar_alertas` | Somente Leitura | Consultar histórico de alertas e notificações disparadas. |
| 52 | `zabbix_consultar_acoes` | Somente Leitura | Listar ações de notificação configuradas para eventos. |
| 53 | `zabbix_consultar_historico_notificacoes` | Somente Leitura | Consultar notificações e seus resultados de envio (sucesso ou falha). |
| 54 | `zabbix_listar_canais_notificacao` | Somente Leitura | Listar tipos de mídia cadastrados (Media Types: e-mail, webhook, etc.). |
| 55 | `zabbix_testar_canal_notificacao` | Operacional | Testar envio controlado de um canal mediante confirmação explícita. |
| 56 | `zabbix_gerenciar_acoes` | Operacional | Criar, habilitar, desabilitar ou atualizar ações de notificação. |
| 57 | `zabbix_consultar_regras_escalonamento` | Somente Leitura | Consultar etapas e regras de escalonamento configuradas. |
| 58 | `zabbix_suprimir_notificacoes` | Operacional | Implementar supressão temporária de alertas de problemas. |
| 59 | `zabbix_analisar_falsos_positivos` | Somente Leitura | Identificar padrões suspeitos de triggers oscilantes (flapping). |
| 60 | `zabbix_recomendar_ajustes_alertas` | Somente Leitura | Recomendar alterações técnicas em triggers sem aplicá-las silenciosamente. |

## Categoria 7 — Serviços, Manutenção e Mapas (61 a 70)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 61 | `zabbix_listar_servicos` | Somente Leitura | Listar serviços de negócio disponíveis (Business Services). |
| 62 | `zabbix_consultar_servico` | Somente Leitura | Consultar status, algoritmo de cálculo e dependências de um serviço. |
| 63 | `zabbix_criar_servico` | Operacional | Criar novo serviço de negócio com relações válidas. |
| 64 | `zabbix_atualizar_servico` | Operacional | Atualizar propriedades e regras de um serviço. |
| 65 | `zabbix_consultar_sla_servico` | Somente Leitura | Consultar indicadores de SLA e Service Level Indicators (SLI). |
| 66 | `zabbix_listar_manutencoes` | Somente Leitura | Listar períodos e janelas de manutenção configurados. |
| 67 | `zabbix_criar_manutencao` | Operacional | Criar uma janela de manutenção com período e escopo explícitos. |
| 68 | `zabbix_atualizar_manutencao` | Operacional | Alterar uma janela de manutenção autorizada. |
| 69 | `zabbix_consultar_mapas` | Somente Leitura | Consultar mapas de topologia e elementos visuais configurados. |
| 70 | `zabbix_gerar_mapa_monitoramento` | Somente Leitura | Construir representação visual (Mermaid diagram) de hosts e grupos. |

## Categoria 8 — Inventário, Grupos e Templates (71 a 80)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 71 | `zabbix_consultar_inventario` | Somente Leitura | Consultar inventário de hardware, software e metadados de hosts. |
| 72 | `zabbix_atualizar_inventario` | Operacional | Atualizar campos de inventário permitidos (local, tag, SO, notas). |
| 73 | `zabbix_listar_grupos_hosts` | Somente Leitura | Listar grupos de hosts cadastrados. |
| 74 | `zabbix_gerenciar_grupos_hosts` | Operacional / Admin | Criar, atualizar ou excluir grupos de hosts. |
| 75 | `zabbix_listar_templates` | Somente Leitura | Listar templates disponíveis e suas associações. |
| 76 | `zabbix_consultar_template` | Somente Leitura | Consultar configurações, itens, triggers e macros de um template. |
| 77 | `zabbix_criar_template` | Operacional | Criar novo template no Zabbix. |
| 78 | `zabbix_atualizar_template` | Operacional | Atualizar propriedades e objetos de um template. |
| 79 | `zabbix_gerenciar_grupos_templates` | Operacional | Consultar e gerenciar grupos de templates (templategroups). |
| 80 | `zabbix_auditar_cobertura_templates` | Somente Leitura | Auditar hosts sem templates adequados ou com lacunas de monitoramento. |

## Categoria 9 — Descoberta Nativa, Proxies e Administração (81 a 90)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 81 | `zabbix_listar_regras_descoberta` | Somente Leitura | Listar regras nativas de descoberta de rede (Network Discovery). |
| 82 | `zabbix_gerenciar_regras_descoberta` | Operacional | Habilitar, desabilitar ou atualizar regras nativas de rede. |
| 83 | `zabbix_consultar_descoberta_baixo_nivel` | Somente Leitura | Consultar regras LLD (Low-Level Discovery) e protótipos. |
| 84 | `zabbix_listar_proxies` | Somente Leitura | Listar Zabbix Proxies cadastrados. |
| 85 | `zabbix_consultar_proxy` | Somente Leitura | Consultar detalhes, latência e estado observável de um proxy. |
| 86 | `zabbix_gerenciar_proxies` | Administrativo (Aprovação) | Cadastrar, atualizar ou excluir Zabbix Proxies. |
| 87 | `zabbix_consultar_usuarios` | Somente Leitura | Consultar usuários cadastrados (sem expor senhas/hashes). |
| 88 | `zabbix_consultar_funcoes_usuario` | Somente Leitura | Consultar papéis de usuário (User Roles) e permissões. |
| 89 | `zabbix_consultar_auditoria` | Somente Leitura | Consultar registros nativos de auditoria do Zabbix (Audit Log). |
| 90 | `zabbix_consultar_estado_sistema` | Somente Leitura | Recuperar versão do Zabbix, nós de HA, fila e integridade geral. |

## Categoria 10 — Automação, Análise e Governança (91 a 100)

| # | Ferramenta | Permissão | Descrição |
|---|---|---|---|
| 91 | `zabbix_validar_conexao` | Somente Leitura | Validar URL, conectividade de rede, autenticação e versão da API. |
| 92 | `zabbix_converter_pergunta_para_consulta` | Somente Leitura | Mapear pergunta em linguagem natural para consultas recomendadas. |
| 93 | `zabbix_explicar_metricas` | Somente Leitura | Explicar comportamento e tendências de métricas com dados reais. |
| 94 | `zabbix_comparar_periodos` | Somente Leitura | Comparar o comportamento de uma métrica entre dois períodos equivalentes. |
| 95 | `zabbix_detectar_anomalias` | Somente Leitura | Identificar anomalias estatísticas com desvio padrão e Z-Score. |
| 96 | `zabbix_planejar_automacao` | Somente Leitura | Elaborar plano de execução estruturado com cálculo de token de aprovação. |
| 97 | `zabbix_executar_fluxo_aprovado` | Administrativo (Aprovação) | Executar fluxo de automação previamente validado e aprovado. |
| 98 | `zabbix_previsualizar_alteracao` | Somente Leitura | Apresentar diff e impacto esperado antes de aplicar qualquer alteração. |
| 99 | `zabbix_consultar_auditoria_mcp` | Somente Leitura | Consultar o histórico local de chamadas e comandos das ferramentas MCP. |
| 100 | `zabbix_diagnosticar_ambiente` | Somente Leitura | Produzir diagnóstico holístico 360° da infraestrutura Zabbix. |

