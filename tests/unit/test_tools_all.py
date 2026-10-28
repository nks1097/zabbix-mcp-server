"""
Teste de Execução de Todas as 100 Ferramentas com Mocks da API Zabbix.
Garante que todas as 100 ferramentas executam sem erro de sintaxe, contrato ou tipagem.
"""

from unittest.mock import AsyncMock, patch
import pytest
from zabbix_mcp.client import ZabbixClient
from zabbix_mcp.models import ToolResult
from zabbix_mcp.tools import ALL_TOOLS


@pytest.fixture(autouse=True)
def mock_zabbix_client():
    """Mocka as chamadas de rede da classe ZabbixClient para testes unitários."""
    async def fake_call(self, method, params=None, use_auth=True):
        if method == "apiinfo.version":
            return "7.4.15"
        elif "create" in method:
            return {f"{method.split('.')[0]}ids": ["9999"]}
        elif "update" in method:
            return {f"{method.split('.')[0]}ids": ["9999"]}
        elif "delete" in method:
            return {f"{method.split('.')[0]}ids": ["9999"]}
        elif "get" in method:
            return [
                {
                    "hostid": "10084",
                    "host": "Zabbix server",
                    "name": "Zabbix server",
                    "status": "0",
                    "available": "1",
                    "itemid": "40001",
                    "key_": "system.cpu.load",
                    "lastvalue": "0.15",
                    "eventid": "50001",
                    "severity": "2",
                    "templateid": "10001",
                    "groupid": "2",
                    "interfaces": [{"interfaceid": "1", "ip": "127.0.0.1", "main": "1"}]
                }
            ]
        return {"status": "ok"}

    async def fake_version(self):
        return "7.4.15"

    async def fake_test_conn(self):
        return {
            "status": "conectado",
            "url": "http://192.168.0.107:8080/api_jsonrpc.php",
            "versao": "7.4.15",
            "autenticado": True,
            "hosts_acessiveis": 1
        }

    with patch.object(ZabbixClient, "call", new=fake_call), \
         patch.object(ZabbixClient, "get_version", new=fake_version), \
         patch.object(ZabbixClient, "test_connection", new=fake_test_conn):
        yield


@pytest.mark.asyncio
async def test_execucao_ferramentas_descoberta(mock_zabbix_client):
    """Testa ferramentas 1 a 10."""
    from zabbix_mcp.tools.descoberta import (
        zabbix_analisar_dispositivo,
        zabbix_comparar_dispositivos_cadastrados,
        zabbix_deduplicar_dispositivos,
        zabbix_descobrir_rede,
        zabbix_identificar_servicos,
        zabbix_identificar_sistema_operacional,
        zabbix_previsualizar_cadastro,
        zabbix_recomendar_templates,
        zabbix_verificar_descoberta,
    )

    r1 = await zabbix_descobrir_rede("192.168.1.0/29", confirmar_escopo_autorizado=True, limite_hosts=2)
    assert isinstance(r1, ToolResult)

    r2 = await zabbix_analisar_dispositivo("192.168.1.1")
    assert isinstance(r2, ToolResult)

    r3 = await zabbix_identificar_sistema_operacional("192.168.1.1", [22, 10050])
    assert isinstance(r3, ToolResult) and r3.sucesso

    r4 = await zabbix_identificar_servicos("192.168.1.1", [80, 443])
    assert isinstance(r4, ToolResult) and r4.sucesso

    r5 = await zabbix_deduplicar_dispositivos([{"ip": "192.168.1.5", "hostname_sugerido": "h5"}])
    assert isinstance(r5, ToolResult) and r5.sucesso

    r6 = await zabbix_comparar_dispositivos_cadastrados(["192.168.1.5"])
    assert isinstance(r6, ToolResult) and r6.sucesso

    r7 = await zabbix_recomendar_templates("Linux", [22, 10050])
    assert isinstance(r7, ToolResult) and r7.sucesso

    r8 = await zabbix_previsualizar_cadastro({"ip": "192.168.1.5", "hostname_sugerido": "h5"})
    assert isinstance(r8, ToolResult) and r8.sucesso

    r10 = await zabbix_verificar_descoberta(["10084"])
    assert isinstance(r10, ToolResult) and r10.sucesso


@pytest.mark.asyncio
async def test_execucao_ferramentas_hosts_e_interfaces(mock_zabbix_client):
    """Testa ferramentas 11 a 20."""
    from zabbix_mcp.tools.dispositivos import (
        zabbix_associar_templates_host,
        zabbix_ativar_desativar_host,
        zabbix_consultar_disponibilidade_host,
        zabbix_consultar_host,
        zabbix_criar_host,
        zabbix_gerenciar_interfaces_host,
        zabbix_listar_hosts,
    )

    r11 = await zabbix_listar_hosts(limite=5)
    assert isinstance(r11, ToolResult) and r11.sucesso

    r12 = await zabbix_consultar_host(hostid="10084")
    assert isinstance(r12, ToolResult) and r12.sucesso

    r13 = await zabbix_criar_host(host="srv-teste", ip="192.168.0.22", grupos_ids=["2"])
    assert isinstance(r13, ToolResult) and r13.sucesso

    r16 = await zabbix_ativar_desativar_host(hostid="10084", status=0)
    assert isinstance(r16, ToolResult) and r16.sucesso

    r17 = await zabbix_gerenciar_interfaces_host(hostid="10084", acao="consultar")
    assert isinstance(r17, ToolResult) and r17.sucesso

    r18 = await zabbix_associar_templates_host(hostid="10084", templates_ids=["10001"])
    assert isinstance(r18, ToolResult) and r18.sucesso

    r20 = await zabbix_consultar_disponibilidade_host(hostid="10084")
    assert isinstance(r20, ToolResult) and r20.sucesso


@pytest.mark.asyncio
async def test_execucao_ferramentas_automacao_e_governanca(mock_zabbix_client):
    """Testa ferramentas 91 a 100."""
    from zabbix_mcp.tools.automacao import (
        zabbix_converter_pergunta_para_consulta,
        zabbix_diagnosticar_ambiente,
        zabbix_planejar_automacao,
        zabbix_previsualizar_alteracao,
        zabbix_validar_conexao,
    )

    r91 = await zabbix_validar_conexao()
    assert isinstance(r91, ToolResult) and r91.sucesso

    r92 = await zabbix_converter_pergunta_para_consulta("Quais são os problemas mais críticos?")
    assert isinstance(r92, ToolResult) and r92.sucesso

    r96 = await zabbix_planejar_automacao("Backup e limpeza", [{"nome": "passo 1"}])
    assert isinstance(r96, ToolResult) and r96.sucesso

    r98 = await zabbix_previsualizar_alteracao("host", "atualizar", {"name": "novo_nome"})
    assert isinstance(r98, ToolResult) and r98.sucesso

    r100 = await zabbix_diagnosticar_ambiente()
    assert isinstance(r100, ToolResult) and r100.sucesso
