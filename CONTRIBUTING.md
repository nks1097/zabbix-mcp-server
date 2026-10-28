# Guia de Contribuição — Zabbix MCP Server

Agradecemos o interesse em contribuir com o **Zabbix MCP Server**!

## Diretrizes de Desenvolvimento

1. **Linguagem e Idioma:**
   - O código, commits e docstrings das ferramentas devem manter o português claro e padronizado para as 100 ferramentas MCP.
   - Nomes de funções e variáveis internas seguem convenções Python (`snake_case`).
2. **Ambiente Local:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
   pip install -e ".[dev]"
   ```
3. **Padrão de Código:**
   - Execute `ruff check src tests` antes de abrir Pull Requests.
   - Formate o código com `ruff format src tests`.
4. **Testes Obrigatórios:**
   - Todos os PRs devem passar na suíte de testes unitários:
     ```bash
     pytest -v
     ```
   - O teste `tests/unit/test_inventory.py` valida que nenhuma ferramenta obrigatória seja renomeada ou removida acidentalmente.
5. **Processo de Pull Request:**
   - Crie uma branch descritiva: `git checkout -b feature/suporte-zabbix-7-2` ou `fix/tratamento-timeout`.
   - Adicione testes unitários para qualquer nova funcionalidade ou correção.
   - Abra o Pull Request detalhando as alterações e referenciando a issue relacionada.
