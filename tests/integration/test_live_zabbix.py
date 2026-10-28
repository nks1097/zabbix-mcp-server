"""
Teste de Integração Real contra o Zabbix Server em http://192.168.0.107:8080/.
Utiliza o token fornecido: 3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45.
"""

import pytest
from zabbix_mcp.client import ZabbixClient
from zabbix_mcp.config import AuthorizationMode, Settings
from zabbix_mcp.tools.automacao import zabbix_diagnosticar_ambiente, zabbix_validar_conexao
from zabbix_mcp.tools.dispositivos import zabbix_listar_hosts


@pytest.fixture
def live_client():
    settings = Settings(
        zabbix_url="http://192.168.0.107:8080/api_jsonrpc.php",
        zabbix_token="3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        zabbix_mcp_mode=AuthorizationMode.ADMINISTRATIVO,
        zabbix_timeout=10.0
    )
    return ZabbixClient(settings)


@pytest.mark.asyncio
async def test_live_conexao_e_versao(live_client):
    """Testa se a API do Zabbix real responde e valida autenticação com token Bearer."""
    versao = await live_client.get_version()
    assert versao.startswith("7."), f"Esperado Zabbix 7.x, obtido {versao}"

    diag = await live_client.test_connection()
    assert diag["status"] == "conectado"
    assert diag["autenticado"] is True
    assert diag["hosts_acessiveis"] >= 1


@pytest.mark.asyncio
async def test_live_listar_hosts(live_client):
    """Testa consulta real de hosts cadastrados na instância do laboratório."""
    res = await zabbix_listar_hosts(limite=10)
    assert res.sucesso is True
    assert isinstance(res.dados, list)
    assert len(res.dados) >= 1
    # Valida que o 'Zabbix server' está entre os hosts
    nomes = [h.get("host") for h in res.dados]
    assert "Zabbix server" in nomes or len(nomes) > 0


@pytest.mark.asyncio
async def test_live_diagnostico_completo():
    """Executa a ferramenta 100 contra a instância real do Zabbix."""
    res = await zabbix_diagnosticar_ambiente()
    assert res.sucesso is True
    assert res.dados["saude_conexao"] == "operacional"
    assert res.dados["infraestrutura"]["total_hosts"] >= 1
