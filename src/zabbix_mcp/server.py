"""
Ponto de Entrada do Servidor MCP Zabbix (FastMCP / MCPServer).
Registra as 100 ferramentas em português, recursos e prompts especializados.
"""

import argparse
import logging
import sys

try:
    from mcp.server.mcpserver import MCPServer
except (ImportError, ModuleNotFoundError):
    from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore

from .tools import ALL_TOOLS

# Configuração de logging seguro direcionado para stderr (não polui o transporte stdio)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("zabbix_mcp.server")


def create_server() -> MCPServer:
    """Cria e configura a instância do servidor MCP com as 100 ferramentas registradas."""
    server = MCPServer(
        name="zabbix-mcp",
        instructions=(
            "Servidor MCP para gerenciamento inteligente do Zabbix Enterprise Monitoring, "
            "com 100 ferramentas em português para descoberta automática, cadastro de dispositivos, "
            "relatórios executivos, alertas, problemas, serviços, inventário e auditoria."
        ),
        version="1.0.0"
    )

    # 1. Registro automático das 100 ferramentas oficiais
    for tool_func in ALL_TOOLS:
        server.add_tool(tool_func)

    # 2. Registro de Prompts Especializados para Agentes de IA
    @server.prompt(
        name="investigar_incidente",
        description="Guia o agente de IA a investigar a causa raiz de um problema ou alerta ativo no Zabbix."
    )
    def prompt_investigar_incidente(eventid: str) -> str:
        return (
            f"Por favor, execute uma investigação fundamentada sobre o incidente ID '{eventid}'. "
            "Siga as seguintes etapas:\n"
            "1. Consulte os detalhes do incidente com 'zabbix_investigar_incidente'.\n"
            "2. Analise os últimos valores dos itens correlacionados com 'zabbix_ultimos_valores'.\n"
            "3. Verifique se há histórico de oscilação ou alertas recentes no mesmo host.\n"
            "4. Forneça um diagnóstico claro diferenciando correlações diretas de hipóteses inferidas."
        )

    @server.prompt(
        name="cadastrar_dispositivos",
        description="Executa o fluxo completo em 6 estágios para descoberta e cadastro de dispositivos de rede."
    )
    def prompt_cadastrar_dispositivos(faixa_cidr: str) -> str:
        return (
            f"Inicie o fluxo de onboarding automatizado na rede '{faixa_cidr}'.\n"
            "Etapas obrigatórias:\n"
            "1. Descubra os dispositivos ativos com 'zabbix_descobrir_rede' (confirmar_escopo_autorizado=True).\n"
            "2. Deduplique os hosts com 'zabbix_deduplicar_dispositivos' para evitar duplicidades no Zabbix.\n"
            "3. Identifique o sistema operacional e serviços dos dispositivos novos.\n"
            "4. Gere a prévia de cadastro com 'zabbix_previsualizar_cadastro' e apresente ao usuário.\n"
            "5. Após aprovação, execute o cadastro em lote com 'zabbix_cadastrar_dispositivos_em_lote'.\n"
            "6. Verifique os hosts criados com 'zabbix_verificar_descoberta'."
        )

    @server.prompt(
        name="gerar_relatorio_executivo",
        description="Gera um relatório executivo consolidado com disponibilidade, problemas e recomendações."
    )
    def prompt_gerar_relatorio_executivo(periodo_dias: int = 7) -> str:
        return (
            f"Gere um relatório executivo consolidado dos últimos {periodo_dias} dias utilizando a ferramenta "
            "'zabbix_gerar_relatorio_executivo'. Exporte também em PDF ou Excel através de "
            "'zabbix_exportar_relatorio_pdf' ou 'zabbix_exportar_relatorio_excel'."
        )

    @server.prompt(
        name="diagnosticar_falha_coleta",
        description="Diagnostica por que um host ou conjunto de itens parou de receber dados."
    )
    def prompt_diagnosticar_falha(hostid: str) -> str:
        return (
            f"Diagnostique as falhas de coleta no host '{hostid}':\n"
            "1. Verifique a disponibilidade observável e erros com 'zabbix_consultar_disponibilidade_host'.\n"
            "2. Cheque o estado dos itens e falhas recentes com 'zabbix_verificar_coleta'.\n"
            "3. Identifique lacunas temporais com 'zabbix_detectar_lacunas_coleta'.\n"
            "4. Emita um relatório técnico com os achados e ações recomendadas."
        )

    @server.prompt(
        name="analisar_disponibilidade",
        description="Calcula e analisa a disponibilidade de hosts e serviços no ambiente."
    )
    def prompt_analisar_disponibilidade(periodo_dias: int = 30) -> str:
        return (
            f"Analise a disponibilidade geral do parque monitorado nos últimos {periodo_dias} dias.\n"
            "Utilize 'zabbix_gerar_relatorio_disponibilidade' e detalhe os dispositivos com maior tempo de indisponibilidade."
        )

    @server.prompt(
        name="revisar_templates",
        description="Audita a cobertura e adequação dos templates nos hosts cadastrados."
    )
    def prompt_revisar_templates() -> str:
        return (
            "Execute uma auditoria de templates no Zabbix com 'zabbix_auditar_cobertura_templates'. "
            "Identifique hosts sem templates associados ou dependentes apenas de ICMP Ping e sugira templates recomendados."
        )

    @server.prompt(
        name="auditar_ambiente",
        description="Executa uma varredura 360° da saúde e integridade do Zabbix Server e Proxies."
    )
    def prompt_auditar_ambiente() -> str:
        return (
            "Realize uma auditoria completa do ambiente Zabbix:\n"
            "1. Conectividade e versão com 'zabbix_validar_conexao'.\n"
            "2. Estado global com 'zabbix_diagnosticar_ambiente'.\n"
            "3. Saúde dos proxies com 'zabbix_listar_proxies'.\n"
            "4. Triggers em flapping com 'zabbix_analisar_falsos_positivos'."
        )

    return server


def main() -> None:
    """Função principal executada ao iniciar o servidor via CLI."""
    parser = argparse.ArgumentParser(description="Zabbix MCP Server Universal")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transporte MCP (stdio ou sse)")
    parser.add_argument("--host", default="127.0.0.1", help="Host para transporte SSE")
    parser.add_argument("--port", type=int, default=8000, help="Porta para transporte SSE")
    args = parser.parse_args()

    server = create_server()
    logger.info("Iniciando Zabbix MCP Server (100 ferramentas carregadas)...")

    if args.transport == "sse":
        logger.info(f"Escutando em SSE http://{args.host}:{args.port}")
        server.run(transport="sse")
    else:
        logger.info("Executando em transporte STDIO...")
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
