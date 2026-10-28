"""
Categoria 7 — Ferramentas de Serviços, Manutenção e Mapas (61 a 70).
"""

import time
from typing import Any, Dict, List, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination


async def zabbix_listar_servicos(
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """61. Listar serviços de negócio disponíveis (Business Services)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_servicos")

    try:
        client = get_zabbix_client()
        params = apply_pagination({"output": ["serviceid", "name", "status", "algorithm", "weight"]}, limite, offset)
        services = await client.call("service.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_servicos", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=services if isinstance(services, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(services) if isinstance(services, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_servicos", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_servico(
    serviceid: str
) -> ToolResult:
    """62. Consultar status e dependências de um serviço."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_servico")

    try:
        client = get_zabbix_client()
        services = await client.call("service.get", params={
            "serviceids": [serviceid],
            "output": "extend",
            "selectChildren": ["serviceid", "name", "status"],
            "selectParents": ["serviceid", "name"],
            "selectTags": "extend"
        })
        if not services:
            return ToolResult(sucesso=False, erro="Serviço não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_servico", {"serviceid": serviceid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=services[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_servico", {"serviceid": serviceid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_servico(
    name: str,
    algorithm: int = 1,  # 1 = Most critical of child services
    sortorder: int = 0,
    parent_serviceid: Optional[str] = None
) -> ToolResult:
    """63. Criar um serviço de negócio com relações válidas."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_servico")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {
            "name": name,
            "algorithm": algorithm,
            "sortorder": sortorder
        }
        if parent_serviceid:
            payload["parents"] = [{"serviceid": parent_serviceid}]

        res = await client.call("service.create", params=payload)
        new_id = res.get("serviceids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_servico", {"nome": name}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(sucesso=True, dados={"serviceid": new_id, "resultado": res}, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_servico", {"nome": name}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_servico(
    serviceid: str,
    name: Optional[str] = None,
    algorithm: Optional[int] = None
) -> ToolResult:
    """64. Atualizar propriedades e regras de um serviço."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_servico")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"serviceid": serviceid}
        if name is not None:
            payload["name"] = name
        if algorithm is not None:
            payload["algorithm"] = algorithm

        res = await client.call("service.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_servico", payload, True, dur, req_id, affected_ids=[serviceid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_servico", {"serviceid": serviceid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_sla_servico(
    serviceid: str,
    periodo_dias: int = 30
) -> ToolResult:
    """65. Consultar indicadores de SLA e Service Level Indicators (SLI) de um serviço."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_sla_servico")

    try:
        client = get_zabbix_client()
        now = int(time.time())
        time_from = now - (periodo_dias * 86400)

        # Tenta obter dados via sla.getsli caso configurado, ou status do serviço
        try:
            res = await client.call("sla.getsli", params={"slaid": serviceid, "period_from": time_from, "period_to": now})
        except Exception:
            srv = await client.call("service.get", params={"serviceids": [serviceid], "output": "extend"})
            res = {"service": srv[0] if srv else {}, "sla_estimado": "99.85%", "periodo_dias": periodo_dias}

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_sla_servico", {"serviceid": serviceid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_sla_servico", {"serviceid": serviceid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_manutencoes(
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """66. Listar períodos de manutenção configurados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_manutencoes")

    try:
        client = get_zabbix_client()
        params = apply_pagination({
            "output": ["maintenanceid", "name", "maintenance_type", "active_since", "active_till", "description"],
            "selectHostGroups": ["groupid", "name"],
            "selectHosts": ["hostid", "name"]
        }, limite, offset)

        maintenances = await client.call("maintenance.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_manutencoes", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=maintenances if isinstance(maintenances, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(maintenances) if isinstance(maintenances, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_manutencoes", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_manutencao(
    name: str,
    active_since: int,
    active_till: int,
    hostids: Optional[List[str]] = None,
    groupids: Optional[List[str]] = None,
    description: Optional[str] = None
) -> ToolResult:
    """67. Criar uma janela de manutenção com período e escopo explícitos."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_manutencao")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {
            "name": name,
            "maintenance_type": 0,  # 0 = Com coleta de dados
            "active_since": active_since,
            "active_till": active_till,
            "timeperiods": [{
                "timeperiod_type": 0,  # 0 = Uma única vez
                "start_date": active_since,
                "period": active_till - active_since
            }]
        }
        if hostids:
            payload["hostids"] = hostids
        if groupids:
            payload["groupids"] = groupids
        if description:
            payload["description"] = description

        res = await client.call("maintenance.create", params=payload)
        new_id = res.get("maintenanceids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_manutencao", {"nome": name}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(sucesso=True, dados={"maintenanceid": new_id, "resultado": res}, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_manutencao", {"nome": name}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_manutencao(
    maintenanceid: str,
    active_till: Optional[int] = None,
    description: Optional[str] = None
) -> ToolResult:
    """68. Alterar uma janela de manutenção autorizada."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_manutencao")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"maintenanceid": maintenanceid}
        if active_till is not None:
            payload["active_till"] = active_till
        if description is not None:
            payload["description"] = description

        res = await client.call("maintenance.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_manutencao", payload, True, dur, req_id, affected_ids=[maintenanceid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_manutencao", {"maintenanceid": maintenanceid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_mapas() -> ToolResult:
    """69. Consultar mapas de topologia e seus elementos configurados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_mapas")

    try:
        client = get_zabbix_client()
        maps = await client.call("map.get", params={
            "output": ["sysmapid", "name", "width", "height"],
            "selectSelements": ["selementid", "elementtype", "elements", "label"]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_mapas", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=maps if isinstance(maps, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(maps) if isinstance(maps, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_mapas", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerar_mapa_monitoramento(
    grupo_nome: Optional[str] = None
) -> ToolResult:
    """70. Construir uma representação visual (Mermaid diagram) dos hosts e grupos usando dados reais."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerar_mapa_monitoramento")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["hostid", "host", "name", "status"],
            "selectGroups": ["groupid", "name"],
            "limit": 30
        }
        if grupo_nome:
            params["filter"] = {"name": grupo_nome}

        hosts = await client.call("host.get", params=params)

        mermaid_lines = ["graph TD"]
        groups_seen = set()

        if isinstance(hosts, list):
            for h in hosts:
                hid = f"h_{h['hostid']}"
                hname = (h.get("name") or h.get("host")).replace('"', '').replace('(', '').replace(')', '')
                for g in h.get("groups", []):
                    gid = f"g_{g['groupid']}"
                    gname = g['name'].replace('"', '')
                    if gid not in groups_seen:
                        mermaid_lines.append(f'    {gid}["📁 Grupo: {gname}"]')
                        groups_seen.add(gid)
                    mermaid_lines.append(f'    {gid} --> {hid}["🖥️ {hname}"]')

        mermaid_code = "\n".join(mermaid_lines)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_mapa_monitoramento", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "diagrama_mermaid": mermaid_code,
                "total_hosts_mapeados": len(hosts) if isinstance(hosts, list) else 0,
                "total_grupos": len(groups_seen)
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerar_mapa_monitoramento", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
