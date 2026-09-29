"""PROJETO 06 — Painel de vendas.

CONCEITO NOVO: @st.cache_data e graficos.

O problema que o cache resolve: como o script roda inteiro a cada clique,
ler a base do disco tambem aconteceria a cada clique. Com 50 mil linhas,
o app fica lento e a memoria do servidor sofre.

`@st.cache_data` guarda o resultado da funcao. Na segunda chamada com os
mesmos argumentos, ela nem executa — devolve o que ja estava guardado.
E o cache e COMPARTILHADO entre todos os visitantes, nao por sessao. E por
isso que ele determina quantas pessoas seu app aguenta ao mesmo tempo.

Como rodar sozinho:
    streamlit run projetos/projeto_06_painel.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Painel de vendas", "📊", "wide")

REGIOES = ["Nordeste", "Sudeste", "Sul", "Centro-Oeste", "Norte"]
CATEGORIAS = ["Mobiliario", "Iluminacao", "Acessorios", "Servicos"]
CANAIS = ["Loja fisica", "E-commerce", "Representante"]

COR = {"Mobiliario": "#0A6A78", "Iluminacao": "#C88A2E", "Acessorios": "#4C6B8A", "Servicos": "#7A5C8A"}


@st.cache_data(show_spinner="Carregando a base...")
def carregar(dias: int = 365, semente: int = 7) -> pd.DataFrame:
    """Gera a base de vendas.

    Com dados reais, esta funcao seria:
        return pd.read_excel("vendas.xlsx")
    O resto do arquivo nao mudaria nada.
    """
    rng = np.random.default_rng(semente)
    fim = pd.Timestamp.today().normalize()
    datas = pd.date_range(fim - pd.Timedelta(days=dias - 1), fim, freq="D")

    linhas = []
    for dia in datas:
        # Fim de semana vende menos; dezembro vende mais.
        fator = 0.45 if dia.weekday() >= 5 else 1.0
        fator *= 1.6 if dia.month == 12 else 1.0

        for _ in range(int(rng.poisson(9 * fator)) + 1):
            categoria = rng.choice(CATEGORIAS, p=[0.35, 0.25, 0.30, 0.10])
            base = {"Mobiliario": 1800, "Iluminacao": 420, "Acessorios": 160, "Servicos": 950}[categoria]
            qtd = int(rng.integers(1, 5))
            preco = abs(rng.normal(base, base * 0.22))

            linhas.append(
                {
                    "data": dia,
                    "regiao": rng.choice(REGIOES, p=[0.22, 0.34, 0.18, 0.15, 0.11]),
                    "categoria": categoria,
                    "canal": rng.choice(CANAIS, p=[0.40, 0.45, 0.15]),
                    "quantidade": qtd,
                    "faturamento": round(preco * qtd, 2),
                }
            )

    return pd.DataFrame(linhas).sort_values("data").reset_index(drop=True)


def filtrar(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    return df[
        df["data"].between(f["inicio"], f["fim"])
        & df["regiao"].isin(f["regioes"])
        & df["categoria"].isin(f["categorias"])
        & df["canal"].isin(f["canais"])
    ]


def periodo_anterior(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """Mesmo recorte, deslocado para tras — a base de comparacao dos KPIs."""
    tamanho = f["fim"] - f["inicio"]
    fim = f["inicio"] - pd.Timedelta(days=1)
    return filtrar(df, dict(f, inicio=fim - tamanho, fim=fim))


def moeda(valor: float) -> str:
    return f"R$ {valor:,.0f}".replace(",", ".")


def main() -> None:
    cabecalho(6, "📊 Painel de vendas", "`@st.cache_data` e graficos")

    df = carregar()

    # ---------------- filtros ----------------
    st.sidebar.header("Filtros")
    data_min, data_max = df["data"].min().date(), df["data"].max().date()

    periodo = st.sidebar.date_input(
        "Periodo",
        value=(data_max - pd.Timedelta(days=89), data_max),
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY",
    )
    # Enquanto so a primeira data foi clicada, vem uma tupla de 1 elemento.
    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio = fim = periodo[0] if isinstance(periodo, tuple) else periodo

    filtros = {
        "inicio": pd.Timestamp(inicio),
        "fim": pd.Timestamp(fim),
        "regioes": st.sidebar.multiselect("Regiao", REGIOES, default=REGIOES),
        "categorias": st.sidebar.multiselect("Categoria", CATEGORIAS, default=CATEGORIAS),
        "canais": st.sidebar.multiselect("Canal", CANAIS, default=CANAIS),
    }

    st.sidebar.divider()
    if st.sidebar.button("Limpar cache e recarregar", width="stretch"):
        carregar.clear()
        st.rerun()
    st.sidebar.caption("Use o botao acima para ver a diferenca que o cache faz.")

    atual = filtrar(df, filtros)
    if atual.empty:
        st.warning("Nenhuma venda no recorte escolhido. Ajuste os filtros ao lado.")
        st.stop()

    anterior = periodo_anterior(df, filtros)

    # ---------------- indicadores ----------------
    def delta(a: float, b: float, sufixo: str = "") -> str | None:
        if not len(anterior):
            return None
        return f"{a - b:+,.0f}{sufixo}".replace(",", ".")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", moeda(atual["faturamento"].sum()),
              delta(atual["faturamento"].sum(), anterior["faturamento"].sum()))
    c2.metric("Pedidos", f"{len(atual):,}".replace(",", "."),
              delta(len(atual), len(anterior)))
    c3.metric("Ticket medio", moeda(atual["faturamento"].mean()),
              delta(atual["faturamento"].mean(), anterior["faturamento"].mean() if len(anterior) else 0))
    c4.metric("Itens vendidos", f"{int(atual['quantidade'].sum()):,}".replace(",", "."),
              delta(atual["quantidade"].sum(), anterior["quantidade"].sum()))

    st.caption("A variacao compara com o periodo anterior de mesmo tamanho.")
    st.divider()

    # ---------------- graficos ----------------
    st.subheader("Faturamento por dia")
    por_dia = (
        atual.pivot_table(index="data", columns="categoria", values="faturamento", aggfunc="sum")
        .fillna(0)
        .sort_index()
    )
    st.bar_chart(por_dia, color=[COR[c] for c in por_dia.columns], height=330)

    esq, dir_ = st.columns(2)

    with esq:
        st.subheader("Por regiao")
        por_regiao = atual.groupby("regiao")["faturamento"].sum().sort_values()
        st.bar_chart(por_regiao, horizontal=True, height=300)

    with dir_:
        st.subheader("Desempenho por categoria")
        resumo = (
            atual.groupby("categoria")
            .agg(pedidos=("faturamento", "size"),
                 faturamento=("faturamento", "sum"),
                 ticket=("faturamento", "mean"))
            .sort_values("faturamento", ascending=False)
        )
        st.dataframe(
            resumo,
            height=300,
            column_config={
                "pedidos": st.column_config.NumberColumn("Pedidos"),
                "faturamento": st.column_config.ProgressColumn(
                    "Faturamento", format="R$ %.0f",
                    min_value=0, max_value=float(resumo["faturamento"].max()),
                ),
                "ticket": st.column_config.NumberColumn("Ticket", format="R$ %.0f"),
            },
        )

    st.subheader("Media movel de 7 dias")
    serie = atual.groupby("data")["faturamento"].sum().sort_index()
    st.line_chart(
        pd.DataFrame({"diario": serie, "media 7d": serie.rolling(7, min_periods=1).mean()}),
        height=260,
    )

    with st.expander("Registros filtrados"):
        st.dataframe(
            atual, hide_index=True, height=300, width="stretch",
            column_config={
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "faturamento": st.column_config.NumberColumn("Faturamento", format="R$ %.2f"),
            },
        )
        st.download_button(
            "Baixar CSV",
            data=atual.to_csv(index=False).encode("utf-8-sig"),
            file_name="vendas_filtradas.csv",
            mime="text/csv",
        )

    rodape([
        "`@st.cache_data` guarda o resultado — a funcao nem roda na 2a vez.",
        "O cache e compartilhado entre visitantes: e ele que define a escala do app.",
        "`funcao.clear()` esvazia o cache daquela funcao.",
        "Isolar a leitura numa funcao permite trocar dados ficticios por reais sem mexer no resto.",
        "`pivot_table` prepara o formato que os graficos nativos esperam.",
        "`st.column_config.ProgressColumn` transforma numero em barra dentro da tabela.",
    ])


main()
