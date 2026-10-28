"""
Categoria 1 — Ferramentas de Descoberta Automática de Dispositivos (1 a 10).
"""

import time
from typing import Any, Dict, List, Optional

from ..audit import record_audit
from ..authorization import AuthorizationMode, check_permission
from ..client import get_zabbix_client
from ..discovery import (
    deduplicate_devices,
    execute_batch_onboarding,
    fingerprint_device,
    generate_onboarding_preview,
    recommend_templates_for_device,
    scan_network,
    verify_onboarded_hosts,
)
from ..models import DiscoveredDevice, OnboardingPreview, ToolMetadata, ToolResult


async def zabbix_descobrir_rede(
    faixa_cidr: str,
    confirmar_escopo_autorizado: bool = False,
    portas: Optional[List[int]] = None,
    limite_hosts: int = 64
) -> ToolResult:
    """1. Descobrir dispositivos em uma faixa de rede explicitamente autorizada."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_descobrir_rede")

    try:
        devices = await scan_network(
            network_cidr=faixa_cidr,
            confirmar_escopo_autorizado=confirmar_escopo_autorizado,
            ports=portas,
            max_hosts=limite_hosts
        )
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_descobrir_rede", {"faixa": faixa_cidr}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=[d.model_dump() for d in devices],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=len(devices))
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_descobrir_rede", {"faixa": faixa_cidr}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_analisar_dispositivo(
    ip: str,
    portas: Optional[List[int]] = None
) -> ToolResult:
    """2. Analisar endereço IP, DNS, portas permitidas e evidências de identificação."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_analisar_dispositivo")

    try:
        from ..discovery.scanner import scan_single_host
        check_ports = portas or [22, 80, 443, 161, 3389, 445, 10050, 3306, 5432]
        dev = await scan_single_host(ip, check_ports)
        if not dev:
            dur = (time.time() - t0) * 1000
            return ToolResult(
                sucesso=True,
                dados=None,
                avisos=[f"O IP {ip} não respondeu nas portas verificadas."],
                id_requisicao=req_id,
                metadados=ToolMetadata(duracao_ms=dur)
            )

        dev = fingerprint_device(dev)
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_analisar_dispositivo", {"ip": ip}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=dev.model_dump(),
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_analisar_dispositivo", {"ip": ip}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_identificar_sistema_operacional(
    ip: str,
    portas_abertas: List[int]
) -> ToolResult:
    """3. Inferir o sistema operacional a partir de dados confiáveis, indicando o grau de confiança."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_identificar_sistema_operacional")

    dev = DiscoveredDevice(ip=ip, hostname_sugerido=f"host-{ip}", portas_abertas=portas_abertas)
    dev = fingerprint_device(dev)
    dur = (time.time() - t0) * 1000
    record_audit("zabbix_identificar_sistema_operacional", {"ip": ip}, True, dur, req_id)

    return ToolResult(
        sucesso=True,
        dados={
            "ip": ip,
            "sistema_operacional": dev.sistema_operacional,
            "confianca": dev.confianca_so,
            "tipo_dispositivo": dev.tipo_dispositivo,
            "portas_evidencia": dev.portas_abertas
        },
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_identificar_servicos(
    ip: str,
    portas_abertas: List[int]
) -> ToolResult:
    """4. Identificar serviços monitoráveis usando métodos autorizados e não intrusivos."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_identificar_servicos")

    dev = DiscoveredDevice(ip=ip, hostname_sugerido=f"host-{ip}", portas_abertas=portas_abertas)
    dev = fingerprint_device(dev)
    dur = (time.time() - t0) * 1000
    record_audit("zabbix_identificar_servicos", {"ip": ip}, True, dur, req_id)

    return ToolResult(
        sucesso=True,
        dados={
            "ip": ip,
            "servicos_detectados": dev.servicos_detectados,
            "total_servicos": len(dev.servicos_detectados)
        },
        id_requisicao=req_id,
        metadados=ToolMetadata(duracao_ms=dur)
    )


async def zabbix_deduplicar_dispositivos(
    dispositivos: List[Dict[str, Any]]
) -> ToolResult:
    """5. Identificar possíveis duplicidades entre dispositivos descobertos e hosts existentes."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_deduplicar_dispositivos")

    try:
        client = get_zabbix_client()
        existing_hosts = await client.call("host.get", params={
            "output": ["hostid", "host", "name"],
            "selectInterfaces": ["ip", "dns"]
        })

        dev_objs = [DiscoveredDevice(**d) for d in dispositivos]
        novos, duplicados = deduplicate_devices(dev_objs, existing_hosts if isinstance(existing_hosts, list) else [])

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_deduplicar_dispositivos", {"total": len(dispositivos)}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "total_novos": len(novos),
                "total_duplicados": len(duplicados),
                "dispositivos_novos": [d.model_dump() for d in novos],
                "dispositivos_duplicados": [d.model_dump() for d in duplicados]
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_deduplicar_dispositivos", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_comparar_dispositivos_cadastrados(
    ips_descobertos: List[str]
) -> ToolResult:
    """6. Comparar a descoberta com o inventário atual."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_comparar_dispositivos_cadastrados")

    try:
        client = get_zabbix_client()
        hosts = await client.call("host.get", params={
            "output": ["hostid", "host", "name", "status"],
            "selectInterfaces": ["ip", "dns", "type"]
        })

        registered_ips: Dict[str, Dict[str, Any]] = {}
        if isinstance(hosts, list):
            for h in hosts:
                for iface in h.get("interfaces", []):
                    if iface.get("ip"):
                        registered_ips[iface["ip"]] = h

        cadastrados = []
        nao_cadastrados = []

        for ip in ips_descobertos:
            if ip in registered_ips:
                cadastrados.append({
                    "ip": ip,
                    "hostid": registered_ips[ip].get("hostid"),
                    "host": registered_ips[ip].get("host"),
                    "nome": registered_ips[ip].get("name")
                })
            else:
                nao_cadastrados.append(ip)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_comparar_dispositivos_cadastrados", {"total_ips": len(ips_descobertos)}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "total_comparados": len(ips_descobertos),
                "total_ja_cadastrados": len(cadastrados),
                "total_nao_cadastrados": len(nao_cadastrados),
                "cadastrados": cadastrados,
                "nao_cadastrados": nao_cadastrados
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_comparar_dispositivos_cadastrados", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_recomendar_templates(
    sistema_operacional: str,
    portas_abertas: List[int],
    tipo_dispositivo: str = "generico"
) -> ToolResult:
    """7. Recomendar templates conforme sistema operacional, serviços e compatibilidade."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_recomendar_templates")

    try:
        client = get_zabbix_client()
        templates = await client.call("template.get", params={"output": ["templateid", "name", "host"]})

        dev = DiscoveredDevice(
            ip="127.0.0.1",
            hostname_sugerido="temp",
            sistema_operacional=sistema_operacional,
            tipo_dispositivo=tipo_dispositivo,
            portas_abertas=portas_abertas
        )
        rec = recommend_templates_for_device(dev, templates if isinstance(templates, list) else [])

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_recomendar_templates", {"so": sistema_operacional}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados={
                "templates_recomendados": rec,
                "total_recomendados": len(rec),
                "criterio": f"SO: {sistema_operacional}, Portas: {portas_abertas}"
            },
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_recomendar_templates", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_previsualizar_cadastro(
    dispositivo: Dict[str, Any],
    grupo_destino: str = "Discovered hosts",
    templates: Optional[List[str]] = None
) -> ToolResult:
    """8. Apresentar todos os parâmetros propostos para cadastrar um dispositivo sem efetuar alterações."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_previsualizar_cadastro")

    try:
        dev_obj = DiscoveredDevice(**dispositivo)
        preview = generate_onboarding_preview(dev_obj, grupo_destino, templates)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_previsualizar_cadastro", {"ip": dev_obj.ip}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=preview.model_dump(),
            avisos=preview.avisos,
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_previsualizar_cadastro", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_cadastrar_dispositivos_em_lote(
    previsoes: List[Dict[str, Any]],
    token_aprovacao: Optional[str] = None
) -> ToolResult:
    """9. Cadastrar vários dispositivos aprovados, com validação individual e relatório de resultados."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.OPERACIONAL, "zabbix_cadastrar_dispositivos_em_lote")

    try:
        client = get_zabbix_client()
        preview_objs = [OnboardingPreview(**p) for p in previsoes]

        res = await execute_batch_onboarding(preview_objs, client, token_aprovacao)
        dur = (time.time() - t0) * 1000

        affected = [h["hostid"] for h in res.hosts_cadastrados if "hostid" in h]
        record_audit("zabbix_cadastrar_dispositivos_em_lote", {"total": len(previsoes)}, True, dur, req_id, affected_ids=affected)

        return ToolResult(
            sucesso=res.total_falhas == 0,
            dados=res.model_dump(),
            avisos=[f"{res.total_falhas} falhas durante o onboarding"] if res.total_falhas > 0 else [],
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur, total_registros=res.total_cadastrados)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_cadastrar_dispositivos_em_lote", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))


async def zabbix_verificar_descoberta(
    hostids: List[str]
) -> ToolResult:
    """10. Verificar o resultado da descoberta, identificando falhas, duplicidades e dispositivos não resolvidos."""
    t0 = time.time()
    req_id = ToolResult(sucesso=True).id_requisicao
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_verificar_descoberta")

    try:
        client = get_zabbix_client()
        verif = await verify_onboarded_hosts(hostids, client)

        dur = (time.time() - t0) * 1000
        record_audit("zabbix_verificar_descoberta", {"total_hosts": len(hostids)}, True, dur, req_id)
        return ToolResult(
            sucesso=True,
            dados=verif,
            id_requisicao=req_id,
            metadados=ToolMetadata(duracao_ms=dur)
        )
    except Exception as e:
        dur = (time.time() - t0) * 1000
        record_audit("zabbix_verificar_descoberta", {}, False, dur, req_id, error=str(e))
        return ToolResult(sucesso=False, erro=str(e), id_requisicao=req_id, metadados=ToolMetadata(duracao_ms=dur))
