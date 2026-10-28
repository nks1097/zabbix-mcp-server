"""
Categoria 8 — Ferramentas de Inventário, Grupos e Templates (71 a 80).
"""

import time
from typing import Any, Dict, List, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination
from ..policies import verify_approval


async def zabbix_consultar_inventario(
    hostid: Optional[str] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """71. Consultar inventário de hardware, software e metadados de hosts."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_inventario")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["hostid", "host", "name"],
            "selectInventory": "extend",
            "filter": {"inventory_mode": [0, 1]}  # Manual ou Automático
        }
        if hostid:
            params["hostids"] = [hostid]

        params = apply_pagination(params, limite, offset)
        hosts = await client.call("host.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_inventario", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=hosts if isinstance(hosts, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(hosts) if isinstance(hosts, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_inventario", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_inventario(
    hostid: str,
    campos_inventario: Dict[str, str],
    modo_inventario: int = 1  # 0 = Manual, 1 = Automático
) -> ToolResult:
    """72. Atualizar campos de inventário permitidos de um host (ex: os, location, tag, notes)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_inventario")

    try:
        client = get_zabbix_client()
        res = await client.call("host.update", params={
            "hostid": hostid,
            "inventory_mode": modo_inventario,
            "inventory": campos_inventario
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_inventario", {"hostid": hostid}, True, dur, req_id, affected_ids=[hostid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_inventario", {"hostid": hostid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_grupos_hosts(
    nome: Optional[str] = None
) -> ToolResult:
    """73. Listar grupos de hosts cadastrados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_grupos_hosts")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {"output": ["groupid", "name", "flags"]}
        if nome:
            params["filter"] = {"name": [nome]}

        groups = await client.call("hostgroup.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_grupos_hosts", {"nome": nome}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=groups if isinstance(groups, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(groups) if isinstance(groups, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_grupos_hosts", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_grupos_hosts(
    acao: str,  # "criar", "atualizar", "excluir"
    nome: Optional[str] = None,
    groupid: Optional[str] = None,
    token_aprovacao: Optional[str] = None
) -> ToolResult:
    """74. Criar, atualizar ou excluir grupos de hosts com as verificações necessárias."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao

    try:
        client = get_zabbix_client()
        if acao == "criar":
            check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_grupos_hosts")
            if not nome:
                return ToolResult(sucesso=False, erro="Nome é obrigatório para criar grupo.", id_requisicao=req_id)
            res = await client.call("hostgroup.create", params={"name": nome})
        elif acao == "atualizar":
            check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_grupos_hosts")
            if not groupid or not nome:
                return ToolResult(sucesso=False, erro="groupid e nome são obrigatórios para atualizar.", id_requisicao=req_id)
            res = await client.call("hostgroup.update", params={"groupid": groupid, "name": nome})
        elif acao == "excluir":
            check_permission(AuthorizationMode.ADMINISTRATIVO, "zabbix_gerenciar_grupos_hosts")
            if not groupid:
                return ToolResult(sucesso=False, erro="groupid é obrigatório para excluir.", id_requisicao=req_id)
            verify_approval("zabbix_gerenciar_grupos_hosts", {"acao": "excluir", "groupid": groupid}, token_aprovacao)
            res = await client.call("hostgroup.delete", params=[groupid])
        else:
            return ToolResult(sucesso=False, erro=f"Ação desconhecida: {acao}", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_grupos_hosts", {"acao": acao, "nome": nome}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_grupos_hosts", {"acao": acao}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_templates(
    nome: Optional[str] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """75. Listar templates disponíveis e associações no Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_templates")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["templateid", "host", "name", "description"]
        }
        if nome:
            params["search"] = {"name": nome, "host": nome}
            params["searchByAny"] = True

        params = apply_pagination(params, limite, offset)
        templates = await client.call("template.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_templates", {"nome": nome}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=templates if isinstance(templates, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(templates) if isinstance(templates, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_templates", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_template(
    templateid: str
) -> ToolResult:
    """76. Consultar configurações, itens, triggers e macros de um template."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_template")

    try:
        client = get_zabbix_client()
        templates = await client.call("template.get", params={
            "templateids": [templateid],
            "output": "extend",
            "selectItems": ["itemid", "name", "key_", "delay"],
            "selectTriggers": ["triggerid", "description", "priority"],
            "selectMacros": "extend"
        })
        if not templates:
            return ToolResult(sucesso=False, erro="Template não encontrado.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_template", {"templateid": templateid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=templates[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_template", {"templateid": templateid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_criar_template(
    host: str,
    name: Optional[str] = None,
    grupos_ids: Optional[List[str]] = None,
    description: Optional[str] = None
) -> ToolResult:
    """77. Criar novo template no Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_template")

    try:
        client = get_zabbix_client()
        # Se nenhum grupo for informado, busca primeiro grupo existente
        g_ids = grupos_ids or []
        if not g_ids:
            groups = await client.call("hostgroup.get", params={"limit": 1})
            if groups and isinstance(groups, list):
                g_ids = [groups[0]["groupid"]]

        payload: Dict[str, Any] = {
            "host": host,
            "name": name or host,
            "groups": [{"groupid": gid} for gid in g_ids]
        }
        if description:
            payload["description"] = description

        res = await client.call("template.create", params=payload)
        new_id = res.get("templateids", [""])[0] if res else ""

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_template", {"host": host}, True, dur, req_id, affected_ids=[new_id])
        return ToolResult(sucesso=True, dados={"templateid": new_id, "resultado": res}, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_criar_template", {"host": host}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_atualizar_template(
    templateid: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> ToolResult:
    """78. Atualizar propriedades e objetos de um template."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_atualizar_template")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"templateid": templateid}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        res = await client.call("template.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_template", payload, True, dur, req_id, affected_ids=[templateid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_atualizar_template", {"templateid": templateid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_grupos_templates(
    acao: str = "listar",
    nome: Optional[str] = None
) -> ToolResult:
    """79. Consultar e gerenciar grupos de templates (templategroup ou hostgroup conforme versão)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao

    try:
        client = get_zabbix_client()
        # Zabbix 6.2+ introduziu templategroup.get separado de hostgroup
        try:
            if acao == "listar":
                check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_gerenciar_grupos_templates")
                res = await client.call("templategroup.get", params={"output": "extend"})
            elif acao == "criar" and nome:
                check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_grupos_templates")
                res = await client.call("templategroup.create", params={"name": nome})
            else:
                return ToolResult(sucesso=False, erro="Ação ou parâmetro inválido.", id_requisicao=req_id)
        except Exception:
            # Fallback para hostgroup.get se for versão anterior que unifica grupos
            res = await client.call("hostgroup.get", params={"output": ["groupid", "name"]})

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_grupos_templates", {"acao": acao}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=res if isinstance(res, list) else [res],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_grupos_templates", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_auditar_cobertura_templates() -> ToolResult:
    """80. Auditar hosts sem templates adequados, associações vazias e possíveis lacunas."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_auditar_cobertura_templates")

    try:
        client = get_zabbix_client()
        hosts = await client.call("host.get", params={
            "output": ["hostid", "host", "name", "status"],
            "selectParentTemplates": ["templateid", "name"]
        })

        hosts_sem_template = []
        hosts_com_poucos_templates = []

        if isinstance(hosts, list):
            for h in hosts:
                t_list = h.get("parentTemplates", [])
                if len(t_list) == 0:
                    hosts_sem_template.append({"hostid": h["hostid"], "host": h.get("name") or h.get("host")})
                elif len(t_list) == 1 and "ping" in t_list[0].get("name", "").lower():
                    hosts_com_poucos_templates.append({
                        "hostid": h["hostid"],
                        "host": h.get("name") or h.get("host"),
                        "template": t_list[0].get("name")
                    })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_auditar_cobertura_templates", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "total_hosts_analisados": len(hosts) if isinstance(hosts, list) else 0,
                "hosts_sem_template": hosts_sem_template,
                "hosts_apenas_com_icmp_ping": hosts_com_poucos_templates,
                "diagnostico": (
                    f"Identificados {len(hosts_sem_template)} hosts sem nenhum template associado "
                    f"e {len(hosts_com_poucos_templates)} monitorados exclusivamente por Ping."
                )
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_auditar_cobertura_templates", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
