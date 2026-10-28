.PHONY: help install test lint format clean run docker-build docker-run

help:
	@echo "Zabbix MCP Server - Comandos Disponíveis:"
	@echo "  make install      - Instala dependências em ambiente virtual"
	@echo "  make test         - Executa todos os testes unitários e de integração"
	@echo "  make lint         - Executa verificação de código com ruff"
	@echo "  make format       - Formata o código automaticamente com ruff"
	@echo "  make run          - Executa o servidor MCP via STDIO"
	@echo "  make docker-build - Constrói a imagem Docker oficial"
	@echo "  make docker-run   - Executa o servidor via Docker SSE na porta 8000"

install:
	pip install --upgrade pip
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache reports_output/*.pdf reports_output/*.xlsx

run:
	python -m zabbix_mcp.server --transport stdio

docker-build:
	docker build -t zabbix-mcp-server:latest .

docker-run:
	docker compose up --build
