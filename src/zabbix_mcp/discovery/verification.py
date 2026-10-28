"""
Módulo de Verificação Pós-Cadastro de Dispositivos (Estágio F).
Confirma a integridade dos hosts criados, estado das interfaces, coleta de itens e chegada de métricas.
"""

from typing import Any, Dict, List

from ..client import ZabbixClient


async def verify_onboarded_hosts(
    hostids: List[str],
    client: ZabbixClient
) -> Dict[str, Any]:
    """
    Executa a verificação pós-onboarding (Estágio F).
    Valida se o host existe, se as interfaces estão sem erros e se os itens começaram a coletar.
    """
    if not hostids:
        return {"total_verificados": 0, "hosts": [], "resumo": "Nenhum host informado para verificação"}

    hosts_data = await client.call(
        "host.get",
        params={
            "hostids": hostids,
            "output": ["hostid", "host", "name", "status", "available", "error"],
            "selectInterfaces": ["interfaceid", "ip", "port", "available", "error"],
            "selectItems": ["itemid", "name", "key_", "status", "state", "lastclock", "error"]
        }
    )

    verified_hosts: List[Dict[str, Any]] = []
    total_itens_coletando = 0
    total_itens_com_erro = 0

    for h in hosts_data:
        h_id = h.get("hostid")
        h_name = h.get("name") or h.get("host")
        interfaces = h.get("interfaces", [])
        items = h.get("items", [])

        # Checa status das interfaces
        erros_interface = [i.get("error") for i in interfaces if i.get("error")]

        # Checa itens
        itens_ativos = [i for i in items if str(i.get("status")) == "0"]
        itens_com_dados = [i for i in itens_ativos if i.get("lastclock") and int(i.get("lastclock")) > 0]
        itens_com_erro = [i for i in itens_ativos if i.get("error")]

        total_itens_coletando += len(itens_com_dados)
        total_itens_com_erro += len(itens_com_erro)

        status_geral = "operacional"
        avisos = []

        if erros_interface:
            status_geral = "alerta_interface"
            avisos.append(f"Interface com erro: {erros_interface[0]}")
        elif len(itens_ativos) == 0:
            status_geral = "sem_itens"
            avisos.append("Nenhum item de coleta associado ao host.")
        elif len(itens_com_dados) == 0:
            status_geral = "aguardando_primeira_coleta"
            avisos.append("Itens cadastrados, aguardando ciclo inicial de polling.")

        verified_hosts.append({
            "hostid": h_id,
            "host": h_name,
            "status_geral": status_geral,
            "total_interfaces": len(interfaces),
            "erros_interface": erros_interface,
            "total_itens_ativos": len(itens_ativos),
            "itens_coletando": len(itens_com_dados),
            "itens_com_erro": len(itens_com_erro),
            "avisos": avisos
        })

    return {
        "total_verificados": len(verified_hosts),
        "total_itens_com_metricas": total_itens_coletando,
        "total_itens_com_erro": total_itens_com_erro,
        "hosts": verified_hosts,
        "conclusao": (
            "Dispositivos verificados com sucesso. Itens ativos detectados e ciclos de coleta iniciados."
            if total_itens_coletando > 0 else
            "Dispositivos cadastrados. Algumas métricas ainda estão no primeiro ciclo de coleta ou aguardam resposta do agente."
        )
    }
