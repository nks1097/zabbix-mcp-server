"""
Módulo de Compatibilidade de Versões da API Zabbix.
Lida com diferenças estruturais entre Zabbix 6.0 LTS, 6.4, 7.0 LTS e 7.4.
"""

from typing import Optional, Tuple


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Converte string de versão '7.4.15' ou '6.0.28' em tupla de inteiros (7, 4, 15)."""
    clean = version_str.split("-")[0].split("rc")[0].split("alpha")[0].split("beta")[0].strip()
    parts = clean.split(".")
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (6, 0, 0)


def is_version_at_least(current_version: Optional[str], target_version: str) -> bool:
    """Verifica se current_version é maior ou igual a target_version."""
    if not current_version:
        return False
    return parse_version(current_version) >= parse_version(target_version)


class CompatibilityMatrix:
    """Matriz de capacidades suportadas por versão do Zabbix."""

    @staticmethod
    def requires_bearer_header(version: Optional[str]) -> bool:
        """Zabbix 7.0+ exige Authorization: Bearer <token> e proíbe auth no payload JSON."""
        return is_version_at_least(version, "7.0.0")

    @staticmethod
    def supports_user_roles(version: Optional[str]) -> bool:
        """Suporte a role.get (Zabbix 5.2+)."""
        return is_version_at_least(version, "5.2.0")

    @staticmethod
    def supports_sla_services(version: Optional[str]) -> bool:
        """Suporte à API moderna de sla.get (Zabbix 6.0+)."""
        return is_version_at_least(version, "6.0.0")

    @staticmethod
    def supports_proxy_groups(version: Optional[str]) -> bool:
        """Suporte a proxygroup.get (Zabbix 7.0+)."""
        return is_version_at_least(version, "7.0.0")

    @staticmethod
    def supports_ha_cluster(version: Optional[str]) -> bool:
        """Suporte a ha.get para nós de Alta Disponibilidade (Zabbix 6.0+)."""
        return is_version_at_least(version, "6.0.0")
