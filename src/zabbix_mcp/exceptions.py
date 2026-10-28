"""
Hierarquia de exceções especializadas do Zabbix MCP Server.
"""

from typing import Any, Dict, Optional


class ZabbixError(Exception):
    """Exceção base para erros do Zabbix MCP."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ZabbixAuthError(ZabbixError):
    """Falha de autenticação ou token inválido na API Zabbix."""
    pass


class ZabbixRPCError(ZabbixError):
    """Erro retornado pelo motor JSON-RPC 2.0 do Zabbix."""
    def __init__(self, code: int, message: str, data: Optional[str] = None):
        super().__init__(f"Zabbix JSON-RPC Error ({code}): {message}. Detalhes: {data}")
        self.code = code
        self.rpc_message = message
        self.data = data


class ZabbixNotFoundError(ZabbixError):
    """Recurso solicitado (host, item, trigger, template) não encontrado."""
    pass


class ZabbixPermissionError(ZabbixError):
    """Operação bloqueada pelo modo de autorização RBAC do MCP."""
    pass


class ZabbixValidationError(ZabbixError):
    """Falha na validação de parâmetros de entrada."""
    pass


class ZabbixApprovalRequiredError(ZabbixError):
    """Operação de alto impacto requer token de aprovação explícito."""
    pass


class ZabbixVersionCompatibilityError(ZabbixError):
    """Método ou parâmetro não suportado pela versão atual do Zabbix."""
    pass
