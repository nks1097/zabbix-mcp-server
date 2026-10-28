"""
Módulo de Identificação e Fingerprinting de Dispositivos e Serviços.
Infere sistema operacional, tipos de dispositivos e recomenda templates adequados.
"""

from typing import Any, Dict, List

from ..models import DiscoveredDevice


def fingerprint_device(device: DiscoveredDevice) -> DiscoveredDevice:
    """
    Analisa portas abertas e metadados para inferir Sistema Operacional,
    serviços e tipo de dispositivo com grau de confiança documentado.
    """
    ports = set(device.portas_abertas)
    services: List[str] = []

    # Detecção de serviços
    if 10050 in ports:
        services.append("Zabbix Agent (TCP 10050)")
    if 161 in ports:
        services.append("SNMP (UDP/TCP 161)")
    if 22 in ports:
        services.append("SSH (TCP 22)")
    if 3389 in ports:
        services.append("RDP (TCP 3389)")
    if 445 in ports:
        services.append("SMB (TCP 445)")
    if 80 in ports:
        services.append("HTTP (TCP 80)")
    if 443 in ports:
        services.append("HTTPS (TCP 443)")
    if 3306 in ports:
        services.append("MySQL/MariaDB (TCP 3306)")
    if 5432 in ports:
        services.append("PostgreSQL (TCP 5432)")

    device.servicos_detectados = services

    # Inferência de Sistema Operacional e Tipo de Dispositivo
    if 3389 in ports or 445 in ports:
        device.sistema_operacional = "Windows Server / Desktop"
        device.confianca_so = 0.85
        device.tipo_dispositivo = "servidor_windows"
    elif 22 in ports and 3389 not in ports:
        if 161 in ports and 10050 not in ports:
            device.sistema_operacional = "Network OS / Linux Appliance"
            device.confianca_so = 0.70
            device.tipo_dispositivo = "equipamento_rede"
        else:
            device.sistema_operacional = "Linux / Unix"
            device.confianca_so = 0.80
            device.tipo_dispositivo = "servidor_linux"
    elif 161 in ports and not (ports & {22, 3389, 445, 10050}):
        device.sistema_operacional = "Network Equipment Firmware (SNMP)"
        device.confianca_so = 0.75
        device.tipo_dispositivo = "equipamento_rede"
    elif 80 in ports or 443 in ports:
        device.sistema_operacional = "Servidor Web / Appliance"
        device.confianca_so = 0.50
        device.tipo_dispositivo = "servico_web"
    else:
        device.sistema_operacional = "Não identificado com precisão"
        device.confianca_so = 0.20
        device.tipo_dispositivo = "generico"

    return device


def recommend_templates_for_device(
    device: DiscoveredDevice,
    available_templates: List[Dict[str, Any]]
) -> List[str]:
    """
    Recomenda templates Zabbix compatíveis com base no SO e serviços detectados.
    Cruza com os templates efetivamente instalados no Zabbix Server.
    """
    names_to_recommend: List[str] = []
    ports = set(device.portas_abertas)

    # 1. Templates de Agente / SO
    if device.tipo_dispositivo == "servidor_linux":
        names_to_recommend.extend([
            "Linux by Zabbix agent",
            "Linux by Zabbix agent active",
            "ICMP Ping"
        ])
    elif device.tipo_dispositivo == "servidor_windows":
        names_to_recommend.extend([
            "Windows by Zabbix agent",
            "Windows by Zabbix agent active",
            "ICMP Ping"
        ])
    elif device.tipo_dispositivo == "equipamento_rede":
        names_to_recommend.extend([
            "Generic by SNMP",
            "Network Generic Device by SNMP",
            "ICMP Ping"
        ])
    else:
        names_to_recommend.append("ICMP Ping")

    # 2. Templates de Serviços Adicionais
    if 3306 in ports:
        names_to_recommend.append("MySQL by Zabbix agent 2")
    if 5432 in ports:
        names_to_recommend.append("PostgreSQL by Zabbix agent 2")
    if 80 in ports or 443 in ports:
        names_to_recommend.append("Website certificate by Zabbix agent 2")

    # Filtra pelos templates reais existentes no Zabbix se disponíveis
    if available_templates:
        existing_names = {t.get("name") or t.get("host"): t for t in available_templates}
        matched = [name for name in names_to_recommend if name in existing_names]
        # Se nenhum coincidir exatamente, sugere ao menos ICMP Ping ou o genérico correspondente
        if not matched:
            for t_name in existing_names:
                if "ping" in t_name.lower() or "icmp" in t_name.lower():
                    matched.append(t_name)
                    break
        return matched or names_to_recommend

    return names_to_recommend
