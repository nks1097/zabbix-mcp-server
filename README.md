# Zabbix MCP Server Universal

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0%2B%20%2F%202.x-green)](https://modelcontextprotocol.io/)
[![Zabbix](https://img.shields.io/badge/Zabbix-6.0%20%7C%206.4%20%7C%207.0%20LTS%20%7C%207.4-red)](https://www.zabbix.com/)

Servidor MCP (**Model Context Protocol**) corporativo para gerenciamento inteligente do **Zabbix Enterprise Monitoring**, com **100 ferramentas em português**, automação completa de descoberta e onboarding de dispositivos em 6 estágios, motor profissional de relatórios (PDF, XLSX, CSV, JSON, Markdown), controles de acesso baseados em funções (RBAC), aprovação em dois passos e compatibilidade universal.

*Read this in English: [README.en.md](README.en.md)*

---

## 🚀 Destaques do Projeto

- **100 Ferramentas Oficiais:** Nomes estáveis em `snake_case`, contratos Pydantic estritos e descrições detalhadas em português cobrindo todas as áreas operacionais do Zabbix.
- **Onboarding Automatizado de Dispositivos (Estágios A ao F):**
  1. *Descoberta Controlada:* Varredura de sub-redes autorizadas com taxa limitada e sem risco de saturação.
  2. *Identificação & Fingerprinting:* Inferência de Sistema Operacional (Linux, Windows, Network Appliance) com score de confiança e portas de serviço.
  3. *Reconciliação & Deduplicação:* Checagem contra o inventário existente para evitar hosts duplicados.
  4. *Planejamento & Prévia:* Exibição de interfaces, grupos e templates antes de qualquer gravação.
  5. *Cadastro em Lote Transacional:* Criação segura com tratamento individual de falhas.
  6. *Verificação Pós-Cadastro:* Confirmação de interfaces sem erros, itens ativos e chegada do primeiro ciclo de métricas.
- **Motor Profissional de Relatórios:** Geração direta de documentos em **PDF** corporativo (com tabelas e layout executivo), **Planilhas Excel (.xlsx)** multi-abas, **CSV**, **JSON** e **Markdown**.
- **Segurança Produtiva (DevSecOps):**
  - Modos de autorização RBAC: `somente_leitura` (padrão), `operacional` e `administrativo`.
  - **Aprovação em Dois Passos:** Ações destrutivas (excluir hosts, alterar regras) exigem token criptográfico HMAC vinculado aos parâmetros exatos com expiração de 15 minutos.
  - **Redação Automática de Segredos:** Tokens, senhas e communities SNMP são mascarados como `[REDACTED]`.
  - **Proteção contra SSRF:** Bloqueio de loopback (`127.0.0.1`) e limitação de escopos de varredura.
  - **Trilha de Auditoria Local:** Registro imutável em JSON Lines (`audit_mcp.jsonl`) de todas as invocações.
- **Compatibilidade Inteligente de Versões:** Identificação dinâmica via `apiinfo.version` com suporte a autenticação por cabeçalho Bearer no Zabbix 7.0+ e suporte a Zabbix 6.0 LTS / 6.4.

---

## 📖 Guia de Instalação e Configuração Passo a Passo

### Passo 1: Pré-Requisitos do Sistema
- **Python:** Versão `3.11`, `3.12` ou `3.13` instalada (`python --version` ou `python3 --version`).
- **Git:** Instalado no sistema (`git --version`).
- **Instância Zabbix:** Endpoint HTTP/HTTPS acessível (ex: `http://192.168.0.107:8080/api_jsonrpc.php`).

---

### Passo 2: Gerar o Token de API no Zabbix Web
O token de API é o método mais seguro e recomendado de autenticação:
1. Abra a interface web do Zabbix no navegador.
2. Acesse o menu: **Administração** (`Administration`) ➔ **Tokens de API** (`API tokens`).
3. Clique em **Criar token de API** (`Create API token`) no canto superior direito.
4. Digite um nome (ex: `Zabbix-MCP-Server`) e clique em **Adicionar** (`Add`).
5. **Copie imediatamente a chave de 64 caracteres** exibida na janela pop-up (ela não será mostrada novamente).

---

### Passo 3: Clonar o Repositório do GitHub
```bash
git clone https://github.com/nks1097/zabbix-mcp-server.git
cd zabbix-mcp-server
```

---

### Passo 4: Criar e Ativar o Ambiente Virtual

#### No Windows (PowerShell):
> [!TIP]
> Caso o PowerShell bloqueie a execução de scripts (`running scripts is disabled on this system`), execute o comando abaixo antes de ativar:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```
*(O indicador `(.venv)` aparecerá no início da sua linha de comando).*

#### No Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Passo 5: Instalar as Dependências do Projeto
```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

---

### Passo 6: Configurar o Arquivo `.env`
Copie o arquivo de exemplo `.env.example` criando o seu `.env`:

**No Windows:**
```powershell
copy .env.example .env
```

**No Linux / macOS:**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com os dados do seu Zabbix:
```ini
# URL completa do endpoint JSON-RPC do Zabbix
ZABBIX_URL=http://192.168.0.107:8080/api_jsonrpc.php

# Token de API do Zabbix gerado no Passo 2
ZABBIX_TOKEN=3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45

# Modo de operação: 'somente_leitura', 'operacional' ou 'administrativo'
ZABBIX_MCP_MODE=operacional

# Validação SSL (defina false para certificados autoassinados ou HTTP local)
ZABBIX_VERIFY_SSL=false

# Exigir aprovação em 2 passos para ações destrutivas (excluir hosts)
ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE=true
ZABBIX_APPROVAL_TOKEN_SECRET=sua-chave-secreta-hmac-aqui
```

---

### Passo 7: Validar a Instalação com Testes
Execute a suíte de testes automatizados para validar a integridade:

```bash
# Executar todos os testes unitários (offline com fixtures mock)
pytest tests/unit -v

# Executar os testes de integração ao vivo contra a sua instância do Zabbix
pytest tests/integration/test_live_zabbix.py -v
```

---

## 🔌 Configuração nos Principais Clientes MCP

### 1. Claude Desktop
Adicione ao arquivo de configuração:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "C:/Users/SEU_USUARIO/zabbix-mcp-server/.venv/Scripts/python.exe",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "cwd": "C:/Users/SEU_USUARIO/zabbix-mcp-server",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional",
        "ZABBIX_VERIFY_SSL": "false"
      }
    }
  }
}
```

### 2. Antigravity IDE (`mcp_config.json`)
Localizado em `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "zabbix-mcp": {
      "command": "C:\\Users\\Natanael Krindges\\.gemini\\antigravity-ide\\mcp\\zabbix\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "zabbix_mcp.server",
        "--transport",
        "stdio"
      ],
      "cwd": "C:\\Users\\Natanael Krindges\\.gemini\\antigravity-ide\\mcp\\zabbix",
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### 3. Cursor (`.cursor/mcp.json`)
No arquivo `.cursor/mcp.json` na raiz do workspace ou nas configurações de MCP:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

### 4. VS Code (com Cline / Roo Code / Claude Dev)
Nas configurações da extensão ou no arquivo de ferramentas MCP:

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "seu_token_aqui",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

---

## 🐳 Execução via Docker e Docker Compose

Para rodar o servidor MCP como um microsserviço containerizado com transporte **SSE**:

```bash
# 1. Copiar e preencher o .env
cp .env.example .env

# 2. Inicializar o container em segundo plano
docker compose up -d

# 3. Verificar os logs
docker compose logs -f zabbix-mcp

# 4. Validar o endpoint SSE
curl -I http://localhost:8000/sse
```

---

## 🔒 Modos de Segurança e Permissões (RBAC)

O servidor implementa 3 níveis de permissão controlados pela variável `ZABBIX_MCP_MODE`:

1. **`somente_leitura` (Padrão de Fábrica):** Bloqueia qualquer operação que tente alterar dados no Zabbix. Apenas consultas e relatórios são permitidos.
2. **`operacional`:** Permite criação e atualização de hosts, reconhecimento de problemas, manutenções e vinculação de templates.
3. **`administrativo`:** Habilita comandos estruturais críticos. Ações destrutivas (excluir hosts, remover proxies) exigem aprovação em dois passos via token HMAC.

---

## 🛠️ Catálogo Completo das 100 Ferramentas (Para que serve cada uma)

Abaixo está o índice descritivo de todas as 100 ferramentas disponíveis no servidor MCP, organizadas por suas 10 categorias funcionais. Para especificações detalhadas de todos os parâmetros e esquemas JSON de entrada/saída, consulte o [Manual Técnico de Ferramentas](docs/ferramentas.md).


### Categoria 1 — Descoberta Automática de Dispositivos

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 01 | [`zabbix_descobrir_rede`](docs/ferramentas.md#001-zabbix-descobrir-rede) | `Operacional` | Realiza uma varredura controlada e não-intrusiva em faixas de rede CIDR IPv4 explicitamente autorizadas. |
| 02 | [`zabbix_analisar_dispositivo`](docs/ferramentas.md#002-zabbix-analisar-dispositivo) | `Somente Leitura` | Analisa detalhadamente um endereço IP específico, coletando latência, hostname reverso via DNS (PTR), portas abertas fundamentais (22/SSH, 80/HTTP, 443/HTTPS, 161/SNMP, 10050/Agent, 3389/RDP, 445/SMB) e evidências preliminares de identificação. |
| 03 | [`zabbix_identificar_sistema_operacional`](docs/ferramentas.md#003-zabbix-identificar-sistema-operacional) | `Somente Leitura` | Infere o sistema operacional provável (Linux, Windows Server, Appliance de Rede, Servidor Web) a partir de assinaturas de portas e comportamento de rede, retornando o nome do SO e um percentual de confiança. |
| 04 | [`zabbix_identificar_servicos`](docs/ferramentas.md#004-zabbix-identificar-servicos) | `Somente Leitura` | Mapeia serviços monitoráveis em execução no host (servidores HTTP/Nginx/Apache, bancos de dados MySQL/PostgreSQL, SSH, Docker, SNMP) através de sondagens não-invasivas em portas bem conhecidas. |
| 05 | [`zabbix_deduplicar_dispositivos`](docs/ferramentas.md#005-zabbix-deduplicar-dispositivos) | `Somente Leitura` | Verifica se um dispositivo descoberto já se encontra cadastrado no Zabbix Server, comparando endereços IP de interfaces, nomes visíveis, nomes técnicos e resolução DNS. |
| 06 | [`zabbix_comparar_dispositivos_cadastrados`](docs/ferramentas.md#006-zabbix-comparar-dispositivos-cadastrados) | `Somente Leitura` | Cruza uma lista de IPs descobertos com todos os hosts atualmente cadastrados no Zabbix, gerando um balanço categorizado: novos nós a cadastrar, nós já monitorados e possíveis divergências de configuração. |
| 07 | [`zabbix_recomendar_templates`](docs/ferramentas.md#007-zabbix-recomendar-templates) | `Somente Leitura` | Cruza o sistema operacional e serviços detectados com o acervo de templates instalados no Zabbix, recomendando os templates oficiais mais indicados com seus respectivos IDs. |
| 08 | [`zabbix_previsualizar_cadastro`](docs/ferramentas.md#008-zabbix-previsualizar-cadastro) | `Somente Leitura` | Simula a criação do host no Zabbix (Dry-Run), apresentando a estrutura JSON exata dos parâmetros: nome técnico, nome visível, interfaces, grupos, templates vinculados e macros, sem gravar alterações. |
| 09 | [`zabbix_cadastrar_dispositivos_em_lote`](docs/ferramentas.md#009-zabbix-cadastrar-dispositivos-em-lote) | `Operacional` | Cria múltiplos hosts aprovados no Zabbix de forma transacional e segura. |
| 10 | [`zabbix_verificar_descoberta`](docs/ferramentas.md#010-zabbix-verificar-descoberta) | `Somente Leitura` | Audita o estado pós-implantação dos hosts criados: confirma se a interface está ativa, se os templates foram herdados, se os itens estão criados e se os primeiros dados de telemetria já chegaram. |

### Categoria 2 — Hosts e Interfaces

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 11 | [`zabbix_listar_hosts`](docs/ferramentas.md#011-zabbix-listar-hosts) | `Somente Leitura` | Lista os hosts monitorados no Zabbix aplicando filtros flexíveis por nome, grupo de hosts, status de monitoramento (habilitado/desabilitado) e estado de disponibilidade de interface. |
| 12 | [`zabbix_consultar_host`](docs/ferramentas.md#012-zabbix-consultar-host) | `Somente Leitura` | Retorna o registro completo e detalhado de um host específico no Zabbix, incluindo interfaces de rede, grupos vinculados, templates herdados, macros, status e metadados de inventário. |
| 13 | [`zabbix_criar_host`](docs/ferramentas.md#013-zabbix-criar-host) | `Operacional` | Cria um novo host no Zabbix com parâmetros estritamente validados: nome técnico, nome visível, endereço IP ou DNS, porta, tipo de interface (Agent, SNMP, IPMI, JMX), grupos e templates. |
| 14 | [`zabbix_atualizar_host`](docs/ferramentas.md#014-zabbix-atualizar-host) | `Operacional` | Atualiza propriedades permitidas de um host existente, como nome visível, descrição, status de monitoramento, grupos associados e macros. |
| 15 | [`zabbix_remover_host`](docs/ferramentas.md#015-zabbix-remover-host) | `Administrativo (Exige Aprovação HMAC)` | Exclui permanentemente um host do Zabbix juntamente com todo o seu histórico de dados e configurações. |
| 16 | [`zabbix_ativar_desativar_host`](docs/ferramentas.md#016-zabbix-ativar-desativar-host) | `Operacional` | Altera o status operacional de monitoramento de um host entre 0 (Monitorado/Ativo) e 1 (Não monitorado/Desativado), pausando temporariamente todas as checagens e alertas. |
| 17 | [`zabbix_gerenciar_interfaces_host`](docs/ferramentas.md#017-zabbix-gerenciar-interfaces-host) | `Operacional` | Cria, consulta e atualiza interfaces de comunicação de um host (Zabbix Agent, SNMP v1/v2c/v3, IPMI, JMX), definindo porta, IP, DNS e interface primária. |
| 18 | [`zabbix_associar_templates_host`](docs/ferramentas.md#018-zabbix-associar-templates-host) | `Operacional` | Vincula um ou mais templates a um host existente no Zabbix preservando intactos todos os templates que já estavam previamente vinculados. |
| 19 | [`zabbix_desassociar_templates_host`](docs/ferramentas.md#019-zabbix-desassociar-templates-host) | `Operacional` | Remove a associação de templates de um host, oferecendo a opção de limpeza (unlink_and_clear) para remover do host os itens e gráficos herdados daquele template. |
| 20 | [`zabbix_consultar_disponibilidade_host`](docs/ferramentas.md#020-zabbix-consultar-disponibilidade-host) | `Somente Leitura` | Inspeciona o estado operacional das interfaces de comunicação do host (Agent, SNMP, IPMI, JMX): se estão disponíveis (1), indisponíveis com erro (2) ou desconhecidas (0), exibindo mensagens de erro de polling se houver. |

### Categoria 3 — Coleta de Dados e Métricas

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 21 | [`zabbix_listar_itens`](docs/ferramentas.md#021-zabbix-listar-itens) | `Somente Leitura` | Lista os itens de telemetria cadastrados no Zabbix com filtros por host, chave de item (ex: system. |
| 22 | [`zabbix_consultar_item`](docs/ferramentas.md#022-zabbix-consultar-item) | `Somente Leitura` | Recupera a configuração completa de um item específico: chave, intervalo de atualização, período de retenção de histórico/trends, tipo de valor, pré-processamento e estado de erro. |
| 23 | [`zabbix_criar_item`](docs/ferramentas.md#023-zabbix-criar-item) | `Operacional` | Cria um novo item de coleta customizado em um host com chave, tipo de informação, intervalo de atualização e parâmetros validados. |
| 24 | [`zabbix_atualizar_item`](docs/ferramentas.md#024-zabbix-atualizar-item) | `Operacional` | Modifica parâmetros permitidos de um item de coleta, como intervalo de atualização (delay), período de histórico, status (habilitado/desabilitado) e descrição. |
| 25 | [`zabbix_consultar_historico`](docs/ferramentas.md#025-zabbix-consultar-historico) | `Somente Leitura` | Recupera os registros históricos pontuais de valores de um ou mais itens em uma janela temporal (numéricos float, inteiros, strings ou logs), com ordenação cronológica. |
| 26 | [`zabbix_consultar_tendencias`](docs/ferramentas.md#026-zabbix-consultar-tendencias) | `Somente Leitura` | Recupera dados consolidados por hora de tendências estatísticas (trends: valor mínimo, médio e máximo) calculados pelo Zabbix para longos períodos de tempo. |
| 27 | [`zabbix_ultimos_valores`](docs/ferramentas.md#027-zabbix-ultimos-valores) | `Somente Leitura` | Consulta a última leitura válida recebida (lastvalue), horário da última coleta e unidade de medida de todos os itens ou de itens filtrados de um host. |
| 28 | [`zabbix_verificar_coleta`](docs/ferramentas.md#028-zabbix-verificar-coleta) | `Somente Leitura` | Analisa se os itens habilitados estão realmente recebendo dados dentro do intervalo esperado (delay), identificando itens atrasados ou com erros de polling. |
| 29 | [`zabbix_detectar_lacunas_coleta`](docs/ferramentas.md#029-zabbix-detectar-lacunas-coleta) | `Somente Leitura` | Examina o histórico de um item e detecta 'buracos' ou lacunas temporais (gaps) onde dados deveriam ter sido coletados mas não foram, calculando a duração de cada falha. |
| 30 | [`zabbix_diagnosticar_coleta`](docs/ferramentas.md#030-zabbix-diagnosticar-coleta) | `Somente Leitura` | Produz um diagnóstico inteligente correlacionando erros de itens não suportados (unsupported items), indisponibilidade de interface e atrasos na fila de coleta do host. |

### Categoria 4 — Problemas, Triggers e Eventos

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 31 | [`zabbix_listar_problemas`](docs/ferramentas.md#031-zabbix-listar-problemas) | `Somente Leitura` | Lista incidentes e problemas ativos no ambiente com suporte a filtros por severidade (Informational até Disaster), host, grupo, status de reconhecimento e tags. |
| 32 | [`zabbix_consultar_problema`](docs/ferramentas.md#032-zabbix-consultar-problema) | `Somente Leitura` | Retorna os detalhes analíticos completos de um problema específico: evento gerador, trigger associada, tags, tempo de duração, severidade e mensagens de reconhecimento. |
| 33 | [`zabbix_consultar_eventos`](docs/ferramentas.md#033-zabbix-consultar-eventos) | `Somente Leitura` | Consulta a linha do tempo de eventos de problemas (geração e recuperação) no Zabbix, permitindo filtrar por janela temporal, host e severidade. |
| 34 | [`zabbix_listar_triggers`](docs/ferramentas.md#034-zabbix-listar-triggers) | `Somente Leitura` | Lista as regras de alerta (triggers) configuradas no Zabbix com seus respectivos estados (0=OK, 1=Problem), expressões de gatilho, severidades e status (ativa/inativa). |
| 35 | [`zabbix_consultar_trigger`](docs/ferramentas.md#035-zabbix-consultar-trigger) | `Somente Leitura` | Recupera a definição técnica detalhada de uma trigger: expressão matemática exata, expressão de recuperação, prioridade, modo de geração de eventos e dependências. |
| 36 | [`zabbix_criar_trigger`](docs/ferramentas.md#036-zabbix-criar-trigger) | `Operacional` | Cria uma nova regra de trigger customizada vinculada a itens de um host com expressão sintaticamente validada e nível de severidade configurável. |
| 37 | [`zabbix_atualizar_trigger`](docs/ferramentas.md#037-zabbix-atualizar-trigger) | `Operacional` | Atualiza propriedades permitidas de uma trigger: expressão, severidade, status de habilitação, descrição e tags de correlação. |
| 38 | [`zabbix_reconhecer_problema`](docs/ferramentas.md#038-zabbix-reconhecer-problema) | `Operacional` | Registra o reconhecimento formal (Acknowledge) de um problema ativo no Zabbix, permitindo anexar uma mensagem de justificativa/chamado e opcionalmente alterar a severidade ou fechar o evento. |
| 39 | [`zabbix_obter_historico_problema`](docs/ferramentas.md#039-zabbix-obter-historico-problema) | `Somente Leitura` | Recupera o histórico completo de ações de um problema: quando iniciou, quem reconheceu, comentários adicionados, escalonamentos de notificação e horário de fechamento. |
| 40 | [`zabbix_investigar_incidente`](docs/ferramentas.md#040-zabbix-investigar-incidente) | `Somente Leitura` | Executa uma investigação holística de causa raiz para um incidente: correlaciona o problema com as métricas do host no exato momento da falha, eventos concomitantes e alertas relacionados. |

### Categoria 5 — Relatórios e Exportações

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 41 | [`zabbix_gerar_relatorio_executivo`](docs/ferramentas.md#041-zabbix-gerar-relatorio-executivo) | `Somente Leitura` | Consolida indicadores executivos do ambiente: total de hosts monitorados, distribuição por severidade de problemas ativos, taxa geral de saúde e principais gargalos em formato de alto nível. |
| 42 | [`zabbix_gerar_relatorio_disponibilidade`](docs/ferramentas.md#042-zabbix-gerar-relatorio-disponibilidade) | `Somente Leitura` | Calcula a disponibilidade percentual (uptime vs downtime) de hosts e serviços no período selecionado, fundamentado em dados reais de triggers e eventos. |
| 43 | [`zabbix_gerar_relatorio_problemas`](docs/ferramentas.md#043-zabbix-gerar-relatorio-problemas) | `Somente Leitura` | Agrupa e analisa todos os incidentes ocorridos no período por severidade, tempo médio de duração, hosts mais incidentados (Top Problematic Hosts) e taxa de resolução. |
| 44 | [`zabbix_gerar_relatorio_desempenho`](docs/ferramentas.md#044-zabbix-gerar-relatorio-desempenho) | `Somente Leitura` | Analisa o perfil de consumo de recursos computacionais (CPU, memória RAM, tráfego de rede e espaço em disco) apontando picos, médias e desvios de capacidade. |
| 45 | [`zabbix_gerar_relatorio_inventario`](docs/ferramentas.md#045-zabbix-gerar-relatorio-inventario) | `Somente Leitura` | Mapeia todo o parque instalado: sistemas operacionais, localizações físicas/virtuais, números de série, versões de software e cobertura de monitoramento por grupo. |
| 46 | [`zabbix_gerar_relatorio_capacidade`](docs/ferramentas.md#046-zabbix-gerar-relatorio-capacidade) | `Somente Leitura` | Analisa tendências de consumo de armazenamento (disco) e memória para prever dias até a exaustão (Days Until Full / Runway) com base no crescimento histórico. |
| 47 | [`zabbix_gerar_relatorio_sla`](docs/ferramentas.md#047-zabbix-gerar-relatorio-sla) | `Somente Leitura` | Calcula os índices de cumprimento de acordos de nível de serviço (SLA) para serviços de negócio configurados, apontando tempo de conformidade e violações. |
| 48 | [`zabbix_exportar_relatorio_pdf`](docs/ferramentas.md#048-zabbix-exportar-relatorio-pdf) | `Somente Leitura` | Converte os dados de qualquer relatório estruturado em um documento PDF corporativo profissional, com cabeçalho, tabelas zebradas, sumário executivo e layout limpo. |
| 49 | [`zabbix_exportar_relatorio_excel`](docs/ferramentas.md#049-zabbix-exportar-relatorio-excel) | `Somente Leitura` | Gera planilhas nativas em formato Microsoft Excel (. |
| 50 | [`zabbix_agendar_relatorio`](docs/ferramentas.md#050-zabbix-agendar-relatorio) | `Operacional` | Configura agendamentos nativos de relatórios no Zabbix Server (Zabbix 6. |

### Categoria 6 — Alertas, Ações e Notificações

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 51 | [`zabbix_listar_alertas`](docs/ferramentas.md#051-zabbix-listar-alertas) | `Somente Leitura` | Consulta a fila de alertas gerados pelo Zabbix, permitindo filtrar por destinatário, período, canal de mídia (E-mail, Telegram, Slack) e status de envio (enviado/falhou). |
| 52 | [`zabbix_consultar_acoes`](docs/ferramentas.md#052-zabbix-consultar-acoes) | `Somente Leitura` | Lista as regras de ações (actions) configuradas no Zabbix para tratamento de triggers, descoberta de rede, autorregistro ou serviços internos. |
| 53 | [`zabbix_consultar_historico_notificacoes`](docs/ferramentas.md#053-zabbix-consultar-historico-notificacoes) | `Somente Leitura` | Recupera o histórico cronológico de notificações enviadas para um determinado usuário ou host, facilitando a correlação de alertas. |
| 54 | [`zabbix_listar_canais_notificacao`](docs/ferramentas.md#054-zabbix-listar-canais-notificacao) | `Somente Leitura` | Lista os tipos de mídia (media types) configurados no Zabbix Server (SMTP, SMS, Webhooks para Jira/ServiceNow/Teams/Slack, scripts personalizados). |
| 55 | [`zabbix_testar_canal_notificacao`](docs/ferramentas.md#055-zabbix-testar-canal-notificacao) | `Operacional` | Dispara um teste controlado de envio através de um tipo de mídia específico para validar a conectividade e integridade das credenciais configuradas. |
| 56 | [`zabbix_gerenciar_acoes`](docs/ferramentas.md#056-zabbix-gerenciar-acoes) | `Operacional` | Habilita, desabilita ou atualiza as propriedades operacionais de uma regra de ação do Zabbix. |
| 57 | [`zabbix_consultar_regras_escalonamento`](docs/ferramentas.md#057-zabbix-consultar-regras-escalonamento) | `Somente Leitura` | Consulta a árvore de escalonamento configurada em uma ação (ex: Passo 1: notificar NOC; Passo 2 após 30m: notificar Coordenador; Passo 3 após 1h: notificar Gerente). |
| 58 | [`zabbix_suprimir_notificacoes`](docs/ferramentas.md#058-zabbix-suprimir-notificacoes) | `Operacional` | Aplica supressão temporária manual de notificações para um problema específico ou host, impedindo o envio de novos alertas sem desativar a coleta. |
| 59 | [`zabbix_analisar_falsos_positivos`](docs/ferramentas.md#059-zabbix-analisar-falsos-positivos) | `Somente Leitura` | Examina o histórico recente de eventos para identificar triggers com comportamento de 'flapping' (oscilação contínua entre Problem e OK em curtos intervalos). |
| 60 | [`zabbix_recomendar_ajustes_alertas`](docs/ferramentas.md#060-zabbix-recomendar-ajustes-alertas) | `Somente Leitura` | Com base no histórico e nas oscilações de métricas, propõe ajustes técnicos fundamentados em triggers (ex: adicionar função min() ou max(), aumentar tempo de avaliação de 1m para 5m). |

### Categoria 7 — Serviços de Negócio, Manutenções e Mapas

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 61 | [`zabbix_listar_servicos`](docs/ferramentas.md#061-zabbix-listar-servicos) | `Somente Leitura` | Lista a árvore de Business Services (Serviços de Negócio) configurada no Zabbix, exibindo hierarquia pai-filho e status de saúde consolidado. |
| 62 | [`zabbix_consultar_servico`](docs/ferramentas.md#062-zabbix-consultar-servico) | `Somente Leitura` | Retorna os detalhes de um serviço de negócio específico: regras de propagação de status, triggers filhas associadas, pesos e tags de correlação. |
| 63 | [`zabbix_criar_servico`](docs/ferramentas.md#063-zabbix-criar-servico) | `Operacional` | Cria um novo serviço de negócio no catálogo de serviços do Zabbix, definindo seu algoritmo de cálculo de status (qualquer filho falha, todos falham, etc. |
| 64 | [`zabbix_atualizar_servico`](docs/ferramentas.md#064-zabbix-atualizar-servico) | `Operacional` | Atualiza propriedades, regras de avaliação e dependências de um serviço de negócio existente. |
| 65 | [`zabbix_consultar_sla_servico`](docs/ferramentas.md#065-zabbix-consultar-sla-servico) | `Somente Leitura` | Calcula os indicadores SLI (Service Level Indicator) e o cumprimento de metas de SLA para um serviço em períodos específicos (semanal, mensal, anual). |
| 66 | [`zabbix_listar_manutencoes`](docs/ferramentas.md#066-zabbix-listar-manutencoes) | `Somente Leitura` | Lista todas as janelas de manutenção cadastradas no Zabbix (ativas, agendadas ou expiradas) com tipo de manutenção (com ou sem coleta de dados) e hosts afetados. |
| 67 | [`zabbix_criar_manutencao`](docs/ferramentas.md#067-zabbix-criar-manutencao) | `Operacional` | Cria uma nova janela de manutenção com horários de início e término estritos, escopo de hosts/grupos e definição se a coleta de dados deve ser mantida ou suspensa. |
| 68 | [`zabbix_atualizar_manutencao`](docs/ferramentas.md#068-zabbix-atualizar-manutencao) | `Operacional` | Modifica o período ou a lista de hosts contemplados em uma janela de manutenção já existente. |
| 69 | [`zabbix_consultar_mapas`](docs/ferramentas.md#069-zabbix-consultar-mapas) | `Somente Leitura` | Recupera as configurações e nós de mapas de topologia visual cadastrados no Zabbix. |
| 70 | [`zabbix_gerar_mapa_monitoramento`](docs/ferramentas.md#070-zabbix-gerar-mapa-monitoramento) | `Somente Leitura` | Gera dinamicamente uma representação gráfica de mapa em formato Markdown/Mermaid a partir dos hosts, grupos e status reais consultados na API do Zabbix. |

### Categoria 8 — Inventário, Grupos e Templates

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 71 | [`zabbix_consultar_inventario`](docs/ferramentas.md#071-zabbix-consultar-inventario) | `Somente Leitura` | Recupera os campos detalhados de inventário de um host (hardware, sistema operacional, localização geográfica, responsável técnico, número de série, vendor, notas). |
| 72 | [`zabbix_atualizar_inventario`](docs/ferramentas.md#072-zabbix-atualizar-inventario) | `Operacional` | Atualiza campos de inventário permitidos de um host (modo de inventário manual/automático, tags, local físico, notas de suporte, etc. |
| 73 | [`zabbix_listar_grupos_hosts`](docs/ferramentas.md#073-zabbix-listar-grupos-hosts) | `Somente Leitura` | Lista todos os grupos de hosts (hostgroups) cadastrados no Zabbix com seus respectivos IDs e nomes. |
| 74 | [`zabbix_gerenciar_grupos_hosts`](docs/ferramentas.md#074-zabbix-gerenciar-grupos-hosts) | `Operacional` | Cria, renomeia ou remove grupos de hosts no Zabbix, validando a não-existência de hosts dependentes antes de qualquer exclusão. |
| 75 | [`zabbix_listar_templates`](docs/ferramentas.md#075-zabbix-listar-templates) | `Somente Leitura` | Lista os templates disponíveis no Zabbix, permitindo filtrar por nome ou grupo de templates. |
| 76 | [`zabbix_consultar_template`](docs/ferramentas.md#076-zabbix-consultar-template) | `Somente Leitura` | Inspeciona profundamente um template específico: itens, triggers, protótipos de descoberta (LLD), gráficos, dashboards e macros herdadas. |
| 77 | [`zabbix_criar_template`](docs/ferramentas.md#077-zabbix-criar-template) | `Operacional` | Cria um novo template no Zabbix com parâmetros validados, associando-o ao grupo de templates adequado. |
| 78 | [`zabbix_atualizar_template`](docs/ferramentas.md#078-zabbix-atualizar-template) | `Operacional` | Atualiza propriedades, nome visível, descrição e macros de um template existente. |
| 79 | [`zabbix_gerenciar_grupos_templates`](docs/ferramentas.md#079-zabbix-gerenciar-grupos-templates) | `Operacional` | Gerencia a criação e listagem de grupos de templates, compatível com a separação entre hostgroups e templategroups introduzida a partir do Zabbix 6. |
| 80 | [`zabbix_auditar_cobertura_templates`](docs/ferramentas.md#080-zabbix-auditar-cobertura-templates) | `Somente Leitura` | Audita todo o Zabbix em busca de falhas de governança: hosts ativos sem nenhum template vinculado, templates órfãos sem nenhum host e discrepâncias de padronização. |

### Categoria 9 — Descoberta Nativa, Proxies e Administração

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 81 | [`zabbix_listar_regras_descoberta`](docs/ferramentas.md#081-zabbix-listar-regras-descoberta) | `Somente Leitura` | Lista as regras nativas de Descoberta de Rede (Network Discovery Rules - drule) configuradas no Zabbix Server/Proxy. |
| 82 | [`zabbix_gerenciar_regras_descoberta`](docs/ferramentas.md#082-zabbix-gerenciar-regras-descoberta) | `Operacional` | Habilita, desabilita ou altera propriedades de regras nativas de descoberta de rede (drule). |
| 83 | [`zabbix_consultar_descoberta_baixo_nivel`](docs/ferramentas.md#083-zabbix-consultar-descoberta-baixo-nivel) | `Somente Leitura` | Consulta as regras LLD (Low-Level Discovery) e protótipos de itens, triggers e gráficos de um host ou template. |
| 84 | [`zabbix_listar_proxies`](docs/ferramentas.md#084-zabbix-listar-proxies) | `Somente Leitura` | Lista todos os proxies de monitoramento distribuído cadastrados no Zabbix, indicando se operam em modo Ativo ou Passivo e seus respectivos status. |
| 85 | [`zabbix_consultar_proxy`](docs/ferramentas.md#085-zabbix-consultar-proxy) | `Somente Leitura` | Inspeciona detalhadamente o estado operacional de um proxy: última comunicação (lastaccess), lista de hosts atribuídos e endereço de conexão. |
| 86 | [`zabbix_gerenciar_proxies`](docs/ferramentas.md#086-zabbix-gerenciar-proxies) | `Administrativo (Exige Aprovação HMAC para exclusão)` | Cadastra, atualiza ou remove configurações de proxies no Zabbix Server. |
| 87 | [`zabbix_consultar_usuarios`](docs/ferramentas.md#087-zabbix-consultar-usuarios) | `Somente Leitura` | Lista os usuários cadastrados no Zabbix com seus respectivos grupos e funções de acesso, com redação automática e mascaramento estrito de senhas ou tokens. |
| 88 | [`zabbix_consultar_funcoes_usuario`](docs/ferramentas.md#088-zabbix-consultar-funcoes-usuario) | `Somente Leitura` | Consulta os papéis de acesso (User Roles) e conjuntos de permissões configurados no Zabbix (Admin, Super Admin, User). |
| 89 | [`zabbix_consultar_auditoria`](docs/ferramentas.md#089-zabbix-consultar-auditoria) | `Somente Leitura` | Consulta os logs de auditoria nativos do Zabbix (Audit Log), registrando quem alterou, criou ou excluiu qualquer objeto no ambiente com IP de origem e timestamp. |
| 90 | [`zabbix_consultar_estado_sistema`](docs/ferramentas.md#090-zabbix-consultar-estado-sistema) | `Somente Leitura` | Recupera a versão da API do Zabbix, nós do cluster de Alta Disponibilidade (HA nodes se habilitado), tamanho da fila de itens atrasados e integridade geral do servidor. |

### Categoria 10 — Automação, Análise e Diagnóstico Holístico

| # | Ferramenta | Nível | Para que serve |
|---|---|---|---|
| 91 | [`zabbix_validar_conexao`](docs/ferramentas.md#091-zabbix-validar-conexao) | `Somente Leitura` | Testa de ponta a ponta a comunicação com a API JSON-RPC do Zabbix: valida resolução de URL, certificado SSL/TLS, conectividade HTTP, autenticação via Token/Bearer e versão suportada. |
| 92 | [`zabbix_converter_pergunta_para_consulta`](docs/ferramentas.md#092-zabbix-converter-pergunta-para-consulta) | `Somente Leitura` | Traduz uma necessidade expressa em linguagem natural (ex: 'Quais servidores Linux tiveram consumo de CPU acima de 90% ontem?') em um plano estruturado de chamadas da API do Zabbix. |
| 93 | [`zabbix_explicar_metricas`](docs/ferramentas.md#093-zabbix-explicar-metricas) | `Somente Leitura` | Analisa estatisticamente a série temporal de um item e gera uma explicação compreensível em linguagem natural: média, volatilidade, desvio padrão, tendência de subida ou descida e limites de segurança. |
| 94 | [`zabbix_comparar_periodos`](docs/ferramentas.md#094-zabbix-comparar-periodos) | `Somente Leitura` | Compara matematicamente o comportamento de uma métrica em dois períodos temporais distintos (ex: hoje vs mesmo dia da semana passada; este mês vs mês anterior), calculando variação percentual. |
| 95 | [`zabbix_detectar_anomalias`](docs/ferramentas.md#095-zabbix-detectar-anomalias) | `Somente Leitura` | Aplica modelos estatísticos de Z-Score sobre os dados históricos da métrica para identificar valores atípicos (outliers) que fogem do comportamento padrão do host. |
| 96 | [`zabbix_planejar_automacao`](docs/ferramentas.md#096-zabbix-planejar-automacao) | `Somente Leitura` | Gera um plano de execução completo passo a passo para automações complexas (onboarding, migração de templates, expurgo de hosts), detalhando pré-requisitos, validações e plano de rollback. |
| 97 | [`zabbix_executar_fluxo_aprovado`](docs/ferramentas.md#097-zabbix-executar-fluxo-aprovado) | `Operacional` | Executa sequencialmente um plano de automação previamente validado e autorizado, com checagem estrita de pré-condições em cada estágio e interrupção segura em caso de imprevisto. |
| 98 | [`zabbix_previsualizar_alteracao`](docs/ferramentas.md#098-zabbix-previsualizar-alteracao) | `Somente Leitura` | Gera uma visualização em formato de Diff (Antes vs Depois) de qualquer alteração proposta em hosts, templates, triggers ou itens, destacando claramente impactos esperados. |
| 99 | [`zabbix_consultar_auditoria_mcp`](docs/ferramentas.md#099-zabbix-consultar-auditoria-mcp) | `Somente Leitura` | Consulta o arquivo local de auditoria (`audit_mcp. |
| 100 | [`zabbix_diagnosticar_ambiente`](docs/ferramentas.md#100-zabbix-diagnosticar-ambiente) | `Somente Leitura` | Produz um diagnóstico holístico 360° do ecossistema Zabbix: valida conectividade da API, saúde da fila de coleta, integridade dos proxies, proporção de problemas críticos e hosts desprotegidos. |


---

## 📂 Estrutura do Repositório

```text
zabbix-mcp-server/
├── src/zabbix_mcp/
│   ├── server.py              # Ponto de entrada FastMCP / MCPServer (100 ferramentas registradas)
│   ├── config.py              # Pydantic Settings e validação de ambiente
│   ├── client.py              # Cliente assíncrono httpx com JSON-RPC 2.0 e retries
│   ├── api_compatibility.py   # Detecção de versão e matriz de recursos
│   ├── models.py              # Contratos Pydantic de entrada e saída (ToolResult)
│   ├── security.py            # Redação de segredos e prevenção de SSRF/Path Traversal
│   ├── authorization.py       # Modos de autorização RBAC
│   ├── policies.py            # Tokens de aprovação HMAC em 2 passos
│   ├── audit.py               # Motor de auditoria local em JSONL
│   ├── discovery/             # Onboarding automatizado em 6 estágios (A ao F)
│   ├── reports/               # Motor de exportação PDF, Excel, CSV, JSON e MD
│   └── tools/                 # As 100 ferramentas divididas em 10 categorias modulares
├── tests/
│   ├── unit/                  # Testes unitários (inventário das 100 ferramentas, RBAC, etc.)
│   └── integration/           # Testes de integração contra Zabbix real
├── docs/                      # 9 Guias detalhados de arquitetura, ferramentas e segurança
│   ├── instalacao.md          # Manual de instalação multi-plataforma
│   ├── configuracao.md        # Tabela completa de variáveis e clientes MCP
│   ├── ferramentas.md         # Manual definitivo das 100 ferramentas com parâmetros
│   └── solucao-de-problemas.md# Guia de troubleshooting e diagnósticos
├── Dockerfile                 # Imagem de produção sem privilégios de root
├── compose.yaml               # Docker Compose com suporte a transporte SSE
└── pyproject.toml             # Metadados e dependências do projeto
```

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
