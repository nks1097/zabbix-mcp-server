FROM python:3.12-slim

# Metadados da imagem
LABEL maintainer="Natanael Krindges"
LABEL description="Zabbix MCP Server Universal - 100 Ferramentas em Português"
LABEL version="1.0.0"

# Instalação de dependências de sistema mínimas para compilação segura
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Criação de usuário não privilegiado para execução segura em produção
RUN useradd -u 1000 -m -s /bin/bash appuser

# Instalação do gerenciador de pacotes e dependências
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copia código fonte
COPY src/ /app/src/

# Cria diretórios de saída com permissões adequadas
RUN mkdir -p /app/reports_output && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV ZABBIX_REPORTS_DIR=/app/reports_output
ENV ZABBIX_AUDIT_LOG_PATH=/app/audit_mcp.jsonl

# Padrão: STDIO para conexão com clientes MCP (Claude Desktop, Cursor, Antigravity, etc.)
ENTRYPOINT ["zabbix-mcp"]
CMD ["--transport", "stdio"]

