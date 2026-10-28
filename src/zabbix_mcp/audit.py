"""
Módulo de Auditoria Local das Ferramentas MCP.
Registra de forma imutável e estruturada cada chamada realizada pelo agente de IA.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .config import get_settings
from .security import redact_sensitive_data


def record_audit(
    tool_name: str,
    params: Dict[str, Any],
    success: bool,
    duration_ms: float,
    req_id: str,
    error: Optional[str] = None,
    affected_ids: Optional[List[str]] = None
) -> None:
    """Registra uma entrada no arquivo de auditoria em formato JSONL."""
    settings = get_settings()
    log_path = settings.zabbix_audit_log_path.resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "id_requisicao": req_id,
        "ferramenta": tool_name,
        "modo_mcp": settings.zabbix_mcp_mode.value,
        "parametros": redact_sensitive_data(params),
        "sucesso": success,
        "duracao_ms": round(duration_ms, 2),
        "erro": error,
        "ids_afetados": affected_ids or []
    }

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # Não falha a ferramenta se a escrita do log de auditoria falhar temporariamente
        pass


def query_audit_logs(
    limite: int = 50,
    ferramenta: Optional[str] = None,
    apenas_erros: bool = False
) -> List[Dict[str, Any]]:
    """Consulta os registros de auditoria mais recentes."""
    settings = get_settings()
    log_path = settings.zabbix_audit_log_path.resolve()
    if not log_path.exists():
        return []

    results = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if ferramenta and entry.get("ferramenta") != ferramenta:
                    continue
                if apenas_erros and entry.get("sucesso") is True:
                    continue
                results.append(entry)
                if len(results) >= limite:
                    break
    except Exception:
        pass

    return results
