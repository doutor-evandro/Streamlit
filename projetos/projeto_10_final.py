"""PROJETO 10 — Central de Automacoes (projeto final integrado).

CONCEITO NOVO: integracao e desempenho.

Este projeto junta tudo o que veio antes — widgets, layout, session_state,
formulario, upload, cache, API, banco e acesso protegido — e acrescenta a
peca que faltava: `st.fragment`.

`st.fragment` e a resposta madura para a limitacao que voce conheceu no
Projeto 01. Uma funcao decorada com ele reroda SOZINHA, sem reexecutar o
arquivo inteiro. E o que permite um relogio que atualiza a cada segundo sem
recarregar a pagina toda.

Como rodar sozinho:
    streamlit run projetos/projeto_10_final.py
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Central de Automacoes", "🎛️", "wide")

BANCO = Path(__file__).resolve().parent.parent / "dados_projeto10.db"
ROBOS = ["Conciliacao bancaria", "Emissao de notas", "Backup", "Relatorio diario"]
SITUACOES = ["Sucesso", "Alerta", "Falha"]


# ==========================================================================
# Dados — banco (Projeto 08) e base analitica com cache (Projeto 06)
# ==========================================================================
@st.cache_resource
def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(BANCO, check_same_thread=False)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS execucoes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            quando   TEXT NOT NULL,
            robo     TEXT NOT NULL,
            situacao TEXT NOT NULL,
            duracao  REAL NOT NULL,
            nota     TEXT
        )
        """
    )
    con.commit()
    return con


def registrar(robo: str, situacao: str, duracao: float, nota: str) -> None:
    con = conectar()
    con.execute(
        "INSERT INTO execucoes (quando, robo, situacao, duracao, nota) VALUES (?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), robo, situacao, duracao, nota.strip()),
    )
    con.commit()


def historico() -> pd.DataFrame:
    df = pd.read_sql_query("SELECT * FROM execucoes ORDER BY quando DESC", conectar())
    if not df.empty:
        df["quando"] = pd.to_datetime(df["quando"])
    return df


@st.cache_data(ttl=300, show_spinner="Carregando base analitica...")
def base_analitica(dias: int = 60, semente: int = 3) -> pd.DataFrame:
    """Historico simulado, com cache de 5 minutos."""
    rng = np.random.default_rng(semente)
    fim = pd.Timestamp.today().normalize()
    linhas = []
    for dia in pd.date_range(fim - pd.Timedelta(days=dias - 1), fim, freq="D"):
        for robo in ROBOS:
            for _ in range(int(rng.poisson(4)) + 1):
                situacao = rng.choice(SITUACOES, p=[0.88, 0.07, 0.05])
                linhas.append(
                    {
                        "data": dia,
                        "robo": robo,
                        "situacao": situacao,
                        "duracao": round(abs(rng.normal(90, 30)), 1),
                        "economia": 0 if situacao == "Falha" else int(rng.integers(5, 40)),
                    }
                )
    return pd.DataFrame(linhas)


# ==========================================================================
# Fragmento — reroda sozinho, sem reexecutar a pagina inteira
# ==========================================================================
@st.fragment(run_every=2)
def painel_ao_vivo() -> None:
    """Atualiza a cada 2 segundos. O resto da pagina NAO reroda.

    Este e o recurso que resolve a limitacao do Projeto 01.
    """
    agora = datetime.now()
    c1, c2, c3 = st.columns(3)
    c1.metric("Horario do servidor", agora.strftime("%H:%M:%S"))
    c2.metric("Proxima execucao", (agora + timedelta(minutes=17)).strftime("%H:%M"))
    # Valor que oscila so para tornar a atualizacao visivel.
    c3.metric("Fila", f"{(agora.second % 5)} tarefa(s)")
    st.caption("Este bloco se atualiza sozinho. Repare que o resto da tela fica parado.")


# ==========================================================================
# Abas
# ==========================================================================
def aba_visao_geral() -> None:
    df = base_analitica()

    robos = st.multiselect("Robos", ROBOS, default=ROBOS)
    dados = df[df["robo"].isin(robos)]
    if dados.empty:
        st.warning("Selecione ao menos um robo.")
        return

    sucesso = (dados["situacao"] == "Sucesso").mean() * 100
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Execucoes", f"{len(dados):,}".replace(",", "."))
    c2.metric("Taxa de sucesso", f"{sucesso:.1f}%")
    c3.metric("Horas economizadas", f"{dados['economia'].sum() / 60:,.0f} h".replace(",", "."))
    c4.metric("Duracao media", f"{dados['duracao'].mean():.0f}s")

    st.divider()
    por_dia = (
        dados.pivot_table(index="data", columns="situacao", values="duracao", aggfunc="size")
        .fillna(0).sort_index()
    )
    st.bar_chart(por_dia, height=300)

    esq, dir_ = st.columns(2)
    esq.subheader("Economia por robo")
    esq.bar_chart(dados.groupby("robo")["economia"].sum().div(60).sort_values(),
                  horizontal=True, height=260)
    dir_.subheader("Confiabilidade")
    dir_.dataframe(
        dados.groupby("robo").agg(
            execucoes=("situacao", "size"),
            sucesso=("situacao", lambda s: (s == "Sucesso").mean()),
        ),
        height=260,
        column_config={
            "execucoes": st.column_config.NumberColumn("Execucoes"),
            "sucesso": st.column_config.ProgressColumn("Sucesso", format="%.0f%%",
                                                       min_value=0, max_value=1),
        },
    )


def aba_registrar() -> None:
    st.subheader("Registrar execucao")

    with st.form("registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        robo = c1.selectbox("Robo *", ROBOS)
        situacao = c2.selectbox("Situacao *", SITUACOES)
        duracao = st.number_input("Duracao (segundos) *", min_value=0.0, value=60.0, step=5.0)
        nota = st.text_area("Observacao", max_chars=200)

        if st.form_submit_button("Registrar", type="primary", width="stretch"):
            registrar(robo, situacao, duracao, nota)
            st.toast("Execucao registrada", icon="✅")

    df = historico()
    if df.empty:
        st.info("Nenhuma execucao registrada ainda.")
        return

    st.divider()
    st.subheader(f"Registros gravados ({len(df)})")
    st.dataframe(
        df, hide_index=True, width="stretch", height=280,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "quando": st.column_config.DatetimeColumn("Quando", format="DD/MM/YYYY HH:mm"),
            "duracao": st.column_config.NumberColumn("Duracao", format="%.0f s"),
        },
    )
    st.download_button(
        "Baixar CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="execucoes.csv", mime="text/csv",
    )
    st.caption("Lembre: no Community Cloud este banco some quando o app hiberna.")


def aba_importar() -> None:
    st.subheader("Importar planilha")
    arquivo = st.file_uploader("CSV ou Excel", type=["csv", "xlsx"])

    if arquivo is None:
        st.info("Envie um arquivo para ver o resumo automatico.")
        return

    try:
        df = pd.read_excel(arquivo) if arquivo.name.endswith("x") else pd.read_csv(arquivo)
    except Exception as erro:
        st.error("Nao consegui ler este arquivo.")
        st.caption(f"Detalhe: {erro}")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Linhas", f"{len(df):,}".replace(",", "."))
    c2.metric("Colunas", df.shape[1])
    c3.metric("Celulas vazias", int(df.isna().sum().sum()))

    st.dataframe(df.head(50), width="stretch", height=300)

    numericas = df.select_dtypes("number").columns
    if len(numericas):
        coluna = st.selectbox("Coluna para o grafico", numericas)
        st.line_chart(df[coluna].head(200), height=240)


def aba_restrito() -> None:
    st.session_state.setdefault("liberado", False)

    try:
        senha_certa = st.secrets["app"]["senha"]
        configurado = True
    except Exception:
        senha_certa, configurado = "trilha2026", False

    if not st.session_state.liberado:
        st.subheader("🔒 Configuracoes restritas")
        if not configurado:
            st.warning(f"Sem secrets configurado — senha padrao: **{senha_certa}**", icon="⚠️")

        with st.form("entrar"):
            digitada = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if digitada == senha_certa:
                    st.session_state.liberado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
        return

    topo, sair = st.columns([3, 1])
    topo.success("Area liberada.")
    if sair.button("Sair", width="stretch"):
        st.session_state.liberado = False
        st.rerun()

    st.divider()
    st.subheader("Manutencao")

    c1, c2 = st.columns(2)
    if c1.button("Limpar cache analitico", width="stretch"):
        base_analitica.clear()
        st.success("Cache esvaziado. Os dados serao recarregados.")
    if c2.button("Apagar todos os registros", width="stretch"):
        conectar().execute("DELETE FROM execucoes")
        conectar().commit()
        st.success("Registros apagados.")
        st.rerun()


def main() -> None:
    cabecalho(10, "🎛️ Central de Automacoes", "integracao de tudo + `st.fragment`")

    st.sidebar.header("Central")
    st.sidebar.caption(
        "Projeto final da trilha. Reune os nove anteriores num app so — "
        "e acrescenta o `st.fragment`."
    )
    st.sidebar.divider()
    st.sidebar.markdown(
        "**Origem de cada peca**\n\n"
        "- Layout e abas — Projeto 02\n"
        "- Memoria de sessao — Projeto 03\n"
        "- Formulario — Projeto 04\n"
        "- Upload — Projeto 05\n"
        "- Cache e graficos — Projeto 06\n"
        "- Banco de dados — Projeto 08\n"
        "- Acesso protegido — Projeto 09"
    )

    painel_ao_vivo()
    st.divider()

    visao, registro, importar, restrito = st.tabs(
        ["Visao geral", "Registrar", "Importar", "Restrito"]
    )
    with visao:
        aba_visao_geral()
    with registro:
        aba_registrar()
    with importar:
        aba_importar()
    with restrito:
        aba_restrito()

    rodape([
        "`@st.fragment(run_every=...)` reroda so aquele bloco — o resto da pagina fica parado.",
        "Um app real combina varias fontes: memoria, banco, arquivo e API.",
        "`st.cache_data` para dados; `st.cache_resource` para conexoes.",
        "Abas mantem o app navegavel conforme ele cresce.",
        "Area restrita vem depois da checagem, nunca antes.",
        "Daqui em diante o limite deixa de ser o Streamlit e passa a ser a arquitetura.",
    ])


main()
