"""
Módulo de Segurança e Higienização de Dados.
Implementa proteção contra vazamento de credenciais, validação de escopos de rede e proteção SSRF/Path Traversal.
"""

import ipaddress
import re
from pathlib import Path
from typing import Any, Set

from .exceptions import ZabbixValidationError

SENSITIVE_KEYS: Set[str] = {
    "password", "senha", "token", "auth", "secret", "privatekey",
    "snmpv3_authpassphrase", "snmpv3_privpassphrase", "community",
    "apikey", "sessionid", "authtoken", "key"
}


def redact_sensitive_data(obj: Any) -> Any:
    """Substitui valores confidenciais por '[REDACTED]' recursivamente."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if any(s in k_lower for s in SENSITIVE_KEYS):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_sensitive_data(v)
        return cleaned
    elif isinstance(obj, list):
        return [redact_sensitive_data(item) for item in obj]
    return obj


def validate_cidr_or_ip(target: str, allow_public: bool = False) -> ipaddress.IPv4Network:
    """
    Valida se uma string é um IP ou CIDR válido.
    Por padrão, protege contra escopos de rede perigosos (Loopback, Multicast, Link-Local).
    """
    target = target.strip()
    try:
        if "/" in target:
            net = ipaddress.IPv4Network(target, strict=False)
        else:
            ip = ipaddress.IPv4Address(target)
            net = ipaddress.IPv4Network(f"{ip}/32")
    except ValueError as e:
        raise ZabbixValidationError(f"Endereço IP ou bloco CIDR inválido: '{target}'. Detalhe: {str(e)}")

    # Bloqueios de segurança
    if net.is_loopback:
        raise ZabbixValidationError(f"Varredura em rede de loopback ({target}) é proibida por segurança.")
    if net.is_multicast:
        raise ZabbixValidationError(f"Endereço de multicast ({target}) não é válido para varredura de hosts.")
    if net.is_reserved:
        raise ZabbixValidationError(f"Rede reservada ({target}) não é válida para varredura.")

    # Limite máximo de hosts por varredura para evitar negação de serviço
    if net.num_addresses > 1024:
        raise ZabbixValidationError(
            f"O bloco {target} contém {net.num_addresses} endereços. O limite máximo seguro por varredura é 1024 IPs."
        )

    return net


def safe_report_path(base_dir: Path, filename: str) -> Path:
    """
    Garante que o caminho do arquivo gerado fique estritamente dentro do diretório de relatórios permitido.
    Previne ataques de Path Traversal (e.g., ../../../etc/passwd).
    """
    base_dir = base_dir.resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    # Sanitiza o nome do arquivo removendo caracteres perigosos
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    target_path = (base_dir / safe_name).resolve()

    if not str(target_path).startswith(str(base_dir)):
        raise ZabbixValidationError(f"Tentativa de acesso a caminho não autorizado: {filename}")

    return target_path
