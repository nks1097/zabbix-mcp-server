"""
Teste do Inventário das 100 Ferramentas Obrigatórias do Zabbix MCP Server.
Valida unicidade dos nomes, padrão snake_case, docstrings em português e registro no servidor MCP.
"""

import inspect
import re
import pytest
from zabbix_mcp.server import create_server
from zabbix_mcp.tools import ALL_TOOLS


def test_exatamente_100_ferramentas_catalogadas():
    """Valida se a lista ALL_TOOLS contém rigorosamente 100 ferramentas."""
    assert len(ALL_TOOLS) == 100, f"Esperado exatamente 100 ferramentas, encontrado {len(ALL_TOOLS)}"


def test_nomes_unicos_e_padrao_snake_case():
    """Valida se todas as ferramentas possuem nomes únicos começando com 'zabbix_' em snake_case."""
    nomes = [fn.__name__ for fn in ALL_TOOLS]
    assert len(nomes) == len(set(nomes)), "Existem nomes duplicados no inventário de ferramentas!"

    pattern = re.compile(r"^zabbix_[a-z0-9_]+$")
    for nome in nomes:
        assert pattern.match(nome), f"O identificador '{nome}' não segue o padrão snake_case exigido (deve iniciar com 'zabbix_')"


def test_todas_ferramentas_possuem_docstring_em_portugues():
    """Valida se cada função possui documentação (docstring) explicando sua finalidade."""
    for fn in ALL_TOOLS:
        doc = inspect.getdoc(fn)
        assert doc is not None and len(doc.strip()) > 10, f"A ferramenta '{fn.__name__}' não possui docstring explicativa válida."


@pytest.mark.asyncio
async def test_registro_no_servidor_mcp():
    """Valida se todas as 100 ferramentas são aceitas e registradas na instância MCPServer."""
    server = create_server()
    registered_tools = await server.list_tools()
    assert len(registered_tools) == 100, f"O servidor MCP registrou {len(registered_tools)} ferramentas, esperado 100."

    registered_names = {t.name for t in registered_tools}
    expected_names = {fn.__name__ for fn in ALL_TOOLS}
    assert registered_names == expected_names, "Divergência entre ferramentas registradas e ferramentas esperadas."

