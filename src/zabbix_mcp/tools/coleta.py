"""
Categoria 3 — Ferramentas de Coleta de Dados e Métricas (21 a 30).
"""

import time
from typing import Any, Dict, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination


async def zabbix_listar_itens(
    hostid: Optional[str] = None,
    chave: Optional[str] = None,
    status: Optional[int] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """21. Listar itens de coleta com filtros por host, chave, tipo e status."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_itens")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["itemid", "hostid", "name", "key_", "type", "value_type", "status", "state", "lastclock", "lastvalue", "units", "delay"]
        }
        if hostid:
            params["hostids"] = [hostid]
        if status is not None:
            params["filter"] = {"status": status}
        if chave:
            params["search"] = {"key_": chave}

        params = apply_pagination(params, limite, offset)
        items = await client.call("item.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_itens", {"hostid": hostid, "chave": chave}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=items if isinstance(items, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(items) if isinstance(items, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_itens", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_item(
    itemid: str
) -> ToolResult:
    """22. Consultar configuração e metadados de um item."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_item")

    try:
        client = get_zabbix_client()
        items = await client.call("item.get", params={"itemids": [itemid], "output": "extend"})
        if not items:
            return ToolResult(sucesso=False, erro="Item não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_item", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=items[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_item", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_item(
    hostid: str,
    name: str,
    key_: str,
    type: int = 0,         # 0 = Zabbix agent
    value_type: int = 3,   # 3 = Numeric unsigned
    interfaceid: Optional[str] = None,
    delay: str = "1m",
    units: Optional[str] = None
) -> ToolResult:
    """23. Criar itens de coleta quando suportado e autorizado."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_item")

    try:
        client = get_zabbix_client()
        if not interfaceid:
            # Obtém interface primária do host
            ifaces = await client.call("hostinterface.get", params={"hostids": [hostid], "filter": {"main": 1}})
            if ifaces and isinstance(ifaces, list):
                interfaceid = ifaces[0]["interfaceid"]
            else:
                return ToolResult(sucesso=False, erro="Host não possui interface cadastrada para associar ao item.", id_requisicao=req_id)

        payload: Dict[str, Any] = {
            "hostid": hostid,
            "name": name,
            "key_": key_,
            "type": type,
            "value_type": value_type,
            "interfaceid": interfaceid,
            "delay": delay
        }
        if units:
            payload["units"] = units

        res = await client.call("item.create", params=payload)
        new_id = res.get("itemids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_item", {"hostid": hostid, "key": key_}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(sucesso=True, dados={"itemid": new_id, "resultado": res}, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_item", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_item(
    itemid: str,
    name: Optional[str] = None,
    delay: Optional[str] = None,
    status: Optional[int] = None
) -> ToolResult:
    """24. Atualizar configurações permitidas de um item."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_item")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"itemid": itemid}
        if name is not None:
            payload["name"] = name
        if delay is not None:
            payload["delay"] = delay
        if status is not None:
            payload["status"] = status

        res = await client.call("item.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_item", payload, True, dur, req_id, affected_ids=[itemid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_item", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_historico(
    itemid: str,
    historico_tipo: int = 0,  # 0=float, 1=string, 2=log, 3=unsigned, 4=text
    limite: int = 50,
    tempo_de: Optional[int] = None,
    tempo_ate: Optional[int] = None
) -> ToolResult:
    """25. Consultar dados históricos de itens."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_historico")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "itemids": [itemid],
            "history": historico_tipo,
            "output": "extend",
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": min(limite, 500)
        }
        if tempo_de:
            params["time_from"] = tempo_de
        if tempo_ate:
            params["time_till"] = tempo_ate

        hist = await client.call("history.get", params=params)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_historico", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=hist if isinstance(hist, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(hist) if isinstance(hist, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_historico", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_tendencias(
    itemid: str,
    tempo_de: int,
    tempo_ate: int
) -> ToolResult:
    """26. Recuperar tendências (trends) para períodos disponíveis."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_tendencias")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "itemids": [itemid],
            "time_from": tempo_de,
            "time_till": tempo_ate,
            "output": ["itemid", "clock", "num", "value_min", "value_avg", "value_max"]
        }
        trends = await client.call("trend.get", params=params)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_tendencias", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=trends if isinstance(trends, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(trends) if isinstance(trends, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_tendencias", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_ultimos_valores(
    hostid: str,
    filtro_chave: Optional[str] = None
) -> ToolResult:
    """27. Consultar os últimos valores recebidos dos itens do host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_ultimos_valores")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "hostids": [hostid],
            "output": ["itemid", "name", "key_", "lastclock", "lastvalue", "units", "status"],
            "filter": {"status": 0}
        }
        if filtro_chave:
            params["search"] = {"key_": filtro_chave}

        items = await client.call("item.get", params=params)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_ultimos_valores", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=items if isinstance(items, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(items) if isinstance(items, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_ultimos_valores", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_verificar_coleta(
    hostid: str
) -> ToolResult:
    """28. Verificar se os itens ativos estão coletando dados dentro dos prazos esperados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_verificar_coleta")

    try:
        client = get_zabbix_client()
        now = int(time.time())
        items = await client.call("item.get", params={
            "hostids": [hostid],
            "filter": {"status": 0},
            "output": ["itemid", "name", "key_", "lastclock", "lastvalue", "state", "error", "delay"]
        })

        coletando = []
        sem_dados = []
        com_erro = []

        if isinstance(items, list):
            for i in items:
                err = i.get("error")
                lastclock = int(i.get("lastclock") or 0)
                if err or str(i.get("state")) == "1":
                    com_erro.append(i)
                elif lastclock == 0 or (now - lastclock > 86400):
                    sem_dados.append(i)
                else:
                    coletando.append(i)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_verificar_coleta", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "hostid": hostid,
                "total_itens_ativos": len(items) if isinstance(items, list) else 0,
                "itens_coletando_normalmente": len(coletando),
                "itens_sem_dados_recentes": len(sem_dados),
                "itens_com_erro": len(com_erro),
                "detalhes_erros": [{"itemid": x["itemid"], "nome": x["name"], "erro": x.get("error")} for x in com_erro[:10]]
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_verificar_coleta", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_detectar_lacunas_coleta(
    itemid: str,
    tempo_de: int,
    tempo_ate: int,
    tolerancia_multiplicador: float = 3.0
) -> ToolResult:
    """29. Identificar lacunas temporais (gaps) na coleta de um item."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_detectar_lacunas_coleta")

    try:
        client = get_zabbix_client()
        item_data = await client.call("item.get", params={"itemids": [itemid], "output": ["itemid", "name", "delay", "value_type"]})
        if not item_data:
            return ToolResult(sucesso=False, erro="Item não encontrado.", id_requisicao=req_id)

        v_type = int(item_data[0].get("value_type", 0))
        h_type = 0 if v_type == 0 else (3 if v_type == 3 else 1)

        history = await client.call("history.get", params={
            "itemids": [itemid],
            "history": h_type,
            "time_from": tempo_de,
            "time_till": tempo_ate,
            "sortfield": "clock",
            "sortorder": "ASC",
            "limit": 1000
        })

        gaps = []
        if isinstance(history, list) and len(history) > 1:
            # Intervalo esperado em segundos (default 60s se string não for pura)
            delay_sec = 60
            limite_gap = delay_sec * tolerancia_multiplicador

            for idx in range(len(history) - 1):
                c1 = int(history[idx]["clock"])
                c2 = int(history[idx + 1]["clock"])
                delta = c2 - c1
                if delta > limite_gap:
                    gaps.append({"de": c1, "ate": c2, "duracao_segundos": delta})

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_detectar_lacunas_coleta", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "itemid": itemid,
                "total_amostras": len(history) if isinstance(history, list) else 0,
                "total_lacunas_detectadas": len(gaps),
                "lacunas": gaps[:20]
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_detectar_lacunas_coleta", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_diagnosticar_coleta(
    hostid: str
) -> ToolResult:
    """30. Correlacionar erros, disponibilidade, intervalos e dados ausentes do host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_diagnosticar_coleta")

    try:
        client = get_zabbix_client()
        host_info = await client.call("host.get", params={
            "hostids": [hostid],
            "output": ["hostid", "host", "name", "status", "available", "error"],
            "selectInterfaces": ["interfaceid", "ip", "port", "type", "available", "error"],
            "selectItems": ["itemid", "name", "key_", "status", "state", "error", "lastclock"]
        })
        if not host_info:
            return ToolResult(sucesso=False, erro="Host não encontrado.", id_requisicao=req_id)

        h = host_info[0]
        diagnosticos = []

        if str(h.get("status")) == "1":
            diagnosticos.append("O host está com status 'Desativado'. Toda a coleta de dados está suspensa.")

        if h.get("error"):
            diagnosticos.append(f"Erro de comunicação do agente Zabbix: {h.get('error')}")

        for iface in h.get("interfaces", []):
            if iface.get("error"):
                diagnosticos.append(f"Erro na interface {iface.get('ip')}:{iface.get('port')} (Tipo {iface.get('type')}): {iface.get('error')}")

        items_err = [i for i in h.get("items", []) if i.get("error")]
        if items_err:
            diagnosticos.append(f"{len(items_err)} itens apresentam erro ou estado não suportado (unsupported).")

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_diagnosticar_coleta", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "hostid": hostid,
                "host": h.get("name") or h.get("host"),
                "status_geral": "saudavel" if not diagnosticos else "com_problemas",
                "diagnosticos": diagnosticos if diagnosticos else ["Nenhuma falha de coleta identificada."]
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_diagnosticar_coleta", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
