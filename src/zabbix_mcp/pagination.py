"""
Módulo de Utilitários de Paginação e Particionamento de Consultas.
Evita esgotamento de memória e timeouts em ambientes com milhares de hosts e eventos.
"""

from typing import Any, Dict, List, TypeVar

T = TypeVar("T")


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Divide uma lista em lotes menores de tamanho máximo chunk_size."""
    if chunk_size <= 0:
        return [items]
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def apply_pagination(params: Dict[str, Any], limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Aplica limit e offset aos parâmetros do Zabbix API JSON-RPC de forma segura."""
    p = dict(params)
    p["limit"] = max(1, min(limit, 1000))
    if offset > 0:
        p["offset"] = offset
    return p

