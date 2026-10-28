"""
Módulo de Descoberta Automática e Onboarding de Dispositivos para o Zabbix.
"""

from .deduplication import deduplicate_devices
from .fingerprinting import fingerprint_device, recommend_templates_for_device
from .onboarding import execute_batch_onboarding, generate_onboarding_preview
from .scanner import scan_network
from .verification import verify_onboarded_hosts

__all__ = [
    "scan_network",
    "fingerprint_device",
    "recommend_templates_for_device",
    "deduplicate_devices",
    "generate_onboarding_preview",
    "execute_batch_onboarding",
    "verify_onboarded_hosts",
]
