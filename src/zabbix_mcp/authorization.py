"""
Módulo de Controle de Acesso Baseado em Funções (RBAC) do Zabbix MCP.
Garante o princípio do menor privilégio através dos modos: somente_leitura, operacional e administrativo.
"""

from functools import wraps
from typing import Any, Callable

from .config import AuthorizationMode, get_settings
from .exceptions import ZabbixPermissionError

MODE_HIERARCHY = {
    AuthorizationMode.SOMENTE_LEITURA: 1,
    AuthorizationMode.OPERACIONAL: 2,
    AuthorizationMode.ADMINISTRATIVO: 3,
}


def check_permission(required_mode: AuthorizationMode, action_name: str = "") -> None:
    """Verifica se o modo atual do servidor MCP satisfaz o nível requerido."""
    settings = get_settings()
    current_level = MODE_HIERARCHY.get(settings.zabbix_mcp_mode, 1)
    required_level = MODE_HIERARCHY.get(required_mode, 1)

    if current_level < required_level:
        raise ZabbixPermissionError(
            f"Operação '{action_name}' bloqueada. O servidor MCP está operando no modo '{settings.zabbix_mcp_mode.value}', "
            f"mas esta ação requer permissão mínima '{required_mode.value}'."
        )


def require_permission(required_mode: AuthorizationMode):
    """Decorator para aplicar verificação de permissão em ferramentas MCP."""
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            check_permission(required_mode, func.__name__)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
