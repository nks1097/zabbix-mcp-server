"""
Testes Unitários de Segurança, RBAC, Tokens de Aprovação e Redação de Segredos.
"""

import pytest
from zabbix_mcp.authorization import AuthorizationMode, check_permission
from zabbix_mcp.config import get_settings
from zabbix_mcp.exceptions import ZabbixApprovalRequiredError, ZabbixPermissionError, ZabbixValidationError
from zabbix_mcp.policies import generate_approval_token, verify_approval
from zabbix_mcp.security import redact_sensitive_data, validate_cidr_or_ip


def test_redacao_dados_sensiveis():
    """Valida se senhas, tokens e chaves privadas são redigidos recursivamente."""
    dados = {
        "host": "servidor-01",
        "password": "MinhaSenhaSuperSecreta123",
        "snmp_community": "public-secret",
        "aninhado": {
            "token": "api_token_abc_xyz",
            "valor_normal": 42
        },
        "lista": [{"senha": "outra"}, {"ip": "192.168.0.10"}]
    }

    limpo = redact_sensitive_data(dados)
    assert limpo["password"] == "[REDACTED]"
    assert limpo["snmp_community"] == "[REDACTED]"
    assert limpo["aninhado"]["token"] == "[REDACTED]"
    assert limpo["aninhado"]["valor_normal"] == 42
    assert limpo["lista"][0]["senha"] == "[REDACTED]"
    assert limpo["lista"][1]["ip"] == "192.168.0.10"


def test_bloqueio_rbac_modo_somente_leitura():
    """Valida se modo somente_leitura bloqueia operações operacionais e administrativas."""
    settings = get_settings()
    settings.zabbix_mcp_mode = AuthorizationMode.SOMENTE_LEITURA

    # Operação de leitura deve passar
    check_permission(AuthorizationMode.SOMENTE_LEITURA, "zabbix_listar_hosts")

    # Operação de escrita/criação deve falhar
    with pytest.raises(ZabbixPermissionError):
        check_permission(AuthorizationMode.OPERACIONAL, "zabbix_criar_host")

    # Operação administrativa deve falhar
    with pytest.raises(ZabbixPermissionError):
        check_permission(AuthorizationMode.ADMINISTRATIVO, "zabbix_remover_host")


def test_aprovacao_dois_passos_validacao_token():
    """Valida a geração e verificação de tokens de aprovação em dois passos."""
    params = {"hostid": "10084"}
    action = "zabbix_remover_host"

    # Sem token deve levantar erro informando o token requerido
    with pytest.raises(ZabbixApprovalRequiredError):
        verify_approval(action, params, token=None)

    # Gera token válido
    token_valido = generate_approval_token(action, params)
    assert verify_approval(action, params, token=token_valido) is True

    # Se parâmetros mudarem, o token anterior DEVE ser invalidado
    params_alterados = {"hostid": "10085"}
    with pytest.raises(ZabbixApprovalRequiredError):
        verify_approval(action, params_alterados, token=token_valido)


def test_validacao_cidr_seguranca():
    """Valida restrições contra loopback e blocos excessivos."""
    # Loopback proibido
    with pytest.raises(ZabbixValidationError):
        validate_cidr_or_ip("127.0.0.1/32")

    # Bloco CIDR válido
    net = validate_cidr_or_ip("192.168.1.0/24")
    assert net.num_addresses == 256

    # Bloco excessivo (> 1024 IPs) proibido
    with pytest.raises(ZabbixValidationError):
        validate_cidr_or_ip("10.0.0.0/16")
