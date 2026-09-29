"""PROJETO 07 — Consulta a uma API.

CONCEITO NOVO: buscar dados de fora, com cache temporizado e tratamento de erro.

Duas licoes que separam um app de estudo de um app confiavel:

1. TTL. `@st.cache_data(ttl=...)` guarda a resposta por um tempo e depois
   busca de novo. Sem ttl, uma cotacao ficaria congelada para sempre.

2. A internet falha. Todo acesso externo vai dentro de try/except, e o app
   precisa continuar utilizavel quando a API nao responde.

APIs usadas, todas publicas e sem cadastro:
  - ViaCEP        https://viacep.com.br
  - AwesomeAPI    https://docs.awesomeapi.com.br
  - Open-Meteo    https://open-meteo.com

Como rodar sozinho:
    streamlit run projetos/projeto_07_api.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Consulta a APIs", "🌐")

TEMPO_LIMITE = 8  # segundos


class ErroDeConsulta(Exception):
    """Erro ja traduzido para linguagem de usuario."""


def _buscar(url: str, params: dict | None = None) -> dict:
    """Uma unica porta de entrada para a internet, com erros traduzidos."""
    try:
        resposta = requests.get(url, params=params, timeout=TEMPO_LIMITE)
        resposta.raise_for_status()
        return resposta.json()
    except requests.Timeout:
        raise ErroDeConsulta("O servico demorou demais para responder. Tente de novo.")
    except requests.ConnectionError:
        raise ErroDeConsulta("Sem conexao com a internet, ou o servico esta fora do ar.")
    except requests.HTTPError as e:
        raise ErroDeConsulta(f"O servico respondeu com erro {e.response.status_code}.")
    except ValueError:
        raise ErroDeConsulta("A resposta veio num formato inesperado.")


# --------------------------------------------------------------------------
# CEP — endereco muda raramente: cache longo (24 h)
# --------------------------------------------------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def consultar_cep(cep: str) -> dict:
    limpo = "".join(c for c in cep if c.isdigit())
    if len(limpo) != 8:
        raise ErroDeConsulta("CEP deve ter 8 digitos. Exemplo: 40140-000")

    dados = _buscar(f"https://viacep.com.br/ws/{limpo}/json/")
    if dados.get("erro"):
        raise ErroDeConsulta("CEP nao encontrado. Confira os digitos.")
    return dados


# --------------------------------------------------------------------------
# Cotacao — muda o tempo todo: cache curto (10 min)
# --------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def consultar_cotacao(par: str) -> dict:
    dados = _buscar(f"https://economia.awesomeapi.com.br/json/last/{par}")
    chave = par.replace("-", "")
    if chave not in dados:
        raise ErroDeConsulta("Par de moedas nao reconhecido.")
    return dados[chave]


@st.cache_data(ttl=3600, show_spinner=False)
def historico_cotacao(par: str, dias: int = 30) -> pd.DataFrame:
    dados = _buscar(f"https://economia.awesomeapi.com.br/json/daily/{par}/{dias}")
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["timestamp"].astype(int), unit="s")
    df["valor"] = df["bid"].astype(float)
    return df[["data", "valor"]].sort_values("data").set_index("data")


# --------------------------------------------------------------------------
# Clima — previsao: cache de 30 min
# --------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def consultar_clima(lat: float, lon: float) -> dict:
    return _buscar(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "America/Sao_Paulo",
            "forecast_days": 7,
        },
    )


CIDADES = {
    "Salvador": (-12.97, -38.50),
    "Sao Paulo": (-23.55, -46.63),
    "Rio de Janeiro": (-22.91, -43.17),
    "Brasilia": (-15.79, -47.88),
    "Porto Alegre": (-30.03, -51.23),
    "Manaus": (-3.12, -60.02),
}


def aba_cep() -> None:
    st.subheader("Endereco por CEP")
    cep = st.text_input("CEP", placeholder="40140-000", max_chars=9)

    if not cep:
        st.info("Digite um CEP para consultar.")
        return

    try:
        with st.spinner("Consultando os Correios..."):
            d = consultar_cep(cep)
    except ErroDeConsulta as erro:
        st.error(str(erro))
        return

    st.success(f"{d['logradouro']}, {d['bairro']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Cidade", d["localidade"])
    c2.metric("Estado", d["uf"])
    c3.metric("DDD", d.get("ddd") or "—")

    with st.expander("Resposta completa da API"):
        st.json(d)
    st.caption("Cache de 24 horas: endereco nao muda de um minuto para o outro.")


def aba_cotacao() -> None:
    st.subheader("Cotacao de moedas")
    pares = {"Dolar → Real": "USD-BRL", "Euro → Real": "EUR-BRL",
             "Libra → Real": "GBP-BRL", "Bitcoin → Real": "BTC-BRL"}
    escolha = st.selectbox("Par", list(pares.keys()))
    par = pares[escolha]

    try:
        with st.spinner("Buscando cotacao..."):
            d = consultar_cotacao(par)
    except ErroDeConsulta as erro:
        st.error(str(erro))
        st.caption("O restante do app continua funcionando normalmente.")
        return

    variacao = float(d["pctChange"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Compra", f"R$ {float(d['bid']):,.4f}".replace(",", "X").replace(".", ",").replace("X", "."),
              f"{variacao:+.2f}%")
    c2.metric("Maxima do dia", f"R$ {float(d['high']):,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Minima do dia", f"R$ {float(d['low']):,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.caption(f"Atualizado pela fonte em {d['create_date']} · cache de 10 minutos")

    try:
        st.line_chart(historico_cotacao(par), height=260)
    except ErroDeConsulta:
        st.info("Historico indisponivel no momento.")


def aba_clima() -> None:
    st.subheader("Previsao do tempo")
    cidade = st.selectbox("Cidade", list(CIDADES.keys()))
    lat, lon = CIDADES[cidade]

    try:
        with st.status("Consultando a estacao meteorologica...", expanded=False) as status:
            d = consultar_clima(lat, lon)
            status.update(label="Previsao recebida", state="complete")
    except ErroDeConsulta as erro:
        st.error(str(erro))
        return

    agora = d["current"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperatura", f"{agora['temperature_2m']:.0f} °C")
    c2.metric("Umidade", f"{agora['relative_humidity_2m']:.0f} %")
    c3.metric("Vento", f"{agora['wind_speed_10m']:.0f} km/h")

    diario = pd.DataFrame(
        {
            "data": pd.to_datetime(d["daily"]["time"]),
            "maxima": d["daily"]["temperature_2m_max"],
            "minima": d["daily"]["temperature_2m_min"],
        }
    ).set_index("data")

    st.line_chart(diario, height=260)
    st.caption("Cache de 30 minutos · dados do Open-Meteo")


def main() -> None:
    cabecalho(7, "🌐 Consulta a APIs", "dados externos, cache com ttl e tratamento de falhas")

    st.warning(
        "Este projeto precisa de internet. Se voce estiver offline, as consultas "
        "vao falhar com mensagem clara — que e exatamente o comportamento correto.",
        icon="📡",
    )

    cep, cotacao, clima = st.tabs(["CEP", "Cotacao", "Clima"])
    with cep:
        aba_cep()
    with cotacao:
        aba_cotacao()
    with clima:
        aba_clima()

    rodape([
        "`ttl` define por quanto tempo a resposta fica guardada — cotacao precisa, endereco nao.",
        "Concentre o acesso a rede numa funcao so: um lugar para tratar os erros.",
        "`requests.get(..., timeout=...)` e obrigatorio: sem ele o app pode travar para sempre.",
        "Traduza o erro tecnico para linguagem de usuario antes de mostrar.",
        "`st.spinner` e `st.status` avisam que algo esta acontecendo.",
        "Uma aba que falha nao pode derrubar as outras.",
    ])


main()
