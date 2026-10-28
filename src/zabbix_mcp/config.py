"""
Módulo de Configurações do Zabbix MCP Server.
Utiliza Pydantic Settings para carregamento seguro a partir de variáveis de ambiente.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthorizationMode(str, Enum):
    """Modos de autorização para o servidor MCP."""
    SOMENTE_LEITURA = "somente_leitura"
    OPERACIONAL = "operacional"
    ADMINISTRATIVO = "administrativo"


class Settings(BaseSettings):
    """Configurações centrais do Zabbix MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Conexão com o Zabbix
    zabbix_url: str = Field(
        default="http://192.168.0.107:8080/api_jsonrpc.php",
        description="URL completa do endpoint api_jsonrpc.php do Zabbix"
    )
    zabbix_token: Optional[str] = Field(
        default=None,
        description="Token de API gerado no Zabbix (recomendado)"
    )
    zabbix_user: str = Field(
        default="Admin",
        description="Usuário para login caso token não seja utilizado"
    )
    zabbix_password: Optional[str] = Field(
        default=None,
        description="Senha do usuário Zabbix"
    )

    # Segurança e Autorização
    zabbix_mcp_mode: AuthorizationMode = Field(
        default=AuthorizationMode.SOMENTE_LEITURA,
        description="Nível de autorização do MCP: somente_leitura, operacional, administrativo"
    )
    zabbix_require_approval_destructive: bool = Field(
        default=True,
        description="Exigir aprovação em dois passos (token de aprovação) para ações destrutivas"
    )
    zabbix_approval_token_secret: str = Field(
        default="zabbix-mcp-secret-key-change-in-production",
        description="Chave secreta para assinatura HMAC dos tokens de aprovação"
    )

    # Desempenho e Conectividade
    zabbix_timeout: float = Field(
        default=30.0,
        description="Timeout em segundos para chamadas HTTP à API Zabbix"
    )
    zabbix_verify_ssl: bool = Field(
        default=True,
        description="Verificar certificados SSL/TLS da API Zabbix"
    )
    zabbix_max_retries: int = Field(
        default=3,
        description="Número máximo de tentativas com backoff exponencial para erros transitórios"
    )
    zabbix_backoff_factor: float = Field(
        default=0.5,
        description="Fator de multiplicação do backoff exponencial"
    )
    zabbix_max_concurrency: int = Field(
        default=10,
        description="Limite de requisições simultâneas ao Zabbix"
    )
    zabbix_page_size: int = Field(
        default=100,
        description="Tamanho padrão de lote/página para consultas volumosas"
    )

    # Armazenamento e Auditoria
    zabbix_reports_dir: Path = Field(
        default=Path("./reports_output"),
        description="Diretório onde relatórios gerados (PDF, XLSX, CSV, JSON) são gravados"
    )
    zabbix_audit_log_path: Path = Field(
        default=Path("./audit_mcp.jsonl"),
        description="Caminho do arquivo de auditoria das operações executadas pelo MCP"
    )

    def normalize_url(self) -> str:
        """Garante que a URL termine com /api_jsonrpc.php."""
        url = self.zabbix_url.strip()
        if not url.endswith("/api_jsonrpc.php"):
            if url.endswith("/"):
                url = f"{url}api_jsonrpc.php"
            else:
                url = f"{url}/api_jsonrpc.php"
        return url


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retorna a instância singleton de configurações."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings(new_settings: Optional[Settings] = None) -> None:
    """Atualiza ou redefine as configurações (útil para testes)."""
    global _settings
    _settings = new_settings
