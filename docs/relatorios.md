# Guia de Relatórios Profissionais

O Zabbix MCP Server possui um motor de relatórios nativo e desacoplado capaz de emitir documentos técnicos e executivos nos formatos **PDF**, **XLSX (Excel)**, **CSV**, **JSON** e **Markdown**.

## Tipos de Relatórios Disponíveis

1. **Relatório Executivo (`zabbix_gerar_relatorio_executivo`):**
   - Resumo consolidado para gerência e diretoria.
   - Total de dispositivos, percentual de cobertura, volumetria de problemas por severidade e disponibilidade global observada.
2. **Relatório de Disponibilidade (`zabbix_gerar_relatorio_disponibilidade`):**
   - Análise detalhada de uptime/downtime de hosts e serviços no período selecionado (7, 15 ou 30 dias).
3. **Relatório de Problemas e Alertas (`zabbix_gerar_relatorio_problemas`):**
   - Distribuição de eventos por severidade (Não classificado, Informação, Aviso, Média, Alta e Desastre).
4. **Relatório de Desempenho e Capacidade (`zabbix_gerar_relatorio_desempenho` / `capacidade`):**
   - Análise de CPU, Memória, Volumes de Disco e Interfaces de Rede.
5. **Relatório de SLA de Serviços (`zabbix_gerar_relatorio_sla`):**
   - Aferição de cumprimento de metas de SLA e Service Level Indicators (SLI).

## Formatos de Exportação

### 1. Documento PDF Corporativo (`zabbix_exportar_relatorio_pdf`)
- Utiliza a biblioteca `reportlab` (100% Python, sem dependências de binários nativos no Windows ou Linux).
- Layout profissional contendo:
  - Cabeçalho institucional e data de emissão.
  - Tabela formatada de indicadores chave de desempenho (KPIs).
  - Tabelas de distribuição de incidentes e amostragem de ativos.
  - Conclusões técnicas e limitações metodológicas.

### 2. Planilha Excel Multi-Abas (`zabbix_exportar_relatorio_excel`)
- Utiliza `openpyxl` com formatação visual (cores institucionais, fontes em negrito, bordas e larguras de colunas autoajustáveis).
- Aba 1: Resumo Executivo e KPIs.
- Abas subsequentes: Detalhamento de problemas e inventário de hosts.

### 3. CSV e JSON Estruturado
- Ideal para ingestão em pipelines de dados, Data Lakes, Grafana ou análise via scripts Python/Pandas.
