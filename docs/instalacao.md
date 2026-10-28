# Guia Completo de Instalação do Zabbix MCP Server

Este guia orienta a instalação e inicialização do **Zabbix MCP Server** em ambientes corporativos e de desenvolvimento, suportando **Windows**, **Linux**, **macOS** e **Docker**.

---

## 1. Pré-Requisitos do Sistema

Antes de iniciar, certifique-se de ter:
1. **Python:** Versão `3.11`, `3.12` ou superior instalada (`python --version` ou `python3 --version`).
2. **Git:** Instalado e configurado no PATH do sistema (`git --version`).
3. **Instância Zabbix Ativa:** Versão 6.0 LTS, 6.4, 7.0 LTS ou 7.4+ acessível pela rede local ou internet (ex: `http://192.168.0.107:8080/api_jsonrpc.php`).
4. **Token de API ou Credenciais:** Um usuário Zabbix com privilégios adequados (veja o Passo 2 abaixo).

---

## 2. Como Gerar o Token de API no Zabbix (Passo a Passo)

Recomendamos o uso de **Token de API** (Zabbix 5.4+) por ser mais seguro, imutável e dispensar o armazenamento de senhas em texto puro.

1. Acesse o frontend web do seu Zabbix no navegador.
2. No menu lateral esquerdo, vá em:
   - **Zabbix 6.x / 7.x:** **Administração** (`Administration`) ➔ **Tokens de API** (`API tokens`)
   - *(Ou no perfil do usuário no canto superior direito ➔ Tokens de API)*.
3. Clique no botão azul **Criar token de API** (`Create API token`) no canto superior direito.
4. Preencha os campos:
   - **Nome:** `Zabbix-MCP-Server-Token`
   - **Usuário:** Selecione o usuário com permissões de monitoramento (ex: `Admin`).
   - **Expira em:** Deixe desmarcado para token permanente ou defina a data limite desejada.
   - **Descrição:** `Token utilizado pelo servidor MCP para automação e relatórios`.
5. Clique em **Adicionar** (`Add`).
6. **MUITO IMPORTANTE:** Copie a chave de autenticação exibida na tela pop-up (uma cadeia de 64 caracteres hexadecimais, ex: `3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45`).
   > [!WARNING]
   > Essa chave só é exibida uma única vez. Guarde-a em local seguro.

---

## 3. Instalação no Windows (PowerShell)

### Passo 3.1: Liberar Política de Execução do PowerShell
Por padrão de segurança, o Windows pode bloquear a ativação de ambientes virtuais (`running scripts is disabled on this system`). Para liberar apenas para o seu usuário:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
*(Digite `S` para confirmar quando solicitado).*

### Passo 3.2: Clonar o Repositório
```powershell
git clone https://github.com/nks1097/zabbix-mcp-server.git
cd zabbix-mcp-server
```

### Passo 3.3: Criar e Ativar o Ambiente Virtual
```powershell
python -m venv .venv
.\.venv\Scriptsctivate
```
*(O prefixo `(.venv)` aparecerá no início da linha de comando).*

### Passo 3.4: Instalar as Dependências
```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 4. Instalação no Linux e macOS

### Passo 4.1: Atualizar Pacotes do Sistema
No Ubuntu/Debian:
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git curl
```
No RHEL / Rocky / AlmaLinux:
```bash
sudo dnf install -y python3 python3-pip git
```

### Passo 4.2: Clonar e Configurar o Virtualenv
```bash
git clone https://github.com/nks1097/zabbix-mcp-server.git
cd zabbix-mcp-server

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 5. Configuração do Arquivo `.env`

Copie o arquivo de exemplo `.env.example` para `.env`:

**No Windows:**
```powershell
copy .env.example .env
```

**No Linux / macOS:**
```bash
cp .env.example .env
```

Abra o arquivo `.env` em seu editor preferido (`notepad .env` ou `nano .env`) e configure os parâmetros da sua infraestrutura:

```ini
# ==============================================================================
# CONFIGURAÇÃO DE CONEXÃO COM O ZABBIX
# ==============================================================================
# URL completa do endpoint da API Zabbix (JSON-RPC)
ZABBIX_URL=http://192.168.0.107:8080/api_jsonrpc.php

# Token de API do Zabbix (Recomendado)
ZABBIX_TOKEN=3752dc4ae3d95027e4ce06e1ed28b2ba57f4e7902357b7eb9e2dae109bf02d45

# Credenciais legadas (utilizadas apenas se ZABBIX_TOKEN estiver em branco)
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# Validação SSL/TLS (defina false para certificados autoassinados ou HTTP local)
ZABBIX_VERIFY_SSL=false

# Timeout em segundos para chamadas HTTP
ZABBIX_TIMEOUT=30.0

# ==============================================================================
# GOVERNANÇA, RBAC E SEGURANÇA
# ==============================================================================
# Nível de autorização: 'somente_leitura', 'operacional' ou 'administrativo'
ZABBIX_MCP_MODE=operacional

# Exigir aprovação em 2 passos para ações destrutivas (excluir hosts/proxies)
ZABBIX_REQUIRE_APPROVAL_DESTRUCTIVE=true

# Chave secreta HMAC para assinatura de tokens de aprovação
ZABBIX_APPROVAL_TOKEN_SECRET=sua-chave-secreta-corporativa-muito-forte

# ==============================================================================
# DIRETÓRIOS E LOGS
# ==============================================================================
ZABBIX_REPORTS_DIR=./reports_output
ZABBIX_AUDIT_LOG_PATH=./audit_mcp.jsonl
```

---

## 6. Teste de Conectividade e Validação

Para certificar que o ambiente está configurado perfeitamente antes de integrar aos clientes de IA, execute a suíte de testes:

```bash
# 1. Executar testes unitários (offline)
pytest tests/unit -v

# 2. Executar testes de integração ao vivo contra o seu Zabbix
pytest tests/integration/test_live_zabbix.py -v
```
Se todos os testes passarem (`PASSED`), o servidor está 100% pronto para uso em produção.

---

## 7. Execução do Servidor MCP

### Opção A: Modo STDIO (Padrão para IDEs e Assistentes de IA)
Usado por Claude Desktop, Cursor, Antigravity IDE, VS Code, Roo Code e Cline:
```bash
python -m zabbix_mcp.server --transport stdio
```

### Opção B: Modo SSE (Server-Sent Events via HTTP)
Usado para expor o servidor MCP como um microsserviço de rede em containers, Kubernetes ou servidores remotos:
```bash
python -m zabbix_mcp.server --transport sse --host 0.0.0.0 --port 8000
```

---

## 8. Execução via Docker e Docker Compose

Se preferir rodar em containers isolados:

```bash
# 1. Configurar o .env
cp .env.example .env
nano .env

# 2. Iniciar o container em segundo plano
docker compose up -d

# 3. Verificar os logs
docker compose logs -f zabbix-mcp

# 4. Testar o endpoint SSE
curl -I http://localhost:8000/sse
```
