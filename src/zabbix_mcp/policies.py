"""
Módulo de Políticas de Confirmação e Tokens de Aprovação em Dois Passos.
Garante que operações críticas ou destrutivas não sejam executadas sem aprovação explícita vinculada aos parâmetros.
"""

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

from .config import get_settings
from .exceptions import ZabbixApprovalRequiredError

TOKEN_EXPIRATION_SECONDS = 900  # 15 minutos


def _canonicalize_params(params: Dict[str, Any]) -> str:
    """Gera representação JSON canônica e ordenada dos parâmetros para cálculo de hash."""
    # Remove chaves transitórias como token_aprovacao
    filtered = {k: v for k, v in params.items() if k not in ("token_aprovacao", "confirmacao")}
    return json.dumps(filtered, sort_keys=True, default=str)


def generate_approval_token(action: str, params: Dict[str, Any]) -> str:
    """Gera um token criptográfico HMAC-SHA256 vinculado à ação e aos parâmetros exatos."""
    settings = get_settings()
    secret = settings.zabbix_approval_token_secret.encode("utf-8")
    payload = f"{action}:{_canonicalize_params(params)}"
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    timestamp = int(time.time())
    return f"apr_{timestamp}_{signature[:24]}"


def verify_approval(action: str, params: Dict[str, Any], token: Optional[str]) -> bool:
    """
    Verifica se o token de aprovação fornecido é válido, recente e corresponde exatamente aos parâmetros.
    """
    settings = get_settings()
    if not settings.zabbix_require_approval_destructive:
        return True

    if not token or not token.startswith("apr_"):
        raise ZabbixApprovalRequiredError(
            f"A operação '{action}' requer aprovação explícita antes de ser aplicada. "
            f"Gere uma prévia e envie o token de aprovação correspondente.",
            details={"token_requerido": generate_approval_token(action, params)}
        )

    parts = token.split("_")
    if len(parts) != 3:
        raise ZabbixApprovalRequiredError("Formato de token de aprovação inválido.")

    try:
        token_time = int(parts[1])
    except ValueError:
        raise ZabbixApprovalRequiredError("Timestamp do token corrompido.")

    # Verifica validade temporal
    if time.time() - token_time > TOKEN_EXPIRATION_SECONDS:
        raise ZabbixApprovalRequiredError("O token de aprovação expirou (limite de 15 minutos excedido).")

    # Recalcula a assinatura esperada
    expected_token = generate_approval_token(action, params)
    expected_sig = expected_token.split("_")[2]
    received_sig = parts[2]

    if not hmac.compare_digest(expected_sig, received_sig):
        raise ZabbixApprovalRequiredError(
            "O token de aprovação não coincide com os parâmetros fornecidos. "
            "Qualquer alteração nos parâmetros invalida o token anterior."
        )

    return True
