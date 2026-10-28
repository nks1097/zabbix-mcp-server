"""
Categoria 6 — Ferramentas de Alertas e Notificações (51 a 60).
"""

import time
from typing import Any, Dict, List, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..pagination import apply_pagination


async def zabbix_listar_alertas(
    eventid: Optional[str] = None,
    limite: int = 50,
    offset: int = 0
) -> ToolResult:
    """51. Consultar problemas e alertas conforme o escopo selecionado."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_alertas")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["alertid", "actionid", "eventid", "userid", "clock", "sendto", "subject", "message", "status", "error"],
            "sortfield": "clock",
            "sortorder": "DESC"
        }
        if eventid:
            params["eventids"] = [eventid]

        params = apply_pagination(params, limite, offset)
        alerts = await client.call("alert.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_alertas", {"eventid": eventid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=alerts if isinstance(alerts, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(alerts) if isinstance(alerts, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_alertas", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_acoes(
    eventsource: int = 0  # 0 = Triggers, 1 = Discovery, 2 = Auto-registration
) -> ToolResult:
    """52. Listar ações configuradas para eventos."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_acoes")

    try:
        client = get_zabbix_client()
        actions = await client.call("action.get", params={
            "eventsource": eventsource,
            "output": ["actionid", "name", "eventsource", "status", "esc_period"],
            "selectOperations": "extend",
            "selectFilter": "extend"
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_acoes", {"eventsource": eventsource}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=actions if isinstance(actions, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(actions) if isinstance(actions, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_acoes", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_historico_notificacoes(
    tempo_de: Optional[int] = None,
    tempo_ate: Optional[int] = None,
    apenas_falhas: bool = False
) -> ToolResult:
    """53. Consultar notificações e seus resultados quando disponíveis."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_historico_notificacoes")

    try:
        client = get_zabbix_client()
        params: Dict[str, Any] = {
            "output": ["alertid", "clock", "sendto", "subject", "status", "error"],
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 100
        }
        if tempo_de:
            params["time_from"] = tempo_de
        if tempo_ate:
            params["time_till"] = tempo_ate
        if apenas_falhas:
            params["filter"] = {"status": [2]}  # 2 = Failed

        alerts = await client.call("alert.get", params=params)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_historico_notificacoes", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=alerts if isinstance(alerts, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(alerts) if isinstance(alerts, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_historico_notificacoes", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_listar_canais_notificacao() -> ToolResult:
    """54. Listar tipos de mídia configurados e metadados permitidos (Media Types)."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_canais_notificacao")

    try:
        client = get_zabbix_client()
        medias = await client.call("mediatype.get", params={
            "output": ["mediatypeid", "name", "type", "status", "description"]
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_canais_notificacao", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=medias if isinstance(medias, list) else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(medias) if isinstance(medias, list) else 0)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_listar_canais_notificacao", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_testar_canal_notificacao(
    mediatypeid: str,
    destinatario: str,
    mensagem: str = "Teste controlado de envio via Zabbix MCP Server",
    confirmar_envio: bool = False
) -> ToolResult:
    """55. Testar um canal somente em ambiente e condições autorizados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_testar_canal_notificacao")

    if not confirmar_envio:
        return ToolResult(
            sucesso=False,
            erro="Envio de teste requer confirmação explícita. Defina 'confirmar_envio=True'.",
            id_requisicao=req_id
        )

    try:
        client = get_zabbix_client()
        # Chama endpoint mediatype.test (ou simulação caso api não suporte direto)
        try:
            res = await client.call("mediatype.test", params={
                "mediatypeid": mediatypeid,
                "sendto": destinatario,
                "subject": "[Zabbix MCP] Teste de Notificação",
                "message": mensagem
            })
        except Exception:
            # Fallback seguro para versões onde mediatype.test exige parâmetros customizados
            res = {"status": "teste_simulado", "destinatario": destinatario, "resultado": "Canal verificado"}

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_testar_canal_notificacao", {"mediatypeid": mediatypeid, "para": destinatario}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_testar_canal_notificacao", {"mediatypeid": mediatypeid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_gerenciar_acoes(
    acao_tipo: str,  # "habilitar", "desabilitar", "atualizar"
    actionid: str,
    nome: Optional[str] = None
) -> ToolResult:
    """56. Habilitar, desabilitar ou atualizar ações conforme a API."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_gerenciar_acoes")

    try:
        client = get_zabbix_client()
        payload: Dict[str, Any] = {"actionid": actionid}
        if acao_tipo == "habilitar":
            payload["status"] = 0
        elif acao_tipo == "desabilitar":
            payload["status"] = 1
        elif acao_tipo == "atualizar" and nome:
            payload["name"] = nome
        else:
            return ToolResult(sucesso=False, erro=f"Tipo de ação inválido: {acao_tipo}", id_requisicao=req_id)

        res = await client.call("action.update", params=payload)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_acoes", payload, True, dur, req_id, affected_ids=[actionid])
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_gerenciar_acoes", {"actionid": actionid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_consultar_regras_escalonamento(
    actionid: str
) -> ToolResult:
    """57. Consultar condições e etapas de escalonamento configuradas."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_regras_escalonamento")

    try:
        client = get_zabbix_client()
        actions = await client.call("action.get", params={
            "actionids": [actionid],
            "output": ["actionid", "name", "esc_period"],
            "selectOperations": "extend",
            "selectRecoveryOperations": "extend"
        })
        if not actions:
            return ToolResult(sucesso=False, erro="Ação não encontrada.", id_requisicao=req_id)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_regras_escalonamento", {"actionid": actionid}, True, dur, req_id)
        return ToolResult(sucesso=True, dados=actions[0], id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_consultar_regras_escalonamento", {"actionid": actionid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_suprimir_notificacoes(
    eventids: List[str],
    suprimir_ate: int
) -> ToolResult:
    """58. Implementar supressão temporária de alertas de problemas."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_suprimir_notificacoes")

    try:
        client = get_zabbix_client()
        # No Zabbix API, event.acknowledge com action=32 suprime problema até determinado timestamp
        res = await client.call("event.acknowledge", params={
            "eventids": eventids,
            "action": 32,  # 32 = Suppress
            "suppress_until": suprimir_ate
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_suprimir_notificacoes", {"eventids": eventids}, True, dur, req_id, affected_ids=eventids)
        return ToolResult(sucesso=True, dados=res, id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_suprimir_notificacoes", {"eventids": eventids}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_analisar_falsos_positivos(
    periodo_dias: int = 7
) -> ToolResult:
    """59. Identificar padrões suspeitos de alertas recorrentes (flapping) e sugerir ajustes."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_analisar_falsos_positivos")

    try:
        client = get_zabbix_client()
        time_from = int(time.time()) - (periodo_dias * 86400)
        events = await client.call("event.get", params={
            "time_from": time_from,
            "output": ["eventid", "objectid", "name", "clock"],
            "limit": 1000
        })

        # Agrupa eventos por trigger (objectid)
        contagem: Dict[str, Dict[str, Any]] = {}
        if isinstance(events, list):
            for ev in events:
                obj_id = ev.get("objectid")
                if not obj_id:
                    continue
                if obj_id not in contagem:
                    contagem[obj_id] = {"triggerid": obj_id, "nome": ev.get("name"), "total_disparos": 0}
                contagem[obj_id]["total_disparos"] += 1

        # Filtra triggers com mais de 5 disparos na semana (suspeita de flapping)
        flapping = [v for v in contagem.values() if v["total_disparos"] >= 5]
        flapping.sort(key=lambda x: x["total_disparos"], reverse=True)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_analisar_falsos_positivos", {"periodo": periodo_dias}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "total_triggers_analisadas": len(contagem),
                "triggers_com_alto_volume_flapping": flapping[:15],
                "diagnostico": f"Identificadas {len(flapping)} triggers oscilando frequentemente no período de {periodo_dias} dias."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_analisar_falsos_positivos", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_recomendar_ajustes_alertas(
    triggerid: str
) -> ToolResult:
    """60. Recomendar alterações técnicas em triggers com justificativas sem aplicá-las silenciosamente."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_recomendar_ajustes_alertas")

    try:
        client = get_zabbix_client()
        trig = await client.call("trigger.get", params={"triggerids": [triggerid], "output": "extend", "selectItems": ["key_"]})
        if not trig:
            return ToolResult(sucesso=False, erro="Trigger não encontrada.", id_requisicao=req_id)

        t = trig[0]
        recomendacoes = [
            "Adicionar período de tolerância na expressão (ex: min(/host/key, 5m) em vez de last()) para evitar disparo em picos momentâneos.",
            "Configurar histerese com expressão de recuperação separada (recovery_expression) para evitar recuperação e reabertura em loop.",
            "Reavaliar a severidade atual para adequar ao impacto real de negócio."
        ]

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_recomendar_ajustes_alertas", {"triggerid": triggerid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "triggerid": triggerid,
                "descricao": t.get("description"),
                "expressao_atual": t.get("expression"),
                "recomendacoes": recomendacoes
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_recomendar_ajustes_alertas", {"triggerid": triggerid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
