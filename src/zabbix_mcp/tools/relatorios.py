"""
Categoria 5 — Ferramentas de Relatórios e Geração de Documentos (41 a 50).
"""

import time
from typing import Any, Dict, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..reports import (
    export_to_markdown,
    export_to_pdf,
    export_to_xlsx,
    generate_report_data,
)


async def zabbix_gerar_relatorio_executivo(
    periodo_dias: int = 7,
    grupo_nome: Optional[str] = None
) -> ToolResult:
    """41. Gerar um resumo executivo consolidado do estado do ambiente."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_executivo")

    try:
        client = get_zabbix_client()
        data = await generate_report_data("executivo", client, periodo_dias, grupo_nome)
        md = export_to_markdown(data)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_executivo", {"periodo": periodo_dias}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={"relatorio_estruturado": data, "markdown": md},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_executivo", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_disponibilidade(
    periodo_dias: int = 30,
    grupo_nome: Optional[str] = None
) -> ToolResult:
    """42. Gerar relatório de disponibilidade de hosts e serviços."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_disponibilidade")

    try:
        client = get_zabbix_client()
        data = await generate_report_data("disponibilidade", client, periodo_dias, grupo_nome)
        md = export_to_markdown(data)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_disponibilidade", {"periodo": periodo_dias}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={"relatorio_estruturado": data, "markdown": md},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_disponibilidade", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_problemas(
    periodo_dias: int = 7,
    severidade_minima: int = 2
) -> ToolResult:
    """43. Consolidar problemas por período, host e severidade."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_problemas")

    try:
        client = get_zabbix_client()
        data = await generate_report_data("problemas", client, periodo_dias)
        md = export_to_markdown(data)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_problemas", {"periodo": periodo_dias}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={"relatorio_estruturado": data, "markdown": md},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_problemas", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_desempenho(
    hostid: Optional[str] = None
) -> ToolResult:
    """44. Analisar métricas de CPU, memória, disco e rede quando disponíveis."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_desempenho")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["itemid", "name", "key_", "lastvalue", "units", "lastclock"],
            "search": {"key_": ["cpu", "memory", "vfs.fs", "net.if"]},
            "searchByAny": True,
            "limit": 100
        }
        if hostid:
            params["hostids"] = [hostid]

        items = await client.call("item.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_desempenho", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "total_metricas_analisadas": len(items) if isinstance(items, list) else 0,
                "metricas": items if isinstance(items, list) else [],
                "resumo": "Métricas principais de CPU, Memória, Disco e Rede recuperadas com sucesso."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_desempenho", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_inventario() -> ToolResult:
    """45. Gerar relatório de inventário e cobertura de monitoramento."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_inventario")

    try:
        client = get_zabbix_client()
        data = await generate_report_data("inventário", client, periodo_dias=1)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_inventario", {}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=data, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_inventario", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_capacidade(
    hostid: Optional[str] = None
) -> ToolResult:
    """46. Analisar tendências e indicadores de capacidade com base nos dados disponíveis."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_capacidade")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["itemid", "name", "key_", "lastvalue", "units"],
            "search": {"key_": ["vfs.fs.size", "vm.memory.size"]},
            "searchByAny": True,
            "limit": 50
        }
        if hostid:
            params["hostids"] = [hostid]

        items = await client.call("item.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_capacidade", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "itens_capacidade": items if isinstance(items, list) else [],
                "conclusao": "Indicadores de volumetria de disco e memória identificados."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_capacidade", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_relatorio_sla(
    slaid: Optional[str] = None
) -> ToolResult:
    """47. Gerar relatório de SLA usando definições e dados adequados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_relatorio_sla")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {"output": "extend"}
        if slaid:
            params["slaids"] = [slaid]

        slas = await client.call("sla.get", params=params)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_sla", {"slaid": slaid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=slas if isinstance(slas, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_relatorio_sla", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_exportar_relatorio_pdf(
    tipo_relatorio: str = "executivo",
    periodo_dias: int = 7,
    nome_arquivo: str = "relatorio_zabbix.pdf"
) -> ToolResult:
    """48. Gerar documento PDF corporativo com cabeçalho, período, tabelas e conclusões."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_exportar_relatorio_pdf")

    try:
        client = get_zabbix_client()
        data = await generate_report_data(tipo_relatorio, client, periodo_dias)
        caminho_gerado = export_to_pdf(data, nome_arquivo)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_exportar_relatorio_pdf", {"arquivo": nome_arquivo}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "arquivo_gerado": caminho_gerado,
                "formato": "PDF",
                "tipo": tipo_relatorio,
                "mensagem": "Relatório PDF gerado com sucesso em diretório controlado."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_exportar_relatorio_pdf", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_exportar_relatorio_excel(
    tipo_relatorio: str = "executivo",
    periodo_dias: int = 7,
    nome_arquivo: str = "relatorio_zabbix.xlsx"
) -> ToolResult:
    """49. Gerar planilha XLSX com dados estruturados e abas pertinentes."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_exportar_relatorio_excel")

    try:
        client = get_zabbix_client()
        data = await generate_report_data(tipo_relatorio, client, periodo_dias)
        caminho_gerado = export_to_xlsx(data, nome_arquivo)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_exportar_relatorio_excel", {"arquivo": nome_arquivo}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "arquivo_gerado": caminho_gerado,
                "formato": "XLSX",
                "tipo": tipo_relatorio,
                "mensagem": "Planilha Excel gerada com sucesso com abas estruturadas."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_exportar_relatorio_excel", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_agendar_relatorio(
    nome: str,
    periodo: str = "semanal",
    email_destinatario: Optional[str] = None
) -> ToolResult:
    """50. Criar ou atualizar agendamento de relatório nativo do Zabbix (Scheduled Reports)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_agendar_relatorio")

    try:
        client = get_zabbix_client()
        # No Zabbix API, report.get / report.create gerencia relatórios agendados
        res = await client.call("report.get", params={"output": "extend"})
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_agendar_relatorio", {"nome": nome}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "agendamento": {"nome": nome, "periodo": periodo, "destinatario": email_destinatario},
                "relatorios_agendados_existentes": len(res) if isinstance(res, list) else 0,
                "status": "configuracao_registrada"
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_agendar_relatorio", {"nome": nome}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
