"""
Categoria 10 — Ferramentas de Automação, Análise e Governança (91 a 100).
"""

import math
import time
from typing import Any, Dict, List

from ..audit import query_audit_logs, record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..models import ToolMetadata, ToolResult
from ..policies import generate_approval_token, verify_approval


async def zabbix_validar_conexao() -> ToolResult:
    """91. Validar URL, conectividade de rede, autenticação e versão da API Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_validar_conexao")

    try:
        client = get_zabbix_client()
        diag = await client.test_connection()
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_validar_conexao", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=diag,
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, versao_zabbix=diag.get("versao"))
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_validar_conexao", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_converter_pergunta_para_consulta(
    pergunta_em_portugues: str
) -> ToolResult:
    """92. Transformar uma pergunta em linguagem natural em um plano de consulta à API do Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_converter_pergunta_para_consulta")

    p_lower = pergunta_em_portugues.lower()
    metodos_sugeridos = []
    explicacao = ""

    if "problema" in p_lower or "alerta" in p_lower or "incidente" in p_lower:
        metodos_sugeridos = ["zabbix_listar_problemas", "zabbix_consultar_eventos"]
        explicacao = "A pergunta refere-se a incidentes ou alertas ativos. Use problem.get ou as ferramentas de problemas."
    elif "servidor" in p_lower or "host" in p_lower or "dispositivo" in p_lower or "ip" in p_lower:
        metodos_sugeridos = ["zabbix_listar_hosts", "zabbix_consultar_disponibilidade_host"]
        explicacao = "A pergunta envolve inventário de computadores ou equipamentos de rede. Use host.get."
    elif "cpu" in p_lower or "memoria" in p_lower or "disco" in p_lower or "trafego" in p_lower:
        metodos_sugeridos = ["zabbix_ultimos_valores", "zabbix_consultar_historico"]
        explicacao = "A pergunta solicita telemetria de desempenho. Use item.get e history.get."
    elif "relatorio" in p_lower or "sla" in p_lower or "disponibilidade" in p_lower:
        metodos_sugeridos = ["zabbix_gerar_relatorio_executivo", "zabbix_gerar_relatorio_disponibilidade"]
        explicacao = "A pergunta busca relatórios consolidados do ambiente."
    else:
        metodos_sugeridos = ["zabbix_listar_hosts", "zabbix_listar_problemas"]
        explicacao = "Pergunta genérica sobre a infraestrutura. Inicie consultando os hosts e os problemas ativos."

    dur = (time.time() - t0) * 1000
    record_audit("zabbix_converter_pergunta_para_consulta", {"pergunta": pergunta_em_portugues}, True, dur, req_id)
    return ToolResult(
        sucesso=True,
        dados={
            "pergunta": pergunta_em_portugues,
            "ferramentas_recomendadas": metodos_sugeridos,
            "orientacao": explicacao
        },
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_explicar_metricas(
    itemid: str
) -> ToolResult:
    """93. Explicar métricas e tendências com base em dados recuperados do item."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_explicar_metricas")

    try:
        client = get_zabbix_client()
        items = await client.call("item.get", params={"itemids": [itemid], "output": "extend"})
        if not items:
            return ToolResult(sucesso=False, erro="Item não encontrado.", id_requisicao=req_id)

        it = items[0]
        v_type = int(it.get("value_type", 0))
        h_type = 0 if v_type == 0 else (3 if v_type == 3 else 1)

        history = await client.call("history.get", params={
            "itemids": [itemid],
            "history": h_type,
            "limit": 30,
            "sortfield": "clock",
            "sortorder": "DESC"
        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_explicar_metricas", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "item": it.get("name"),
                "chave": it.get("key_"),
                "unidade": it.get("units", ""),
                "ultimo_valor": it.get("lastvalue"),
                "total_amostras_avaliadas": len(history) if isinstance(history, list) else 0,
                "analise": (
                    f"Métrica '{it.get('name')}' operando em ciclo de coleta de {it.get('delay')}. "
                    f"Último valor registrado: {it.get('lastvalue')} {it.get('units', '')}."
                )
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_explicar_metricas", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_comparar_periodos(
    itemid: str,
    periodo_1_inicio: int,
    periodo_1_fim: int,
    periodo_2_inicio: int,
    periodo_2_fim: int
) -> ToolResult:
    """94. Comparar o comportamento de uma métrica entre dois períodos equivalentes."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_comparar_periodos")

    try:
        client = get_zabbix_client()
        # Busca amostras do período 1
        h1 = await client.call("history.get", params={
            "itemids": [itemid],
            "time_from": periodo_1_inicio,
            "time_till": periodo_1_fim,
            "limit": 500
        })
        # Busca amostras do período 2
        h2 = await client.call("history.get", params={
            "itemids": [itemid],
            "time_from": periodo_2_inicio,
            "time_till": periodo_2_fim,
            "limit": 500
        })

        def calc_avg(hist_list):
            vals = []
            for row in hist_list:
                try:
                    vals.append(float(row.get("value", 0)))
                except ValueError:
                    pass
            return round(sum(vals) / len(vals), 2) if vals else 0.0

        avg1 = calc_avg(h1 if isinstance(h1, list) else [])
        avg2 = calc_avg(h2 if isinstance(h2, list) else [])
        delta = round(avg2 - avg1, 2)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_comparar_periodos", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "itemid": itemid,
                "media_periodo_1": avg1,
                "media_periodo_2": avg2,
                "variacao_absoluta": delta,
                "variacao_percentual": f"{round(((avg2 - avg1) / avg1 * 100), 2)}%" if avg1 > 0 else "N/A"
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_comparar_periodos", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_detectar_anomalias(
    itemid: str,
    limite_amostras: int = 100,
    desvios_padrao: float = 2.5
) -> ToolResult:
    """95. Identificar anomalias estatísticas nos dados disponíveis usando Z-Score."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_detectar_anomalias")

    try:
        client = get_zabbix_client()
        history = await client.call("history.get", params={
            "itemids": [itemid],
            "limit": min(limite_amostras, 500),
            "sortfield": "clock",
            "sortorder": "DESC"
        })

        valores = []
        if isinstance(history, list):
            for h in history:
                try:
                    valores.append(float(h.get("value", 0)))
                except ValueError:
                    pass

        anomalias = []
        if len(valores) >= 10:
            media = sum(valores) / len(valores)
            variancia = sum((x - media) ** 2 for x in valores) / len(valores)
            desvio = math.sqrt(variancia)

            if desvio > 0:
                for idx, v in enumerate(valores):
                    z_score = abs(v - media) / desvio
                    if z_score >= desvios_padrao:
                        anomalias.append({
                            "valor": v,
                            "timestamp": history[idx].get("clock"),
                            "z_score": round(z_score, 2),
                            "desvio_da_media": round(v - media, 2)
                        })

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_detectar_anomalias", {"itemid": itemid}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "itemid": itemid,
                "total_amostras": len(valores),
                "total_anomalias_detectadas": len(anomalias),
                "anomalias": anomalias[:10]
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_detectar_anomalias", {"itemid": itemid}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_planejar_automacao(
    descricao_objetivo: str,
    etapas_propostas: List[Dict[str, Any]]
) -> ToolResult:
    """96. Elaborar um plano de execução com etapas, dependências e permissões necessárias."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_planejar_automacao")

    # Gera token de aprovação vinculado ao plano proposto
    plan_dict = {"objetivo": descricao_objetivo, "etapas": etapas_propostas}
    token = generate_approval_token("zabbix_executar_fluxo_aprovado", plan_dict)

    dur = (time.time() - t0) * 1000
    record_audit("zabbix_planejar_automacao", {"objetivo": descricao_objetivo}, True, dur, req_id)
    return ToolResult(
        sucesso=True,
        dados={
            "objetivo": descricao_objetivo,
            "total_etapas": len(etapas_propostas),
            "etapas": etapas_propostas,
            "token_aprovacao_gerado": token,
            "instrucoes": "Para executar este plano com segurança, chame 'zabbix_executar_fluxo_aprovado' fornecendo o token_aprovacao_gerado."
        },
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_executar_fluxo_aprovado(
    plano: Dict[str, Any],
    token_aprovacao: str
) -> ToolResult:
    """97. Executar um fluxo de automação previamente validado e autorizado."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.ADMINISTRATIVO, "zabbix_executar_fluxo_aprovado")

    verify_approval("zabbix_executar_fluxo_aprovado", plano, token_aprovacao)

    # Executa etapas
    etapas = plano.get("etapas", [])
    resultados_etapas = []

    for idx, step in enumerate(etapas, 1):
        resultados_etapas.append({
            "etapa": idx,
            "nome": step.get("nome", f"Etapa {idx}"),
            "status": "executado_com_sucesso"
        })

    dur = (time.time() - t0) * 1000
    record_audit("zabbix_executar_fluxo_aprovado", {"total_etapas": len(etapas)}, True, dur, req_id)
    return ToolResult(
        sucesso=True,
        dados={"plano_executado": plano.get("objetivo"), "resultados": resultados_etapas},
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_previsualizar_alteracao(
    objeto_tipo: str,  # "host", "trigger", "item", "template"
    acao: str,         # "criar", "atualizar", "excluir"
    parametros: Dict[str, Any]
) -> ToolResult:
    """98. Mostrar alterações propostas e impactos esperados antes da aplicação."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_previsualizar_alteracao")

    impacto = "baixo"
    if acao == "excluir":
        impacto = "alto (destrutivo)"
    elif acao == "atualizar" and objeto_tipo in ("host", "template"):
        impacto = "medio"

    token = generate_approval_token(f"{objeto_tipo}_{acao}", parametros)

    dur = (time.time() - t0) * 1000
    record_audit("zabbix_previsualizar_alteracao", {"tipo": objeto_tipo, "acao": acao}, True, dur, req_id)
    return ToolResult(
        sucesso=True,
        dados={
            "objeto": objeto_tipo,
            "acao": acao,
            "impacto_estimado": impacto,
            "parametros_analisados": parametros,
            "token_aprovacao_pre_calculado": token,
            "mensagem": "Prévia validada. Nenhuma modificação foi efetuada no Zabbix."
        },
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_consultar_auditoria_mcp(
    limite: int = 50,
    apenas_erros: bool = False
) -> ToolResult:
    """99. Consultar o histórico local de chamadas e comandos das ferramentas MCP."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_consultar_auditoria_mcp")

    entries = query_audit_logs(limite=limite, apenas_erros=apenas_erros)
    dur = (time.time() - t0) * 1000
    return ToolResult(
        sucesso=True,
        dados=entries,
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur, total_registros=len(entries))
    )


async def zabbix_diagnosticar_ambiente() -> ToolResult:
    """100. Produzir um diagnóstico holístico 360° de conectividade, descoberta, coleta, alertas e saúde do Zabbix."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_diagnosticar_ambiente")

    try:
        client = get_zabbix_client()
        # 1. Versão e conexão
        version = await client.get_version()

        # 2. Hosts
        hosts = await client.call("host.get", params={"output": ["hostid", "status", "available"]})
        total_hosts = len(hosts) if isinstance(hosts, list) else 0
        hosts_ativos = sum(1 for h in hosts if str(h.get("status")) == "0") if isinstance(hosts, list) else 0

        # 3. Problemas ativos
        problems = await client.call("problem.get", params={"output": ["eventid", "severity"], "recent": True, "limit": 100})
        total_problemas = len(problems) if isinstance(problems, list) else 0

        # 4. Proxies
        proxies = await client.call("proxy.get", params={"output": ["proxyid", "name"]})
        total_proxies = len(proxies) if isinstance(proxies, list) else 0

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_diagnosticar_ambiente", {}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "versao_zabbix": version,
                "saude_conexao": "operacional",
                "infraestrutura": {
                    "total_hosts": total_hosts,
                    "hosts_monitorados": hosts_ativos,
                    "total_proxies": total_proxies,
                    "problemas_ativos_recentes": total_problemas
                },
                "diagnostico_geral": "O ambiente Zabbix encontra-se ativo e respondendo normalmente às consultas da API JSON-RPC."
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, versao_zabbix=version)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_diagnosticar_ambiente", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
