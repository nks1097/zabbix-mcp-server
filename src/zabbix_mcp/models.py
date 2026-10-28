"""
Modelos de dados e contratos de entrada/saída padronizados para o Zabbix MCP Server.
"""

import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadados de execução da ferramenta MCP."""
    duracao_ms: float = Field(default=0.0, description="Duração da execução em milissegundos")
    truncado: bool = Field(default=False, description="Indica se os dados foram truncados por limite de paginação")
    versao_zabbix: Optional[str] = Field(default=None, description="Versão detectada do Zabbix Server")
    total_registros: Optional[int] = Field(default=None, description="Total de registros encontrados")
    pagina: Optional[int] = Field(default=None, description="Número da página retornada")


class ToolResult(BaseModel):
    """Contrato padronizado de resposta para todas as ferramentas MCP."""
    sucesso: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    dados: Any = Field(default=None, description="Payload estruturado retornado pela operação")
    erro: Optional[str] = Field(default=None, description="Descrição detalhada do erro caso sucesso seja false")
    avisos: List[str] = Field(default_factory=list, description="Lista de avisos, recomendações ou pendências")
    id_requisicao: str = Field(
        default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}",
        description="Identificador único da requisição para rastreabilidade"
    )
    metadados: ToolMetadata = Field(
        default_factory=ToolMetadata,
        description="Metadados operacionais da execução"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado em dicionário para o MCP."""
        return self.model_dump(mode="json")


# Modelos para Interfaces e Hosts
class InterfaceType(int, Enum):
    """Tipos de interface suportados pelo Zabbix."""
    AGENT = 1
    SNMP = 2
    IPMI = 3
    JMX = 4


class InterfaceDetails(BaseModel):
    """Especificação de interface de rede para host no Zabbix."""
    type: InterfaceType = Field(default=InterfaceType.AGENT, description="Tipo da interface (1=Agente, 2=SNMP, 3=IPMI, 4=JMX)")
    main: int = Field(default=1, description="1 para interface primária, 0 para secundária")
    useip: int = Field(default=1, description="1 para conectar via IP, 0 para conectar via DNS")
    ip: str = Field(default="127.0.0.1", description="Endereço IP do dispositivo")
    dns: str = Field(default="", description="Nome DNS do dispositivo")
    port: str = Field(default="10050", description="Porta de escuta do serviço")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalhes adicionais (e.g. SNMP version, community, security)")


class DiscoveredDevice(BaseModel):
    """Dispositivo descoberto na rede com evidências."""
    ip: str
    dns: Optional[str] = None
    hostname_sugerido: str
    portas_abertas: List[int] = Field(default_factory=list)
    sistema_operacional: Optional[str] = None
    confianca_so: float = Field(default=0.0, ge=0.0, le=1.0)
    servicos_detectados: List[str] = Field(default_factory=list)
    tipo_dispositivo: str = Field(default="desconhecido")
    templates_recomendados: List[str] = Field(default_factory=list)
    duplicidade_detectada: bool = False
    hostid_existente: Optional[str] = None
    motivo_duplicidade: Optional[str] = None


class OnboardingPreview(BaseModel):
    """Prévia estruturada de cadastro de dispositivo."""
    host_tecnico: str
    nome_visivel: str
    ip: str
    dns: str = ""
    portas: List[int] = Field(default_factory=list)
    grupos_propostos: List[str]
    templates_propostos: List[str]
    tipo_interface: str
    porta_interface: str
    campos_inventario: Dict[str, str] = Field(default_factory=dict)
    requer_aprovacao_manual: bool = False
    avisos: List[str] = Field(default_factory=list)
    token_aprovacao: Optional[str] = None


class BatchOnboardingResult(BaseModel):
    """Resultado do processo de onboarding em lote."""
    total_analisados: int = 0
    total_cadastrados: int = 0
    total_ignorados_duplicados: int = 0
    total_falhas: int = 0
    hosts_cadastrados: List[Dict[str, Any]] = Field(default_factory=list)
    erros: List[Dict[str, Any]] = Field(default_factory=list)
