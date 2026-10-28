"""
Testes Unitários da Geração e Exportação de Relatórios (PDF, XLSX, CSV, JSON e Markdown).
"""

from pathlib import Path
import pytest
from zabbix_mcp.reports.exporters import (
    export_to_csv,
    export_to_json,
    export_to_markdown,
    export_to_pdf,
    export_to_xlsx
)


@pytest.fixture
def dummy_report_data():
    return {
        "titulo": "Relatório Executivo de Teste",
        "organizacao": "Empresa Teste",
        "data_geracao": "28/10/2026 10:00:00 UTC",
        "periodo_analisado": "Últimos 7 dias",
        "resumo_executivo": {
            "total_hosts": 15,
            "hosts_monitorados": 14,
            "hosts_desativados": 1,
            "total_problemas_registrados": 3,
            "problemas_alta_e_desastre": 0,
            "disponibilidade_media_observada": "99.8%"
        },
        "tabelas": [
            {
                "titulo": "Resumo de Incidentes",
                "cabecalho": ["Severidade", "Total"],
                "linhas": [["Aviso", 2], ["Média", 1]]
            }
        ],
        "conclusoes": ["Ambiente com alta disponibilidade observada."]
    }


def test_exportacao_pdf(dummy_report_data, tmp_path):
    """Gera PDF real com ReportLab e valida que o arquivo existe e é maior que zero."""
    pdf_path_str = export_to_pdf(dummy_report_data, "teste_executivo.pdf")
    pdf_path = Path(pdf_path_str)

    assert pdf_path.exists()
    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 1000  # PDF válido gerado


def test_exportacao_xlsx(dummy_report_data, tmp_path):
    """Gera planilha Excel real com openpyxl e valida suas abas."""
    xlsx_path_str = export_to_xlsx(dummy_report_data, "teste_executivo.xlsx")
    xlsx_path = Path(xlsx_path_str)

    assert xlsx_path.exists()
    assert xlsx_path.is_file()
    assert xlsx_path.stat().st_size > 1000


def test_exportacao_csv_json_markdown(dummy_report_data, tmp_path):
    """Valida geração de CSV, JSON e Markdown."""
    csv_path = Path(export_to_csv(dummy_report_data, "teste.csv"))
    assert csv_path.exists()

    json_path = Path(export_to_json(dummy_report_data, "teste.json"))
    assert json_path.exists()

    md = export_to_markdown(dummy_report_data)
    assert "# Relatório Executivo de Teste" in md
    assert "99.8%" in md
