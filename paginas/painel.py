"""Pagina 2 -- Painel de Automacoes.

Estrutura do arquivo (leia nesta ordem):
    carregar()          -> traz os dados (com cache)
    montar_filtros()    -> desenha a barra lateral e devolve o que foi escolhido
    aplicar_filtros()   -> recorta o DataFrame conforme a escolha
    mostrar_kpis()      -> a fileira de numeros grandes do topo
    aba_visao_geral()   -> os graficos
    aba_detalhes()      -> a tabela e o botao de download
    render()            -> junta tudo, na ordem, e e chamada no fim do arquivo
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dados import ROBOS, STATUS, carregar_execucoes

# Cores fixas por status: o mesmo significado tem sempre a mesma cor,
# em todos os graficos do painel.
COR_STATUS = {"Sucesso": "#2E7D32", "Alerta": "#F9A825", "Falha": "#C62828"}


# --------------------------------------------------------------------------
# 1. Dados
# --------------------------------------------------------------------------
@st.cache_data
def carregar() -> pd.DataFrame:
    """Carrega a base uma unica vez.

    O decorador @st.cache_data e um dos recursos mais importantes do
    Streamlit. Sem ele, o script inteiro roda de novo a cada clique --
    e a base seria recriada toda vez. Com ele, o resultado fica guardado
    na memoria e o app responde instantaneamente.
    """
    return carregar_execucoes()


# --------------------------------------------------------------------------
# 2. Filtros (barra lateral)
# --------------------------------------------------------------------------
def montar_filtros(df: pd.DataFrame) -> dict:
    """Desenha os controles da barra lateral e devolve as escolhas."""
    st.sidebar.header("Filtros")

    data_min = df["data"].min().date()
    data_max = df["data"].max().date()

    periodo = st.sidebar.date_input(
        "Periodo",
        value=(data_max - pd.Timedelta(days=29), data_max),
        min_value=data_min,
        max_value=data_max,
        help="Clique em uma data para o inicio e em outra para o fim.",
    )

    # Enquanto o usuario clicou so na primeira data, o Streamlit devolve
    # uma tupla de um elemento. Sem este tratamento o app quebra.
    if isinstance(periodo, tuple) and len(periodo) == 2:
        inicio, fim = periodo
    else:
        inicio = fim = periodo if not isinstance(periodo, tuple) else periodo[0]

    robos = st.sidebar.multiselect(
        "Robos", options=list(ROBOS.keys()), default=list(ROBOS.keys())
    )
    status = st.sidebar.multiselect("Status", options=STATUS, default=STATUS)

    st.sidebar.divider()
    st.sidebar.caption(
        "Dados ficticios, gerados para estudo. "
        "Troque a funcao `carregar_execucoes` em dados.py pelos seus dados reais."
    )

    return {
        "inicio": pd.Timestamp(inicio),
        "fim": pd.Timestamp(fim),
        "robos": robos,
        "status": status,
    }


def aplicar_filtros(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """Recorta o DataFrame conforme os filtros escolhidos."""
    return df[
        df["data"].between(f["inicio"], f["fim"])
        & df["robo"].isin(f["robos"])
        & df["status"].isin(f["status"])
    ]


def periodo_anterior(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """Mesmo recorte, deslocado para tras -- serve de base de comparacao.

    E o que permite mostrar a setinha verde/vermelha nos KPIs.
    """
    tamanho = f["fim"] - f["inicio"]
    fim = f["inicio"] - pd.Timedelta(days=1)
    inicio = fim - tamanho
    anterior = dict(f, inicio=inicio, fim=fim)
    return aplicar_filtros(df, anterior)


# --------------------------------------------------------------------------
# 3. Indicadores do topo
# --------------------------------------------------------------------------
def _taxa_sucesso(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return (df["status"] == "Sucesso").mean() * 100


def mostrar_kpis(atual: pd.DataFrame, anterior: pd.DataFrame) -> None:
    """Fileira de numeros grandes, cada um com a variacao vs. periodo anterior."""
    c1, c2, c3, c4 = st.columns(4)

    # --- execucoes ---
    n_atual, n_ant = len(atual), len(anterior)
    var = f"{n_atual - n_ant:+d}" if n_ant else None
    c1.metric("Execucoes", f"{n_atual:,}".replace(",", "."), var)

    # --- taxa de sucesso ---
    t_atual, t_ant = _taxa_sucesso(atual), _taxa_sucesso(anterior)
    var = f"{t_atual - t_ant:+.1f} p.p." if n_ant else None
    c2.metric("Taxa de sucesso", f"{t_atual:.1f}%", var)

    # --- horas economizadas ---
    h_atual = atual["min_economizados"].sum() / 60
    h_ant = anterior["min_economizados"].sum() / 60
    var = f"{h_atual - h_ant:+.0f} h" if n_ant else None
    c3.metric("Horas economizadas", f"{h_atual:,.0f} h".replace(",", "."), var)

    # --- duracao media ---
    d_atual = atual["duracao_seg"].mean() if not atual.empty else 0
    d_ant = anterior["duracao_seg"].mean() if not anterior.empty else 0
    var = f"{d_atual - d_ant:+.0f}s" if n_ant else None
    # Aqui menos e melhor: por isso delta_color invertido.
    c4.metric("Duracao media", f"{d_atual:.0f}s", var, delta_color="inverse")


# --------------------------------------------------------------------------
# 4. Abas
# --------------------------------------------------------------------------
def aba_visao_geral(df: pd.DataFrame) -> None:
    st.subheader("Execucoes por dia")
    por_dia = (
        df.pivot_table(index="data", columns="status", values="itens", aggfunc="size")
        .fillna(0)
        .sort_index()
    )
    st.bar_chart(
        por_dia,
        color=[COR_STATUS[c] for c in por_dia.columns],
        height=320,
    )

    esq, dir_ = st.columns(2)

    with esq:
        st.subheader("Horas economizadas por robo")
        por_robo = (
            df.groupby("robo")["min_economizados"].sum().div(60).sort_values()
        )
        st.bar_chart(por_robo, horizontal=True, height=300)

    with dir_:
        st.subheader("Confiabilidade por robo")
        resumo = (
            df.groupby("robo")
            .agg(
                execucoes=("status", "size"),
                sucesso=("status", lambda s: (s == "Sucesso").mean()),
                duracao=("duracao_seg", "mean"),
            )
            .sort_values("sucesso")
        )
        # column_config transforma numeros crus em barras e formatos legiveis.
        st.dataframe(
            resumo,
            height=300,
            column_config={
                "execucoes": st.column_config.NumberColumn("Execucoes"),
                "sucesso": st.column_config.ProgressColumn(
                    "Sucesso", format="%.0f%%", min_value=0, max_value=1
                ),
                "duracao": st.column_config.NumberColumn("Duracao", format="%.0f s"),
            },
        )

    st.subheader("Distribuicao ao longo do dia")
    por_hora = df.groupby("hora").size().reindex(range(24), fill_value=0)
    st.area_chart(por_hora, height=220)


def aba_detalhes(df: pd.DataFrame) -> None:
    st.subheader("Registros filtrados")

    apenas_falhas = st.toggle("Mostrar apenas falhas")
    tabela = df[df["status"] == "Falha"] if apenas_falhas else df

    st.dataframe(
        tabela,
        height=430,
        hide_index=True,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "hora": st.column_config.NumberColumn("Hora", format="%d h"),
            "robo": "Robo",
            "status": "Status",
            "duracao_seg": st.column_config.NumberColumn("Duracao", format="%.0f s"),
            "itens": st.column_config.NumberColumn("Itens"),
            "min_economizados": st.column_config.NumberColumn("Economia", format="%d min"),
        },
    )

    st.download_button(
        "Baixar em CSV",
        data=tabela.to_csv(index=False).encode("utf-8-sig"),
        file_name="execucoes.csv",
        mime="text/csv",
        icon=":material/download:",
    )


# --------------------------------------------------------------------------
# 5. Montagem da pagina
# --------------------------------------------------------------------------
def render() -> None:
    st.title("🤖 Painel de Automacoes")
    st.caption("Acompanhamento das rotinas automatizadas -- dados de exemplo")

    df = carregar()
    filtros = montar_filtros(df)
    atual = aplicar_filtros(df, filtros)

    # Sem este bloco, um filtro vazio geraria erros feios nos graficos.
    if atual.empty:
        st.warning("Nenhuma execucao no recorte escolhido. Ajuste os filtros ao lado.")
        st.stop()

    mostrar_kpis(atual, periodo_anterior(df, filtros))
    st.divider()

    visao, detalhes = st.tabs(["Visao geral", "Detalhes"])
    with visao:
        aba_visao_geral(atual)
    with detalhes:
        aba_detalhes(atual)


# Paginas nao usam `if __name__`: o Streamlit executa o arquivo
# inteiro toda vez que a pagina e aberta.
render()
