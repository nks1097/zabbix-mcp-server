"""
Cliente HTTP Assíncrono JSON-RPC 2.0 para a API do Zabbix.
Suporta tokens de API (Bearer header para Zabbix 7.0+ e body auth para <= 6.4),
login com usuário/senha, retries com backoff exponencial e controle de concorrência.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from .api_compatibility import CompatibilityMatrix
from .config import Settings, get_settings
from .exceptions import ZabbixAuthError, ZabbixError, ZabbixRPCError

logger = logging.getLogger("zabbix_mcp.client")


class ZabbixClient:
    """Cliente assíncrono para a API JSON-RPC do Zabbix."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.url = self.settings.normalize_url()
        self._auth_token: Optional[str] = self.settings.zabbix_token
        self._session_auth: Optional[str] = None
        self._version: Optional[str] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._req_counter = 0

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Garante que o semáforo seja vinculado ao loop de eventos ativo atual."""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._semaphore is None or self._loop != current_loop:
            self._loop = current_loop
            self._semaphore = asyncio.Semaphore(self.settings.zabbix_max_concurrency)
            if self._client and not self._client.is_closed:
                # Fecha cliente associado a loop anterior
                self._client = None

        return self._semaphore

    async def get_http_client(self) -> httpx.AsyncClient:
        """Retorna ou inicializa o cliente HTTP assíncrono."""
        self._get_semaphore()
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                verify=self.settings.zabbix_verify_ssl,
                timeout=httpx.Timeout(self.settings.zabbix_timeout),
                headers={"Content-Type": "application/json-rpc", "User-Agent": "Zabbix-MCP-Server/1.0"}
            )
        return self._client

    async def close(self) -> None:
        """Fecha a sessão HTTP subjacente."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def get_version(self) -> str:
        """Consulta e armazena em cache a versão do Zabbix Server."""
        if self._version:
            return self._version

        res = await self.call("apiinfo.version", params={}, use_auth=False)
        self._version = str(res)
        return self._version

    async def ensure_authenticated(self) -> None:
        """Garante que há credencial válida (token ou sessão gerada via user.login)."""
        if self._auth_token:
            return

        if self._session_auth:
            return

        if self.settings.zabbix_user and self.settings.zabbix_password:
            res = await self.call(
                "user.login",
                params={
                    "username": self.settings.zabbix_user,
                    "password": self.settings.zabbix_password
                },
                use_auth=False
            )
            if isinstance(res, str):
                self._session_auth = res
            else:
                raise ZabbixAuthError("Resposta inesperada no login de usuário do Zabbix.")
        else:
            raise ZabbixAuthError("Nenhum ZABBIX_TOKEN ou combinação ZABBIX_USER/ZABBIX_PASSWORD foi configurada.")

    async def call(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        use_auth: bool = True
    ) -> Any:
        """Executa uma chamada JSON-RPC 2.0 à API do Zabbix com retries e backoff."""
        if params is None:
            params = {}

        # Descobre versão se necessário para definir formato de autenticação
        if use_auth and not self._version and method != "apiinfo.version":
            try:
                await self.get_version()
            except Exception:
                # Se falhar obter versão sem auth, assume versão 7.0+ por padrão
                self._version = "7.0.0"

        if use_auth:
            await self.ensure_authenticated()

        self._req_counter += 1
        req_id = self._req_counter

        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": req_id
        }

        headers: Dict[str, str] = {}
        active_token = self._auth_token or self._session_auth

        if use_auth and active_token:
            # No Zabbix 7.0+, o token é enviado no cabeçalho Authorization: Bearer
            if CompatibilityMatrix.requires_bearer_header(self._version) or self._auth_token:
                headers["Authorization"] = f"Bearer {active_token}"
            else:
                payload["auth"] = active_token

        client = await self.get_http_client()
        last_error: Optional[Exception] = None

        async with self._get_semaphore():
            for attempt in range(1, self.settings.zabbix_max_retries + 1):
                try:
                    response = await client.post(
                        self.url,
                        json=payload,
                        headers=headers
                    )

                    # Zabbix API pode retornar HTTP 412 se cabeçalho Bearer falhar ou 5xx
                    if response.status_code >= 500:
                        raise httpx.HTTPStatusError(
                            f"HTTP {response.status_code} recebido do servidor Zabbix",
                            request=response.request,
                            response=response
                        )

                    data = response.json()

                    if "error" in data:
                        err = data["error"]
                        code = err.get("code", -1)
                        msg = err.get("message", "Erro desconhecido")
                        detail = err.get("data", "")

                        # Erro de autenticação típico (-32600 invalid auth)
                        if "auth" in msg.lower() or "auth" in detail.lower() or code in (-32600, -32500):
                            raise ZabbixAuthError(f"Falha de autenticação na API Zabbix: {msg} - {detail}")

                        raise ZabbixRPCError(code, msg, detail)

                    return data.get("result")

                except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                    last_error = e
                    if attempt < self.settings.max_retries if hasattr(self.settings, 'max_retries') else self.settings.zabbix_max_retries:
                        backoff = self.settings.zabbix_backoff_factor * (2 ** (attempt - 1))
                        await asyncio.sleep(backoff)
                    else:
                        raise ZabbixError(f"Falha na comunicação com a API Zabbix ({self.url}): {str(e)}") from e
                except (ZabbixRPCError, ZabbixAuthError):
                    # Não retenta erros lógicos ou de credenciais
                    raise

        if last_error:
            raise ZabbixError(f"Falha persistente na chamada {method}: {str(last_error)}")

    async def test_connection(self) -> Dict[str, Any]:
        """Testa conectividade, autenticação e versão da API Zabbix."""
        version = await self.get_version()
        # Valida autenticação chamando host.get com limit 1
        hosts = await self.call("host.get", params={"limit": 1, "output": ["hostid", "host"]})
        return {
            "status": "conectado",
            "url": self.url,
            "versao": version,
            "autenticado": True,
            "hosts_acessiveis": len(hosts) if isinstance(hosts, list) else 0
        }


_global_client: Optional[ZabbixClient] = None


def get_zabbix_client() -> ZabbixClient:
    """Retorna o cliente global singleton."""
    global _global_client
    if _global_client is None:
        _global_client = ZabbixClient()
    return _global_client
