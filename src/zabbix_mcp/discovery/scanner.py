"""
Módulo de Varredura de Rede Não Intrusiva.
Executa descoberta controlada de dispositivos em faixas CIDR expressamente autorizadas.
"""

import asyncio
import socket
from typing import List, Optional

from ..exceptions import ZabbixValidationError
from ..models import DiscoveredDevice
from ..security import validate_cidr_or_ip

DEFAULT_MONITORING_PORTS = [
    22,    # SSH (Linux/Unix/Network)
    80,    # HTTP
    443,   # HTTPS
    161,   # SNMP
    3389,  # RDP (Windows)
    445,   # SMB (Windows)
    10050, # Zabbix Agent
    10051, # Zabbix Server/Proxy
    3306,  # MySQL / MariaDB
    5432,  # PostgreSQL
]


async def probe_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """Verifica se uma porta TCP responde dentro do timeout especificado."""
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, OSError):
        return False


async def resolve_reverse_dns(ip: str) -> Optional[str]:
    """Tenta obter o nome DNS reverso do endereço IP de forma assíncrona."""
    loop = asyncio.get_running_loop()
    try:
        info = await asyncio.wait_for(
            loop.run_in_executor(None, socket.gethostbyaddr, ip),
            timeout=1.5
        )
        return info[0] if info else None
    except Exception:
        return None


async def scan_single_host(
    ip: str,
    ports_to_check: List[int],
    timeout_per_port: float = 1.0
) -> Optional[DiscoveredDevice]:
    """Varre portas selecionadas em um único IP e extrai informações básicas."""
    tasks = [probe_port(ip, p, timeout=timeout_per_port) for p in ports_to_check]
    results = await asyncio.gather(*tasks)

    open_ports = [port for port, is_open in zip(ports_to_check, results) if is_open]

    # Se nenhuma porta respondeu, considera o host inativo
    if not open_ports:
        return None

    dns_name = await resolve_reverse_dns(ip)
    hostname = dns_name or f"host-{ip.replace('.', '-')}"

    return DiscoveredDevice(
        ip=ip,
        dns=dns_name,
        hostname_sugerido=hostname,
        portas_abertas=open_ports,
        tipo_dispositivo="indefinido"
    )


async def scan_network(
    network_cidr: str,
    confirmar_escopo_autorizado: bool,
    ports: Optional[List[int]] = None,
    max_hosts: int = 128,
    timeout_per_port: float = 0.8
) -> List[DiscoveredDevice]:
    """
    Varre um escopo de rede autorizado procurando dispositivos ativos.
    Exige confirmação explícita de autorização para prevenir varreduras não autorizadas.
    """
    if not confirmar_escopo_autorizado:
        raise ZabbixValidationError(
            "A varredura de rede requer confirmação explícita. "
            "Defina 'confirmar_escopo_autorizado=True' após certificar-se de possuir autorização formal."
        )

    net = validate_cidr_or_ip(network_cidr)
    check_ports = ports or DEFAULT_MONITORING_PORTS

    # Gera lista de IPs para verificação
    hosts = [str(h) for h in net.hosts()][:max_hosts]
    if not hosts and net.num_addresses == 1:
        hosts = [str(net.network_address)]

    # Executa varredura com semáforo de taxa para não saturar a rede
    semaphore = asyncio.Semaphore(20)

    async def _bounded_scan(ip_addr: str):
        async with semaphore:
            return await scan_single_host(ip_addr, check_ports, timeout_per_port)

    discovered = await asyncio.gather(*[_bounded_scan(ip) for ip in hosts])
    return [d for d in discovered if d is not None]
