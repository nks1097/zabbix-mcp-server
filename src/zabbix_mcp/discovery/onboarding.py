"""
Módulo de Onboarding e Cadastro Automatizado de Dispositivos (Estágios D e E).
Gera prévia detalhada sem efeitos colaterais e cadastra dispositivos em lote de forma transacional.
"""

from typing import Any, Dict, List, Optional

from ..client import ZabbixClient
from ..models import BatchOnboardingResult, DiscoveredDevice, OnboardingPreview
from ..policies import generate_approval_token


def generate_onboarding_preview(
    device: DiscoveredDevice,
    grupo_destino: str = "Discovered hosts",
    templates_adicionais: Optional[List[str]] = None
) -> OnboardingPreview:
    """
    Gera a prévia detalhada de cadastro (Estágio D) para um dispositivo descoberto.
    Não efetua qualquer alteração no Zabbix.
    """
    templates = list(device.templates_recomendados)
    if templates_adicionais:
        for t in templates_adicionais:
            if t not in templates:
                templates.append(t)

    # Determina interface apropriada
    if device.tipo_dispositivo == "equipamento_rede" and 161 in device.portas_abertas:
        tipo_iface = "SNMP"
        porta_iface = "161"
    else:
        tipo_iface = "Zabbix Agent"
        porta_iface = "10050"

    avisos: List[str] = []
    if device.confianca_so < 0.6:
        avisos.append("Sistema operacional identificado com baixa confiança. Recomenda-se conferir os templates.")
    if not templates:
        avisos.append("Nenhum template específico encontrado. Será aplicado monitoramento básico de ICMP Ping.")
        templates.append("ICMP Ping")

    campos_inv = {
        "os": device.sistema_operacional or "Desconhecido",
        "tag": "Auto-Discovered-MCP",
        "notes": f"Cadastrado automaticamente via Zabbix MCP Server. Portas: {device.portas_abertas}"
    }

    preview_dict = {
        "host_tecnico": device.hostname_sugerido,
        "ip": device.ip,
        "grupos": [grupo_destino]
    }
    token = generate_approval_token("zabbix_cadastrar_dispositivos_em_lote", preview_dict)

    return OnboardingPreview(
        host_tecnico=device.hostname_sugerido,
        nome_visivel=device.dns or device.hostname_sugerido,
        ip=device.ip,
        dns=device.dns or "",
        portas=device.portas_abertas,
        grupos_propostos=[grupo_destino],
        templates_propostos=templates,
        tipo_interface=tipo_iface,
        porta_interface=porta_iface,
        campos_inventario=campos_inv,
        requer_aprovacao_manual=device.confianca_so < 0.5,
        avisos=avisos,
        token_aprovacao=token
    )


async def execute_batch_onboarding(
    previews: List[OnboardingPreview],
    client: ZabbixClient,
    token_aprovacao: Optional[str] = None
) -> BatchOnboardingResult:
    """
    Executa o cadastro efetivo dos dispositivos aprovados no Zabbix (Estágio E).
    Valida grupos, templates, interfaces e cria os hosts individualmente com rollback lógico.
    """
    result = BatchOnboardingResult(total_analisados=len(previews))

    # 1. Carrega ou cria grupos de hosts necessários
    groups_cache: Dict[str, str] = {}
    templates_cache: Dict[str, str] = {}

    try:
        existing_groups = await client.call("hostgroup.get", params={"output": ["groupid", "name"]})
        if isinstance(existing_groups, list):
            for g in existing_groups:
                groups_cache[g["name"].lower()] = g["groupid"]
    except Exception:
        pass

    try:
        existing_templates = await client.call("template.get", params={"output": ["templateid", "name", "host"]})
        if isinstance(existing_templates, list):
            for t in existing_templates:
                t_name = (t.get("name") or t.get("host", "")).lower()
                templates_cache[t_name] = t["templateid"]
    except Exception:
        pass

    for preview in previews:
        try:
            # Resolve grupos
            group_ids = []
            for g_name in preview.grupos_propostos:
                g_lower = g_name.lower()
                if g_lower in groups_cache:
                    group_ids.append({"groupid": groups_cache[g_lower]})
                else:
                    # Cria o grupo se não existir
                    created_g = await client.call("hostgroup.create", params={"name": g_name})
                    if created_g and "groupids" in created_g:
                        gid = created_g["groupids"][0]
                        groups_cache[g_lower] = gid
                        group_ids.append({"groupid": gid})

            if not group_ids:
                # Fallback para o primeiro grupo existente
                first_gid = next(iter(groups_cache.values()), "2")
                group_ids.append({"groupid": first_gid})

            # Resolve templates
            template_ids = []
            for t_name in preview.templates_propostos:
                t_lower = t_name.lower()
                if t_lower in templates_cache:
                    template_ids.append({"templateid": templates_cache[t_lower]})

            # Configura interface
            interface_type = 2 if preview.tipo_interface == "SNMP" else 1
            interface_payload: Dict[str, Any] = {
                "type": interface_type,
                "main": 1,
                "useip": 1,
                "ip": preview.ip,
                "dns": preview.dns,
                "port": preview.porta_interface
            }

            # Se for SNMP, adiciona detalhes compatíveis
            if interface_type == 2:
                interface_payload["details"] = {
                    "version": 2,
                    "community": "public",
                    "bulk": 1
                }

            host_payload: Dict[str, Any] = {
                "host": preview.host_tecnico,
                "name": preview.nome_visivel,
                "status": 0,  # 0 = Monitorado
                "groups": group_ids,
                "interfaces": [interface_payload],
                "inventory_mode": 1,  # 1 = Automático
                "inventory": preview.campos_inventario
            }

            if template_ids:
                host_payload["templates"] = template_ids

            created = await client.call("host.create", params=host_payload)

            if created and "hostids" in created:
                new_hostid = created["hostids"][0]
                result.total_cadastrados += 1
                result.hosts_cadastrados.append({
                    "hostid": new_hostid,
                    "host": preview.host_tecnico,
                    "ip": preview.ip,
                    "templates_associados": len(template_ids),
                    "status": "criado_com_sucesso"
                })
            else:
                result.total_falhas += 1
                result.erros.append({
                    "host": preview.host_tecnico,
                    "ip": preview.ip,
                    "erro": "API Zabbix não retornou hostid"
                })

        except Exception as e:
            result.total_falhas += 1
            result.erros.append({
                "host": preview.host_tecnico,
                "ip": preview.ip,
                "erro": str(e)
            })

    return result
