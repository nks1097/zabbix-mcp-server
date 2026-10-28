"""
Categoria 9 — Ferramentas de Descoberta Nativa, Proxies e Administração (81 a 90).
"""

import time
from typing import Any, Dict, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..policies import verify_approval


async def zabbix_listar_regras_descoberta() -> ToolResult:
    """81. Listar regras nativas de descoberta de rede (Network Discovery Rules)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_regras_descoberta")

    try:
        client = get_zabbix_client()
        drules = await client.call("drule.get", params={
            "output": ["druleid", "name", "iprange", "delay", "status"],
            "selectDChecks": ["dcheckid", "type", "key_", "ports"]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_regras_descoberta", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=drules if isinstance(drules, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(drules) if isinstance(drules, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_regras_descoberta", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_regras_descoberta(
    acao: str,  # "habilitar", "desabilitar", "atualizar_faixa"
    druleid: str,
    iprange: Optional[str] = None
) -> ToolResult:
    """82. Gerenciar regras nativas de descoberta de rede (drule)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_regras_descoberta")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"druleid": druleid}
        if acao == "habilitar":
            payload["status"] = 0
        elif acao == "desabilitar":
            payload["status"] = 1
        elif acao == "atualizar_faixa" and iprange:
            payload["iprange"] = iprange
        else:
            return ToolResult(sucesso=False, erro=f"Ação ou parâmetro inválido: {acao}", id_requisicao=req_id)

        res = await client.call("drule.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_regras_descoberta", payload, True, dur, req_id, affected_ids=[druleid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_regras_descoberta", {"druleid": druleid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_descoberta_baixo_nivel(
    hostid: Optional[str] = None
) -> ToolResult:
    """83. Consultar regras LLD (Low-Level Discovery) e protótipos."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_descoberta_baixo_nivel")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["itemid", "name", "key_", "delay", "status", "state", "error"],
            "selectItemPrototypes": ["itemid", "name", "key_"],
            "selectTriggerPrototypes": ["triggerid", "description"]
        }
        if hostid:
            params["hostids"] = [hostid]

        lld_rules = await client.call("discoveryrule.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_descoberta_baixo_nivel", {"hostid": hostid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=lld_rules if isinstance(lld_rules, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(lld_rules) if isinstance(lld_rules, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_descoberta_baixo_nivel", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_proxies() -> ToolResult:
    """84. Listar proxies cadastrados no Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_proxies")

    try:
        client = get_zabbix_client()
        proxies = await client.call("proxy.get", params={
            "output": ["proxyid", "name", "operating_mode", "lastaccess", "description"]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_proxies", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=proxies if isinstance(proxies, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(proxies) if isinstance(proxies, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_proxies", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_proxy(
    proxyid: str
) -> ToolResult:
    """85. Consultar detalhes, latência e estado observável de um proxy."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_proxy")

    try:
        client = get_zabbix_client()
        proxies = await client.call("proxy.get", params={
            "proxyids": [proxyid],
            "output": "extend",
            "selectAssignedHosts": ["hostid", "host", "name"]
        })
        if not proxies:
            return ToolResult(sucesso=False, erro="Proxy não encontrado.", id_requisicao=req_id)

        p = proxies[0]
        now = int(time.time())
        lastaccess = int(p.get("lastaccess") or 0)
        delta_sec = now - lastaccess if lastaccess > 0 else -1

        status_conectividade = "online" if (delta_sec >= 0 and delta_sec < 300) else "atrasado_ou_offline"

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_proxy", {"proxyid": proxyid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "proxy": p,
                "ultimo_acesso_segundos_atras": delta_sec,
                "status_conectividade": status_conectividade
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_proxy", {"proxyid": proxyid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_proxies(
    acao: str,  # "criar", "atualizar", "excluir"
    nome: Optional[str] = None,
    proxyid: Optional[str] = None,
    operating_mode: int = 0,  # 0=Active, 1=Passive
    token_aprovacao: Optional[str] = None
) -> ToolResult:
    """86. Gerenciar proxies (criar, atualizar ou excluir com aprovação)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.ADMINISTRATIVO, "zabbix_gerenciar_proxies")

    try:
        client = get_zabbix_client()
        if acao == "criar":
            if not nome:
                return ToolResult(sucesso=False, erro="Nome é obrigatório para cadastrar proxy.", id_requisicao=req_id)
            res = await client.call("proxy.create", params={"name": nome, "operating_mode": operating_mode})
        elif acao == "atualizar":
            if not proxyid:
                return ToolResult(sucesso=False, erro="proxyid é obrigatório para atualizar.", id_requisicao=req_id)
            payload: Dict[str, Any] = {"proxyid": proxyid}
            if nome:
                payload["name"] = nome
            res = await client.call("proxy.update", params=payload)
        elif acao == "excluir":
            if not proxyid:
                return ToolResult(sucesso=False, erro="proxyid é obrigatório para excluir.", id_requisicao=req_id)
            verify_approval("zabbix_gerenciar_proxies", {"acao": "excluir", "proxyid": proxyid}, token_aprovacao)
            res = await client.call("proxy.delete", params=[proxyid])
        else:
            return ToolResult(sucesso=False, erro=f"Ação desconhecida: {acao}", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_proxies", {"acao": acao, "nome": nome}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_proxies", {"acao": acao}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_usuarios() -> ToolResult:
    """87. Consultar usuários cadastrados (sem expor senhas ou tokens)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_usuarios")

    try:
        client = get_zabbix_client()
        users = await client.call("user.get", params={
            "output": ["userid", "username", "name", "surname", "roleid"],
            "selectRole": ["roleid", "name", "type"]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_usuarios", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=users if isinstance(users, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(users) if isinstance(users, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_usuarios", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_funcoes_usuario() -> ToolResult:
    """88. Consultar funções e papéis de usuário (User Roles) e permissões."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_funcoes_usuario")

    try:
        client = get_zabbix_client()
        roles = await client.call("role.get", params={
            "output": ["roleid", "name", "type", "readonly"],
            "selectRules": "extend"
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_funcoes_usuario", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=roles if isinstance(roles, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(roles) if isinstance(roles, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_funcoes_usuario", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_auditoria(
    limite: int = 50
) -> ToolResult:
    """89. Consultar registros nativos de auditoria do Zabbix (Audit Log)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_auditoria")

    try:
        client = get_zabbix_client()
        logs = await client.call("auditlog.get", params={
            "output": ["auditid", "userid", "username", "clock", "action", "resourcetype", "ip", "details"],
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": min(limite, 200)
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_auditoria", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=logs if isinstance(logs, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(logs) if isinstance(logs, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_auditoria", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_estado_sistema() -> ToolResult:
    """90. Recuperar versão do Zabbix, nós de HA, fila e estado geral do sistema."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_estado_sistema")

    try:
        client = get_zabbix_client()
        version = await client.get_version()

        ha_nodes = []
        try:
            ha_res = await client.call("ha.get", params={})
            if isinstance(ha_res, list):
                ha_nodes = ha_res
        except Exception:
            pass

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_estado_sistema", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "versao_zabbix": version,
                "alta_disponibilidade_ha": ha_nodes,
                "status_servidor": "online",
                "timestamp_verificacao": int(time.time())
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, versao_zabbix=version)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_estado_sistema", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
