"""
Fixtures e configurações para testes unitários e de integração do Zabbix MCP Server.
"""

from pathlib import Path
import sys
import pytest

# Adiciona o diretório src ao path de importação
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

from zabbix_mcp.config import AuthorizationMode, Settings, reset_settings


@pytest.fixture(autouse=True)
def configure_test_settings(tmp_path):
    """Configura ambiente de teste isolado para cada execução."""
    test_reports = tmp_path / "test_reports"
    test_audit = tmp_path / "test_audit.jsonl"

    settings = Settings(
        zabbix_url="http://192.168.0.107:8080/api_jsonrpc.php",
        zabbix_token="3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        zabbix_mcp_mode=AuthorizationMode.ADMINISTRATIVO,
        zabbix_require_approval_destructive=True,
        zabbix_reports_dir=test_reports,
        zabbix_audit_log_path=test_audit,
        zabbix_timeout=5.0
    )
    reset_settings(settings)
    yield settings
    reset_settings(None)
