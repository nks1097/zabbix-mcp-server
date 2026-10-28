# Arquitetura do Zabbix MCP Server

O **Zabbix MCP Server** é estruturado sobre padrões corporativos de observabilidade, segurança e integração assíncrona.

```mermaid
graph TD
    subgraph Clientes MCP
        Agent[Agente de IA / Claude Desktop / Antigravity IDE / Cursor]
    end

    subgraph Zabbix MCP Server
        Server[Servidor MCP - MCPServer FastMCP]
        Auth[Camada de Autorização RBAC & Políticas]
        Audit[Motor de Auditoria Local JSONL]
        
        subgraph Ferramentas e Módulos
            Disc[Descoberta Automática & Onboarding A-F]
            Rep[Motor de Relatórios PDF / Excel / CSV / JSON]
            Tools100[100 Ferramentas Especializadas em Português]
        end
        
        Client[Cliente HTTP Assíncrono httpx JSON-RPC 2.0]
        Compat[Matriz de Compatibilidade de Versões]
    end

    subgraph Infraestrutura de Monitoramento
        ZabbixAPI[Zabbix Server API - api_jsonrpc.php]
        Network[Dispositivos de Rede & Servidores]
    end

    Agent -->|Protocolo MCP STDIO / SSE| Server
    Server --> Auth
    Auth --> Tools100
    Tools100 --> Audit
    Tools100 --> Disc
    Tools100 --> Rep
    Disc -.->|Sondagem autorizada não intrusiva| Network
    Tools100 --> Client
    Client --> Compat
    Client -->|JSON-RPC 2.0 Bearer Token| ZabbixAPI
```

## Componentes Principais

1. **`MCPServer` (FastMCP):** Instância central que expõe as 100 ferramentas, recursos e prompts para agentes de IA através do Model Context Protocol oficial.
2. **Camada de Autorização e Políticas:**
   - Modo `somente_leitura`: Permite apenas consultas (`host.get`, `item.get`, relatórios).
   - Modo `operacional`: Permite cadastros, atualizações de itens e janelas de manutenção.
   - Modo `administrativo`: Permite exclusão de hosts, proxies e gerenciamento avançado.
   - **Tokens de Aprovação em 2 Passos:** Impede execução acidental de ações destrutivas.
3. **Cliente JSON-RPC 2.0 Assíncrono (`ZabbixClient`):**
   - Comunicação via `httpx.AsyncClient` com semáforo de concorrência e retries com backoff exponencial.
   - Autenticação adaptativa (cabeçalho `Authorization: Bearer <token>` para Zabbix 7.0+ e body auth para <= 6.4).
4. **Módulo de Descoberta e Onboarding:**
   - Estágios A a F: Descoberta controlada, fingerprinting, deduplicação com o inventário existente, prévia detalhada, cadastro em lote e verificação de coleta.
5. **Motor de Relatórios Profissionais:**
   - Geração local de PDF (ReportLab com layout corporativo), Excel (openpyxl com múltiplas abas), CSV, JSON e Markdown.
