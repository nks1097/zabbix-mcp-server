"""
Categoria 2 — Ferramentas de Hosts e Interfaces (11 a 20).
"""

import time
from typing import Any, Dict, List, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination
from ..policies import verify_approval


async def zabbix_listar_hosts(
    nome: Optional[str] = None,
    grupo: Optional[str] = None,
    status: Optional[int] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """11. Listar hosts com filtros por nome, grupo, status e disponibilidade."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_hosts")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["hostid", "host", "name", "status", "available", "error"],
            "selectInterfaces": ["interfaceid", "ip", "dns", "port", "type", "available"],
            "selectGroups": ["groupid", "name"]
        }
        if nome:
            params["search"] = {"host": nome, "name": nome}
            params["searchByAny"] = True
        if status is not None:
            params["filter"] = {"status": status}
        if grupo:
            params["group"] = grupo

        params = apply_pagination(params, limite, offset)
        hosts = await client.call("host.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_hosts", {"nome": nome, "grupo": grupo}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=hosts if isinstance(hosts, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(hosts) if isinstance(hosts, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_hosts", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_host(
    hostid: Optional[str] = None,
    nome: Optional[str] = None
) -> ToolResult:
    """12. Consultar detalhes completos de um host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_host")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": "extend",
            "selectInterfaces": "extend",
            "selectGroups": ["groupid", "name"],
            "selectParentTemplates": ["templateid", "name"],
            "selectInventory": "extend"
        }
        if hostid:
            params["hostids"] = [hostid]
        elif nome:
            params["filter"] = {"host": [nome]}
        else:
            return ToolResult(sucesso=False, erro="Informe hostid ou nome do host.", id_requisicao=req_id)

        hosts = await client.call("host.get", params=params)
        if not hosts:
            return ToolResult(sucesso=False, erro="Host não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_host", {"hostid": hostid, "nome": nome}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=hosts[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_host", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_host(
    host: str,
    ip: str,
    grupos_ids: List[str],
    nome_visivel: Optional[str] = None,
    porta: str = "10050",
    tipo_interface: int = 1,
    templates_ids: Optional[List[str]] = None,
    campos_inventario: Optional[Dict[str, str]] = None
) -> ToolResult:
    """13. Criar um host com parâmetros validados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_host")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {
            "host": host,
            "name": nome_visivel or host,
            "status": 0,
            "groups": [{"groupid": gid} for gid in grupos_ids],
            "interfaces": [{
                "type": tipo_interface,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": porta
            }]
        }
        if templates_ids:
            payload["templates"] = [{"templateid": tid} for tid in templates_ids]
        if campos_inventario:
            payload["inventory_mode"] = 1
            payload["inventory"] = campos_inventario

        res = await client.call("host.create", params=payload)
        new_id = res.get("hostids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_host", {"host": host, "ip": ip}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(
            sucesso=True,
            dados={"hostid": new_id, "host": host, "mensagem": "Host criado com sucesso"},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_host", {"host": host}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_host(
    hostid: str,
    nome_visivel: Optional[str] = None,
    status: Optional[int] = None,
    descricao: Optional[str] = None
) -> ToolResult:
    """14. Atualizar propriedades permitidas de um host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_host")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"hostid": hostid}
        if nome_visivel is not None:
            payload["name"] = nome_visivel
        if status is not None:
            payload["status"] = status
        if descricao is not None:
            payload["description"] = descricao

        res = await client.call("host.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_host", payload, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_remover_host(
    hostid: str,
    token_aprovacao: Optional[str] = None
) -> ToolResult:
    """15. Remover um host somente após validação e confirmação (Ação destrutiva)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.ADMINISTRATIVO, "zabbix_remover_host")

    verify_approval("zabbix_remover_host", {"hostid": hostid}, token_aprovacao)

    try:
        client = get_zabbix_client()
        res = await client.call("host.delete", params=[hostid])
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_remover_host", {"hostid": hostid}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(
            sucesso=True,
            dados={"hostid": hostid, "resultado": res, "mensagem": "Host excluído com sucesso"},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_remover_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_ativar_desativar_host(
    hostid: str,
    status: int  # 0 = monitorado, 1 = não monitorado
) -> ToolResult:
    """16. Alterar o status de monitoramento de um host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_ativar_desativar_host")

    try:
        client = get_zabbix_client()
        res = await client.call("host.update", params={"hostid": hostid, "status": status})
        label = "monitorado" if status == 0 else "desativado"
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_ativar_desativar_host", {"hostid": hostid, "status": status}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(
            sucesso=True,
            dados={"hostid": hostid, "status": status, "status_label": label, "resultado": res},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_ativar_desativar_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_interfaces_host(
    hostid: str,
    acao: str,  # "consultar", "adicionar", "atualizar"
    interface_dados: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """17. Criar, consultar e atualizar interfaces suportadas do host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao

    try:
        client = get_zabbix_client()
        if acao == "consultar":
            check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerenciar_interfaces_host")
            ifaces = await client.call("hostinterface.get", params={"hostids": [hostid], "output": "extend"})
            dur = (time.time() - t0) * 1000
            return ToolResult(sucesso=True, dados=ifaces, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))

        check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_interfaces_host")
        if not interface_dados:
            return ToolResult(sucesso=False, erro="interface_dados é obrigatório para adicionar/atualizar.", id_requisicao=req_id)

        if acao == "adicionar":
            interface_dados["hostid"] = hostid
            res = await client.call("hostinterface.create", params=interface_dados)
        elif acao == "atualizar":
            res = await client.call("hostinterface.update", params=interface_dados)
        else:
            return ToolResult(sucesso=False, erro=f"Ação desconhecida: {acao}", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_interfaces_host", {"hostid": hostid, "acao": acao}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_interfaces_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_associar_templates_host(
    hostid: str,
    templates_ids: List[str]
) -> ToolResult:
    """18. Associar templates compatíveis ao host mantendo os existentes."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_associar_templates_host")

    try:
        client = get_zabbix_client()
        # Obtém templates atuais para não sobrescrever
        host_data = await client.call("host.get", params={"hostids": [hostid], "selectParentTemplates": ["templateid"]})
        current_templates = []
        if host_data and host_data[0].get("parentTemplates"):
            current_templates = [t["templateid"] for t in host_data[0]["parentTemplates"]]

        merged = list(set(current_templates + templates_ids))
        res = await client.call("host.update", params={
            "hostid": hostid,
            "templates": [{"templateid": tid} for tid in merged]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_associar_templates_host", {"hostid": hostid, "templates": templates_ids}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(
            sucesso=True,
            dados={"hostid": hostid, "total_templates_associados": len(merged), "resultado": res},
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_associar_templates_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_desassociar_templates_host(
    hostid: str,
    templates_ids: List[str],
    limpar_itens_triggers: bool = False
) -> ToolResult:
    """19. Remover associações de templates com opção de limpeza (unlink / clear)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_desassociar_templates_host")

    try:
        client = get_zabbix_client()
        field = "templates_clear" if limpar_itens_triggers else "templates"
        payload = {"hostid": hostid, field: [{"templateid": tid} for tid in templates_ids]}
        if limpar_itens_triggers:
            # No Zabbix API, templates_clear remove itens e triggers herdados
            payload = {"hostid": hostid, "templates_clear": [{"templateid": tid} for tid in templates_ids]}
        else:
            # Obtém atuais exceto os que serão desassociados
            host_data = await client.call("host.get", params={"hostids": [hostid], "selectParentTemplates": ["templateid"]})
            current = [t["templateid"] for t in host_data[0].get("parentTemplates", [])] if host_data else []
            kept = [tid for tid in current if tid not in templates_ids]
            payload = {"hostid": hostid, "templates": [{"templateid": tid} for tid in kept]}

        res = await client.call("host.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_desassociar_templates_host", {"hostid": hostid, "desassociados": templates_ids}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_desassociar_templates_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_disponibilidade_host(
    hostid: str
) -> ToolResult:
    """20. Consultar a disponibilidade e o estado observável do host."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_disponibilidade_host")

    try:
        client = get_zabbix_client()
        hosts = await client.call("host.get", params={
            "hostids": [hostid],
            "output": ["hostid", "host", "name", "status", "available", "error"],
            "selectInterfaces": ["interfaceid", "type", "ip", "port", "available", "error"]
        })
        if not hosts:
            return ToolResult(sucesso=False, erro="Host não encontrado.", id_requisicao=req_id)

        h = hosts[0]
        status_map = {"0": "Disponível (OK)", "1": "Indisponível (Falha)", "2": "Desconhecido / Sem Coleta"}

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_disponibilidade_host", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "hostid": h.get("hostid"),
                "host": h.get("name") or h.get("host"),
                "monitoramento": "Ativo" if str(h.get("status")) == "0" else "Desativado",
                "disponibilidade_geral": status_map.get(str(h.get("available")), "Indefinido"),
                "erro_geral": h.get("error") or "Nenhum erro registrado",
                "interfaces": h.get("interfaces", [])
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_disponibilidade_host", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
