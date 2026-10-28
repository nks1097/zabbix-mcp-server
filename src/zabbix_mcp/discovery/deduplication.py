"""
Módulo de Reconciliação e Deduplicação de Dispositivos.
Garante que dispositivos já cadastrados não sejam duplicados silenciosamente no Zabbix.
"""

from typing import Any, Dict, List, Tuple

from ..models import DiscoveredDevice


def deduplicate_devices(
    discovered: List[DiscoveredDevice],
    existing_hosts: List[Dict[str, Any]]
) -> Tuple[List[DiscoveredDevice], List[DiscoveredDevice]]:
    """
    Compara os dispositivos descobertos com os hosts já cadastrados no Zabbix.
    Identifica duplicidades por IP de interface, nome técnico ou DNS reverso.
    Retorna uma tupla: (dispositivos_novos, dispositivos_duplicados).
    """
    # Mapeamentos rápidos de hosts existentes
    ip_to_host: Dict[str, Dict[str, Any]] = {}
    name_to_host: Dict[str, Dict[str, Any]] = {}

    for h in existing_hosts:
        tech_name = str(h.get("host", "")).lower()
        vis_name = str(h.get("name", "")).lower()

        name_to_host[tech_name] = h
        if vis_name:
            name_to_host[vis_name] = h

        # Interfaces do host
        for iface in h.get("interfaces", []):
            iface_ip = iface.get("ip")
            iface_dns = str(iface.get("dns", "")).lower()
            if iface_ip:
                ip_to_host[iface_ip] = h
            if iface_dns:
                name_to_host[iface_dns] = h

    novos: List[DiscoveredDevice] = []
    duplicados: List[DiscoveredDevice] = []

    for dev in discovered:
        # 1. Verifica se o IP já existe em alguma interface do Zabbix
        if dev.ip in ip_to_host:
            existing = ip_to_host[dev.ip]
            dev.duplicidade_detectada = True
            dev.hostid_existente = str(existing.get("hostid"))
            dev.motivo_duplicidade = f"IP {dev.ip} já cadastrado no host '{existing.get('name') or existing.get('host')}' (ID {dev.hostid_existente})"
            duplicados.append(dev)
            continue

        # 2. Verifica se o hostname sugerido ou DNS já existe
        dev_host_lower = dev.hostname_sugerido.lower()
        dev_dns_lower = (dev.dns or "").lower()

        matched_host = None
        if dev_host_lower in name_to_host:
            matched_host = name_to_host[dev_host_lower]
        elif dev_dns_lower and dev_dns_lower in name_to_host:
            matched_host = name_to_host[dev_dns_lower]

        if matched_host:
            dev.duplicidade_detectada = True
            dev.hostid_existente = str(matched_host.get("hostid"))
            dev.motivo_duplicidade = f"Nome '{dev.hostname_sugerido}' conflita com o host existente '{matched_host.get('name') or matched_host.get('host')}' (ID {dev.hostid_existente})"
            duplicados.append(dev)
            continue

        dev.duplicidade_detectada = False
        novos.append(dev)

    return novos, duplicados
