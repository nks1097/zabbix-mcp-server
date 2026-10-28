"""
Testes Unitários da Automação de Descoberta, Fingerprinting, Deduplicação e Onboarding.
"""

from zabbix_mcp.discovery.deduplication import deduplicate_devices
from zabbix_mcp.discovery.fingerprinting import fingerprint_device, recommend_templates_for_device
from zabbix_mcp.discovery.onboarding import generate_onboarding_preview
from zabbix_mcp.models import DiscoveredDevice


def test_fingerprinting_linux():
    """Valida inferência de SO Linux e agente."""
    dev = DiscoveredDevice(
        ip="192.168.0.50",
        hostname_sugerido="srv-linux-01",
        portas_abertas=[22, 10050]
    )
    dev = fingerprint_device(dev)

    assert dev.tipo_dispositivo == "servidor_linux"
    assert "Linux" in dev.sistema_operacional
    assert dev.confianca_so >= 0.8
    assert "Zabbix Agent (TCP 10050)" in dev.servicos_detectados


def test_fingerprinting_windows():
    """Valida inferência de SO Windows."""
    dev = DiscoveredDevice(
        ip="192.168.0.60",
        hostname_sugerido="srv-win-01",
        portas_abertas=[3389, 445, 10050]
    )
    dev = fingerprint_device(dev)

    assert dev.tipo_dispositivo == "servidor_windows"
    assert "Windows" in dev.sistema_operacional
    assert dev.confianca_so >= 0.8


def test_deduplicacao_por_ip_e_nome():
    """Valida identificação de duplicidades contra o inventário existente."""
    existing_hosts = [
        {
            "hostid": "101",
            "host": "servidor-linux-prod",
            "name": "Servidor Linux Produção",
            "interfaces": [{"ip": "192.168.0.100", "dns": "linux.local"}]
        }
    ]

    discovered = [
        # Dispositivo 1: IP duplicado
        DiscoveredDevice(ip="192.168.0.100", hostname_sugerido="novo-srv"),
        # Dispositivo 2: Nome duplicado
        DiscoveredDevice(ip="192.168.0.101", hostname_sugerido="servidor-linux-prod"),
        # Dispositivo 3: Totalmente novo
        DiscoveredDevice(ip="192.168.0.102", hostname_sugerido="srv-novo-inedito")
    ]

    novos, duplicados = deduplicate_devices(discovered, existing_hosts)

    assert len(novos) == 1
    assert novos[0].ip == "192.168.0.102"
    assert len(duplicados) == 2
    assert duplicados[0].duplicidade_detectada is True


def test_geracao_previa_onboarding():
    """Valida se a prévia de cadastro contém campos e token de aprovação."""
    dev = DiscoveredDevice(
        ip="192.168.0.200",
        hostname_sugerido="switch-core",
        portas_abertas=[161],
        tipo_dispositivo="equipamento_rede",
        templates_recomendados=["Generic by SNMP"]
    )

    preview = generate_onboarding_preview(dev, grupo_destino="Switches Core")

    assert preview.host_tecnico == "switch-core"
    assert preview.tipo_interface == "SNMP"
    assert preview.porta_interface == "161"
    assert "Generic by SNMP" in preview.templates_propostos
    assert preview.token_aprovacao is not None
    assert preview.token_aprovacao.startswith("apr_")
