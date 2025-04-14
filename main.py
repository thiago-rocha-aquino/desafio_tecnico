import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs

# dando get para obter codigo e foro (manualmenter)
def obter_codigo_e_foro(numero_processo):
    url = f"https://esaj.tjsp.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado=&foroNumeroUnificado=&dadosConsulta.valorConsultaNuUnificado=&dadosConsulta.valorConsultaNuUnificado=UNIFICADO&dadosConsulta.valorConsulta={numero_processo}&dadosConsulta.tipoNuProcesso=SAJ"

    response = requests.get(url, allow_redirects=True)

    final_url = response.url
    parsed_url = urlparse(final_url)
    query_params = parse_qs(parsed_url.query)
    codigo = query_params.get("processo.codigo", [None])[0]
    foro = query_params.get("processo.foro", [None])[0]

    return codigo, foro
# Obtém os dados do processo com base no número fornecido
def obter_dados_processo(numero_processo):
    codigo, foro = obter_codigo_e_foro(numero_processo)

    if not codigo or not foro:
        return {"processo": numero_processo, "erro": "Código ou foro não encontrados"}

    url = f"https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo={codigo}&processo.foro={foro}&processo.numero={numero_processo}"

    response = requests.get(url)
    if response.status_code != 200:
        return {"processo": numero_processo, "erro": "Falha na requisição"}

    soup = BeautifulSoup(response.text, "html.parser")
    movimentacoes = soup.select("#tabelaUltimasMovimentacoes tr")

    if not movimentacoes:
        return {"processo": numero_processo, "erro": "Nenhuma movimentação encontrada"}

    primeira_movimentacao = movimentacoes[0].select("td")
    
    data_movimentacao = primeira_movimentacao[0].text.strip() if primeira_movimentacao else "Indisponível"

    return {
        "processo": numero_processo,
        "data_ultima_movimentacao": data_movimentacao
    }

# Lista de processos
processos = [
    "1000903-10.2022.8.26.0014",
    "1002092-86.2023.8.26.0014",
    "1003054-05.2023.8.26.0566",
    "1001270-97.2023.8.26.0014",
    "1001288-21.2023.8.26.0014"
]

# Obtendo os dados e retornando um JSON formatado
resultado = [obter_dados_processo(processo) for processo in processos]

# Convertendo para JSON e imprimindo
json_resultado = json.dumps(resultado, indent=4, ensure_ascii=False)
print(json_resultado)
