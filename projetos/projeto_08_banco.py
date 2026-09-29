"""PROJETO 08 — Cadastro com banco de dados.

CONCEITO NOVO: persistencia, e por que ela e diferente no servidor.

Ate aqui, tudo sumia ao fechar a aba. Aqui os dados vao para um banco
SQLite de verdade: cadastrar, listar, editar e excluir.

A ARMADILHA PEDAGOGICA DESTE PROJETO:
    No seu computador, o arquivo do banco sobrevive para sempre.
    No Streamlit Community Cloud, NAO. O disco e temporario: a cada
    reinicio ou hibernacao (12 h sem visitas) tudo volta ao zero.

Publique assim mesmo e volte no dia seguinte. Ver os dados sumirem ensina
mais do que ler sobre isso — e explica por que aplicacoes reais usam banco
externo (Supabase, Neon, Google Sheets).

`st.cache_resource` (e nao `cache_data`): conexao de banco se REAPROVEITA,
nao se copia. `cache_data` devolveria uma copia dos dados; `cache_resource`
devolve o mesmo objeto vivo para todo mundo.

Como rodar sozinho:
    streamlit run projetos/projeto_08_banco.py
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Cadastro com banco", "🗄️", "wide")

BANCO = Path(__file__).resolve().parent.parent / "dados_projeto08.db"

SETORES = ["Producao", "Financeiro", "Comercial", "Logistica", "TI"]
SITUACOES = ["Ativo", "Ferias", "Afastado", "Desligado"]


@st.cache_resource
def conectar() -> sqlite3.Connection:
    """Uma conexao para o app inteiro.

    `check_same_thread=False` e necessario porque o Streamlit atende cada
    sessao numa thread diferente.
    """
    con = sqlite3.connect(BANCO, check_same_thread=False)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS colaboradores (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            setor     TEXT    NOT NULL,
            admissao  TEXT    NOT NULL,
            salario   REAL    NOT NULL,
            situacao  TEXT    NOT NULL
        )
        """
    )
    con.commit()
    return con


def listar() -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM colaboradores ORDER BY nome", conectar())


def inserir(nome: str, setor: str, admissao: date, salario: float, situacao: str) -> None:
    con = conectar()
    con.execute(
        "INSERT INTO colaboradores (nome, setor, admissao, salario, situacao) VALUES (?,?,?,?,?)",
        (nome.strip(), setor, admissao.isoformat(), float(salario), situacao),
    )
    con.commit()


def atualizar(registro: dict) -> None:
    con = conectar()
    con.execute(
        "UPDATE colaboradores SET nome=?, setor=?, admissao=?, salario=?, situacao=? WHERE id=?",
        (
            registro["nome"], registro["setor"], str(registro["admissao"]),
            float(registro["salario"]), registro["situacao"], int(registro["id"]),
        ),
    )
    con.commit()


def excluir(ids: list[int]) -> None:
    con = conectar()
    con.executemany("DELETE FROM colaboradores WHERE id = ?", [(int(i),) for i in ids])
    con.commit()


def semear() -> None:
    """Preenche com exemplos, para o app nao abrir vazio."""
    exemplos = [
        ("Ana Souza", "Producao", date(2019, 3, 11), 4200.0, "Ativo"),
        ("Bruno Lima", "TI", date(2021, 7, 1), 7800.0, "Ativo"),
        ("Carla Dias", "Financeiro", date(2017, 1, 23), 6100.0, "Ferias"),
        ("Diego Alves", "Logistica", date(2023, 9, 5), 3400.0, "Ativo"),
    ]
    for e in exemplos:
        inserir(*e)


def main() -> None:
    cabecalho(8, "🗄️ Cadastro com banco de dados", "persistencia com SQLite e `st.cache_resource`")

    st.error(
        "**No Community Cloud este banco NAO sobrevive.** O disco do servidor e "
        "temporario: a cada reinicio ou hibernacao o arquivo some. Publique assim "
        "mesmo e volte amanha para ver acontecer — e a licao deste projeto.",
        icon="⚠️",
    )

    dados = listar()

    if dados.empty:
        st.info("O banco esta vazio.")
        if st.button("Criar registros de exemplo", type="primary"):
            semear()
            st.rerun()

    # ---------------- cadastrar ----------------
    with st.expander("➕ Cadastrar novo", expanded=dados.empty):
        with st.form("novo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome *")
            setor = c2.selectbox("Setor *", SETORES)

            c3, c4, c5 = st.columns(3)
            admissao = c3.date_input("Admissao *", value=date.today(),
                                     min_value=date(1990, 1, 1), format="DD/MM/YYYY")
            salario = c4.number_input("Salario *", min_value=0.0, value=3000.0, step=100.0)
            situacao = c5.selectbox("Situacao *", SITUACOES)

            if st.form_submit_button("Cadastrar", type="primary", width="stretch"):
                if len(nome.strip()) < 3:
                    st.warning("Informe o nome completo.")
                else:
                    inserir(nome, setor, admissao, salario, situacao)
                    st.success(f"{nome.strip()} cadastrado.")
                    st.rerun()

    if dados.empty:
        rodape(["`st.cache_resource` guarda a conexao; `cache_data` guardaria copias dos dados."])
        return

    # ---------------- indicadores ----------------
    ativos = dados[dados["situacao"] == "Ativo"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cadastrados", len(dados))
    c2.metric("Ativos", len(ativos))
    c3.metric("Folha mensal", f"R$ {dados['salario'].sum():,.0f}".replace(",", "."))
    c4.metric("Salario medio", f"R$ {dados['salario'].mean():,.0f}".replace(",", "."))

    st.divider()

    # ---------------- editar ----------------
    st.subheader("Editar")
    st.caption("Altere direto na tabela e clique em Salvar. Marque a caixa para excluir.")

    edicao = dados.copy()
    edicao["admissao"] = pd.to_datetime(edicao["admissao"]).dt.date
    edicao.insert(0, "excluir", False)

    editado = st.data_editor(
        edicao,
        hide_index=True,
        width="stretch",
        disabled=["id"],
        column_config={
            "excluir": st.column_config.CheckboxColumn("🗑", width="small"),
            "id": st.column_config.NumberColumn("ID", width="small"),
            "nome": st.column_config.TextColumn("Nome", required=True),
            "setor": st.column_config.SelectboxColumn("Setor", options=SETORES, required=True),
            "admissao": st.column_config.DateColumn("Admissao", format="DD/MM/YYYY"),
            "salario": st.column_config.NumberColumn("Salario", format="R$ %.2f", min_value=0.0),
            "situacao": st.column_config.SelectboxColumn("Situacao", options=SITUACOES, required=True),
        },
        key="editor",
    )

    c1, c2 = st.columns(2)

    if c1.button("💾 Salvar alteracoes", type="primary", width="stretch"):
        alterados = 0
        for _, linha in editado.iterrows():
            original = dados[dados["id"] == linha["id"]].iloc[0]
            mudou = (
                linha["nome"] != original["nome"]
                or linha["setor"] != original["setor"]
                or str(linha["admissao"]) != str(original["admissao"])
                or float(linha["salario"]) != float(original["salario"])
                or linha["situacao"] != original["situacao"]
            )
            if mudou:
                atualizar(linha.to_dict())
                alterados += 1
        st.success(f"{alterados} registro(s) atualizado(s).") if alterados else st.info("Nada mudou.")
        if alterados:
            st.rerun()

    marcados = editado[editado["excluir"]]["id"].tolist()
    if c2.button(f"🗑 Excluir marcados ({len(marcados)})",
                 width="stretch", disabled=not marcados):
        excluir(marcados)
        st.success(f"{len(marcados)} registro(s) excluido(s).")
        st.rerun()

    st.divider()
    esq, dir_ = st.columns(2)
    with esq:
        st.subheader("Folha por setor")
        st.bar_chart(dados.groupby("setor")["salario"].sum(), horizontal=True, height=260)
    with dir_:
        st.subheader("Situacao")
        st.bar_chart(dados["situacao"].value_counts(), height=260)

    st.download_button(
        "Baixar backup em CSV",
        data=dados.to_csv(index=False).encode("utf-8-sig"),
        file_name="colaboradores.csv",
        mime="text/csv",
    )
    st.caption(
        "No Cloud, este botao e o unico jeito de nao perder os dados — "
        "o que ja mostra que a arquitetura precisaria de um banco externo."
    )

    rodape([
        "`st.cache_resource` guarda objetos vivos (conexoes); `cache_data`, copias de dados.",
        "`check_same_thread=False` e necessario: o Streamlit usa varias threads.",
        "Use sempre parametros `?` no SQL — nunca monte a query com f-string.",
        "`st.data_editor` devolve o DataFrame editado; comparar com o original diz o que mudou.",
        "No Community Cloud o disco e efemero: SQLite local nao serve para producao.",
        "Banco externo com faixa gratuita: Supabase, Neon, Turso.",
    ])


main()
