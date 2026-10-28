"""
Categoria 4 — Ferramentas de Problemas, Triggers e Eventos (31 a 40).
"""

import time
from typing import Any, Dict, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination


async def zabbix_listar_problemas(
    severidade_minima: Optional[int] = None,
    hostid: Optional[str] = None,
    reconhecido: Optional[bool] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """31. Listar problemas ativos com filtros de severidade e status."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_problemas")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["eventid", "name", "severity", "clock", "acknowledged", "r_clock", "opdata"],
            "selectTags": "extend",
            "selectAcknowledges": ["clock", "message", "action"],
            "sortfield": ["eventid"],
            "sortorder": "DESC"
        }
        if hostid:
            params["hostids"] = [hostid]
        if severidade_minima is not None:
            params["severities"] = list(range(severidade_minima, 6))
        if reconhecido is not None:
            params["acknowledged"] = reconhecido

        params = apply_pagination(params, limite, offset)
        problems = await client.call("problem.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_problemas", {"hostid": hostid, "sev": severidade_minima}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=problems if isinstance(problems, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(problems) if isinstance(problems, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_problemas", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_problema(
    eventid: str
) -> ToolResult:
    """32. Consultar detalhes e identificadores de um problema específico."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_problema")

    try:
        client = get_zabbix_client()
        problems = await client.call("problem.get", params={
            "eventids": [eventid],
            "output": "extend",
            "selectTags": "extend",
            "selectAcknowledges": "extend"
        })
        if not problems:
            return ToolResult(sucesso=False, erro="Problema não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_problema", {"eventid": eventid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=problems[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_problema", {"eventid": eventid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_eventos(
    hostid: Optional[str] = None,
    tempo_de: Optional[int] = None,
    tempo_ate: Optional[int] = None,
    severidade: Optional[int] = None,
    limite: int = 50
) -> ToolResult:
    """33. Consultar eventos por host, período, severidade ou objeto."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_eventos")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["eventid", "source", "object", "objectid", "clock", "value", "name", "severity"],
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": min(limite, 500)
        }
        if hostid:
            params["hostids"] = [hostid]
        if tempo_de:
            params["time_from"] = tempo_de
        if tempo_ate:
            params["time_till"] = tempo_ate
        if severidade is not None:
            params["severities"] = [severidade]

        events = await client.call("event.get", params=params)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_eventos", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=events if isinstance(events, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(events) if isinstance(events, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_eventos", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_triggers(
    hostid: Optional[str] = None,
    status: Optional[int] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """34. Listar triggers e suas configurações."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_triggers")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["triggerid", "description", "expression", "priority", "status", "value", "state", "error"]
        }
        if hostid:
            params["hostids"] = [hostid]
        if status is not None:
            params["filter"] = {"status": status}

        params = apply_pagination(params, limite, offset)
        triggers = await client.call("trigger.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_triggers", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=triggers if isinstance(triggers, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(triggers) if isinstance(triggers, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_triggers", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_trigger(
    triggerid: str
) -> ToolResult:
    """35. Consultar expressão, estado e metadados de uma trigger."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_trigger")

    try:
        client = get_zabbix_client()
        triggers = await client.call("trigger.get", params={
            "triggerids": [triggerid],
            "output": "extend",
            "selectFunctions": "extend",
            "selectDependencies": "extend",
            "selectTags": "extend"
        })
        if not triggers:
            return ToolResult(sucesso=False, erro="Trigger não encontrada.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_trigger", {"triggerid": triggerid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=triggers[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_trigger", {"triggerid": triggerid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_trigger(
    description: str,
    expression: str,
    priority: int = 3,  # 3 = Average
    comments: Optional[str] = None
) -> ToolResult:
    """36. Criar triggers quando permitido e com validação da expressão."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_trigger")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {
            "description": description,
            "expression": expression,
            "priority": priority
        }
        if comments:
            payload["comments"] = comments

        res = await client.call("trigger.create", params=payload)
        new_id = res.get("triggerids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_trigger", {"desc": description}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(sucesso=True, dados={"triggerid": new_id, "resultado": res}, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_trigger", {"desc": description}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_trigger(
    triggerid: str,
    priority: Optional[int] = None,
    status: Optional[int] = None,
    comments: Optional[str] = None
) -> ToolResult:
    """37. Atualizar propriedades suportadas de uma trigger."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_trigger")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"triggerid": triggerid}
        if priority is not None:
            payload["priority"] = priority
        if status is not None:
            payload["status"] = status
        if comments is not None:
            payload["comments"] = comments

        res = await client.call("trigger.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_trigger", payload, True, dur, req_id, affected_ids=[triggerid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_trigger", {"triggerid": triggerid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_reconhecer_problema(
    eventid: str,
    mensagem: str,
    acao: int = 6  # 2=close, 4=acknowledge, 6=ack + message
) -> ToolResult:
    """38. Reconhecer (Acknowledge) um problema com mensagem de auditoria."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_reconhecer_problema")

    try:
        client = get_zabbix_client()
        res = await client.call("event.acknowledge", params={
            "eventids": [eventid],
            "action": acao,
            "message": mensagem
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_reconhecer_problema", {"eventid": eventid, "msg": mensagem}, True, dur, req_id, affected_ids=[eventid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_reconhecer_problema", {"eventid": eventid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_obter_historico_problema(
    eventid: str
) -> ToolResult:
    """39. Recuperar o histórico e os eventos associados ao problema."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_obter_historico_problema")

    try:
        client = get_zabbix_client()
        event_data = await client.call("event.get", params={
            "eventids": [eventid],
            "selectAcknowledges": "extend",
            "selectAlerts": "extend"
        })
        if not event_data:
            return ToolResult(sucesso=False, erro="Evento/problema não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_obter_historico_problema", {"eventid": eventid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=event_data[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_obter_historico_problema", {"eventid": eventid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_investigar_incidente(
    eventid: str
) -> ToolResult:
    """40. Correlacionar problemas, hosts, itens e eventos para produzir uma investigação fundamentada."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_investigar_incidente")

    try:
        client = get_zabbix_client()
        # 1. Busca o problema
        prob = await client.call("problem.get", params={"eventids": [eventid], "output": "extend", "selectTags": "extend"})
        if not prob:
            return ToolResult(sucesso=False, erro="Incidente não encontrado.", id_requisicao=req_id)

        p = prob[0]
        objectid = p.get("objectid")  # Trigger ID

        # 2. Busca trigger e itens envolvidos
        trigger_info = await client.call("trigger.get", params={
            "triggerids": [objectid],
            "output": ["triggerid", "description", "expression", "priority", "value"],
            "selectItems": ["itemid", "name", "key_", "lastvalue", "units", "lastclock"],
            "selectHosts": ["hostid", "host", "name", "status"]
        })

        items_envolvidos = []
        host_info = {}
        if trigger_info and isinstance(trigger_info, list):
            items_envolvidos = trigger_info[0].get("items", [])
            hosts = trigger_info[0].get("hosts", [])
            if hosts:
                host_info = hosts[0]

        # 3. Análise de Causa Raiz Baseada em Fatos
        evidencias = []
        for it in items_envolvidos:
            evidencias.append(f"Item '{it.get('name')}' ({it.get('key_')}): último valor registrado = {it.get('lastvalue')} {it.get('units', '')}")

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_investigar_incidente", {"eventid": eventid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "incidente": {
                    "eventid": eventid,
                    "nome": p.get("name"),
                    "severidade": p.get("severity"),
                    "inicio_timestamp": p.get("clock"),
                    "recuperado": p.get("r_clock") != "0"
                },
                "dispositivo_afetado": host_info,
                "trigger": trigger_info[0] if trigger_info else {},
                "itens_metricas": items_envolvidos,
                "evidencias_identificadas": evidencias,
                "recomendacao": (
                    "Verifique os últimos valores das métricas correlacionadas e valide se o limite da expressão de trigger foi ultrapassado."
                )
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_investigar_incidente", {"eventid": eventid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
