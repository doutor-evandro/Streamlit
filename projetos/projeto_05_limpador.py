"""PROJETO 05 — Limpador de planilhas.

CONCEITO NOVO: receber arquivo do usuario e devolver arquivo pronto.

Aqui o app deixa de ser exercicio e vira ferramenta: e o primeiro que voce
pode mandar para outra pessoa usar de verdade.

Duas licoes de robustez:
  1. Sempre trate o caso "nenhum arquivo enviado ainda" com st.stop().
  2. Sempre trate o arquivo corrompido ou no formato errado com try/except.

Como rodar sozinho:
    streamlit run projetos/projeto_05_limpador.py
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Limpador de planilhas", "🧹", "wide")


def ler_arquivo(arquivo, separador: str, decimal: str) -> pd.DataFrame:
    """Le CSV ou Excel conforme a extensao."""
    nome = arquivo.name.lower()
    if nome.endswith((".xlsx", ".xls")):
        return pd.read_excel(arquivo)
    return pd.read_csv(
        arquivo,
        sep=None if separador == "detectar" else separador,
        decimal=decimal,
        engine="python",
        encoding_errors="replace",
    )


def diagnosticar(df: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por coluna, com o que interessa saber antes de limpar."""
    return pd.DataFrame(
        {
            "Coluna": df.columns,
            "Tipo": [str(t) for t in df.dtypes],
            "Vazios": df.isna().sum().values,
            "% vazios": (df.isna().mean().values * 100).round(1),
            "Valores unicos": [df[c].nunique(dropna=True) for c in df.columns],
        }
    )


def limpar(df: pd.DataFrame, opcoes: dict) -> tuple[pd.DataFrame, list[str]]:
    """Aplica as limpezas escolhidas e devolve o relatorio do que mudou."""
    relatorio: list[str] = []
    saida = df.copy()

    if opcoes["padronizar_nomes"]:
        antes = list(saida.columns)
        saida.columns = (
            pd.Index(saida.columns)
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"[^0-9a-z_]", "", regex=True)
        )
        if antes != list(saida.columns):
            relatorio.append("Nomes de colunas padronizados para minusculas com underline.")

    if opcoes["limpar_texto"]:
        colunas_texto = saida.select_dtypes(include=["object", "string"]).columns
        for c in colunas_texto:
            saida[c] = saida[c].astype(str).str.strip().replace({"nan": None, "": None})
        if len(colunas_texto):
            relatorio.append(f"Espacos das pontas removidos em {len(colunas_texto)} coluna(s) de texto.")

    if opcoes["remover_colunas_vazias"]:
        vazias = [c for c in saida.columns if saida[c].isna().all()]
        if vazias:
            saida = saida.drop(columns=vazias)
            relatorio.append(f"{len(vazias)} coluna(s) totalmente vazia(s) removida(s).")

    if opcoes["remover_linhas_vazias"]:
        antes = len(saida)
        saida = saida.dropna(how="all")
        if antes != len(saida):
            relatorio.append(f"{antes - len(saida)} linha(s) totalmente vazia(s) removida(s).")

    if opcoes["remover_duplicatas"]:
        antes = len(saida)
        saida = saida.drop_duplicates()
        if antes != len(saida):
            relatorio.append(f"{antes - len(saida)} linha(s) duplicada(s) removida(s).")

    if not relatorio:
        relatorio.append("Nada a corrigir com as opcoes escolhidas.")

    return saida.reset_index(drop=True), relatorio


def para_excel(df: pd.DataFrame) -> bytes:
    """Gera o .xlsx na memoria, sem criar arquivo em disco."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="dados")
    return buffer.getvalue()


def exemplo_sujo() -> pd.DataFrame:
    """Planilha de exemplo com os problemas tipicos, para testar sem arquivo."""
    return pd.DataFrame(
        {
            " Nome Completo ": ["  Ana Souza", "Bruno Lima ", "Ana Souza", None, "Carla Dias"],
            "E-MAIL": ["ana@x.com", "bruno@x.com", "ana@x.com", None, "carla@x.com"],
            "Valor R$": [1200.5, 890.0, 1200.5, None, 340.25],
            "Observacao": [None, None, None, None, None],
        }
    )


def main() -> None:
    cabecalho(5, "🧹 Limpador de planilhas", "entrada e saida de arquivos")

    st.sidebar.header("Leitura")
    separador = st.sidebar.selectbox("Separador do CSV", ["detectar", ",", ";", "\t", "|"])
    decimal = st.sidebar.selectbox("Separador decimal", [".", ","])

    st.sidebar.header("Limpezas")
    opcoes = {
        "padronizar_nomes": st.sidebar.checkbox("Padronizar nomes das colunas", True),
        "limpar_texto": st.sidebar.checkbox("Remover espacos nas pontas", True),
        "remover_colunas_vazias": st.sidebar.checkbox("Remover colunas vazias", True),
        "remover_linhas_vazias": st.sidebar.checkbox("Remover linhas vazias", True),
        "remover_duplicatas": st.sidebar.checkbox("Remover duplicatas", True),
    }

    arquivo = st.file_uploader(
        "Envie um CSV ou Excel",
        type=["csv", "txt", "xlsx", "xls"],
        help="O arquivo fica na memoria do app; nada e gravado em disco.",
    )

    usar_exemplo = st.checkbox("Nao tenho arquivo — usar planilha de exemplo")

    # A guarda mais importante deste projeto: sem entrada, para por aqui.
    if arquivo is None and not usar_exemplo:
        st.info("Envie um arquivo acima, ou marque a opcao para testar com o exemplo.")
        st.stop()

    if arquivo is not None:
        try:
            bruto = ler_arquivo(arquivo, separador, decimal)
        except Exception as erro:
            st.error("Nao consegui ler este arquivo.")
            st.caption(f"Detalhe tecnico: {erro}")
            st.info("Tente trocar o separador na barra lateral, ou salve como CSV UTF-8.")
            st.stop()
        origem = arquivo.name
    else:
        bruto = exemplo_sujo()
        origem = "exemplo.csv"

    if bruto.empty:
        st.warning("O arquivo foi lido, mas nao tem nenhuma linha.")
        st.stop()

    limpo, relatorio = limpar(bruto, opcoes)

    # ---------------- resumo ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Linhas", f"{len(limpo):,}".replace(",", "."), f"{len(limpo) - len(bruto):+d}")
    c2.metric("Colunas", limpo.shape[1], f"{limpo.shape[1] - bruto.shape[1]:+d}")
    c3.metric("Celulas vazias", int(limpo.isna().sum().sum()))
    c4.metric("Duplicatas restantes", int(limpo.duplicated().sum()))

    st.success("Limpeza aplicada:")
    for item in relatorio:
        st.markdown(f"- {item}")

    st.divider()

    antes, depois, diag = st.tabs(["Antes", "Depois", "Diagnostico por coluna"])
    with antes:
        st.dataframe(bruto, width="stretch", height=320)
    with depois:
        st.dataframe(limpo, width="stretch", height=320)
    with diag:
        st.dataframe(diagnosticar(limpo), hide_index=True, width="stretch", height=320)

    st.divider()
    st.subheader("Baixar o resultado")

    base = Path(origem).stem
    c1, c2 = st.columns(2)
    c1.download_button(
        "Baixar CSV",
        data=limpo.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{base}_limpo.csv",
        mime="text/csv",
        width="stretch",
    )
    c2.download_button(
        "Baixar Excel",
        data=para_excel(limpo),
        file_name=f"{base}_limpo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

    rodape([
        "`st.file_uploader` devolve um objeto de arquivo em memoria, nao um caminho.",
        "`st.stop()` encerra o script — use quando falta a entrada obrigatoria.",
        "Todo `read_csv`/`read_excel` de arquivo alheio vai dentro de `try/except`.",
        "`io.BytesIO` gera o Excel sem tocar no disco (importante no servidor).",
        "`st.download_button` entrega bytes prontos; nada fica gravado no servidor.",
        "`utf-8-sig` faz o Excel abrir acentos corretamente.",
    ])


main()
