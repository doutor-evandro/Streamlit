"""PROJETO 03 — Lista de tarefas.

CONCEITOS: st.session_state (memoria) e persistencia em banco na nuvem.

Este arquivo funciona em DOIS MODOS, e comparar os dois e a licao:

  MODO MEMORIA  — sem banco configurado.
      As tarefas vivem em `st.session_state`. Sobrevivem aos reruns, mas
      morrem ao recarregar a pagina (F5). Cada aba tem a sua lista.

  MODO NUVEM    — com Supabase configurado no secrets.
      As tarefas vao para um Postgres na internet. Sobrevivem ao F5, ao
      fechar o navegador, a hibernacao do app e sao as MESMAS para todos
      os visitantes.

Por que nao SQLite? Porque no Streamlit Community Cloud o disco e
temporario: o arquivo some quando o app hiberna. Para persistir de verdade
no servidor, o dado precisa morar FORA dele.

Como rodar sozinho:
    streamlit run projetos/projeto_03_tarefas.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Lista de tarefas", "✅")

PRIORIDADES = {"Alta": "🔴", "Media": "🟡", "Baixa": "🟢"}
ORDEM = {"Alta": 0, "Media": 1, "Baixa": 2}

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS tarefas (
    id         BIGSERIAL PRIMARY KEY,
    texto      TEXT        NOT NULL,
    prioridade TEXT        NOT NULL DEFAULT 'Media',
    feita      BOOLEAN     NOT NULL DEFAULT FALSE,
    criada_em  TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


# ==========================================================================
# Deteccao do modo
# ==========================================================================
def tem_banco() -> bool:
    """Ha uma conexao configurada no secrets?

    `st.secrets` levanta erro quando nao existe arquivo nenhum — por isso
    o try/except. Assim o projeto roda antes de voce configurar o banco.
    """
    try:
        return bool(st.secrets["connections"]["supabase"]["url"])
    except Exception:
        return False


# ==========================================================================
# MODO NUVEM — Supabase (Postgres)
# ==========================================================================
@st.cache_resource
def conectar():
    """A conexao e um recurso, nao um dado: por isso `cache_resource`.

    `st.connection` le automaticamente a secao [connections.supabase]
    do secrets.toml. Nenhuma senha aparece neste arquivo.
    """
    conexao = st.connection("supabase", type="sql")
    from sqlalchemy import text

    with conexao.session as s:
        s.execute(text(CRIAR_TABELA))
        s.commit()
    return conexao


def banco_listar() -> pd.DataFrame:
    # ttl=0 desliga o cache da consulta: queremos sempre o dado atual.
    return conectar().query(
        "SELECT id, texto, prioridade, feita, criada_em FROM tarefas ORDER BY id",
        ttl=0,
    )


def _executar(sql: str, **valores) -> None:
    from sqlalchemy import text

    with conectar().session as s:
        s.execute(text(sql), valores)
        s.commit()


def banco_adicionar(texto: str, prioridade: str) -> None:
    _executar(
        "INSERT INTO tarefas (texto, prioridade) VALUES (:texto, :prio)",
        texto=texto.strip(), prio=prioridade,
    )


def banco_marcar(tarefa_id: int, feita: bool) -> None:
    _executar("UPDATE tarefas SET feita = :feita WHERE id = :id", feita=feita, id=int(tarefa_id))


def banco_remover(tarefa_id: int) -> None:
    _executar("DELETE FROM tarefas WHERE id = :id", id=int(tarefa_id))


def banco_limpar_feitas() -> None:
    _executar("DELETE FROM tarefas WHERE feita = TRUE")


def banco_apagar_tudo() -> None:
    _executar("DELETE FROM tarefas")


# ==========================================================================
# MODO MEMORIA — st.session_state
# ==========================================================================
def memoria_iniciar() -> None:
    # Sem o `if ... not in`, a lista seria zerada a cada rerun.
    st.session_state.setdefault("tarefas", [])
    st.session_state.setdefault("proximo_id", 1)


def memoria_listar() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.tarefas,
                        columns=["id", "texto", "prioridade", "feita", "criada_em"])


def memoria_adicionar(texto: str, prioridade: str) -> None:
    st.session_state.tarefas.append(
        {
            "id": st.session_state.proximo_id,
            "texto": texto.strip(),
            "prioridade": prioridade,
            "feita": False,
            "criada_em": datetime.now(),
        }
    )
    st.session_state.proximo_id += 1


def memoria_marcar(tarefa_id: int, feita: bool) -> None:
    for t in st.session_state.tarefas:
        if t["id"] == tarefa_id:
            t["feita"] = feita


def memoria_remover(tarefa_id: int) -> None:
    st.session_state.tarefas = [t for t in st.session_state.tarefas if t["id"] != tarefa_id]


def memoria_limpar_feitas() -> None:
    st.session_state.tarefas = [t for t in st.session_state.tarefas if not t["feita"]]


def memoria_apagar_tudo() -> None:
    st.session_state.tarefas = []
    st.session_state.proximo_id = 1


# ==========================================================================
# Interface
# ==========================================================================
def instrucoes_supabase() -> None:
    with st.expander("Como ligar este projeto a um banco de verdade (Supabase)"):
        st.markdown(
            "**1. Crie o projeto** em [supabase.com](https://supabase.com) — "
            "plano gratuito, sem cartao. Guarde a senha do banco que ele pedir."
        )
        st.markdown(
            "**2. Pegue a string de conexao:** botao **Connect**, no topo do painel. "
            "Escolha **Session pooler** — e a unica que funciona no Streamlit Cloud, "
            "porque a conexao direta so responde em IPv6 e o servidor do Streamlit e IPv4."
        )
        st.markdown("**3. No seu PC**, crie `.streamlit/secrets.toml`:")
        st.code(
            '[connections.supabase]\n'
            'url = "postgresql://postgres.SEU_PROJETO:SUA_SENHA'
            '@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"',
            language="toml",
        )
        st.markdown(
            "**4. No Streamlit Cloud**, cole o mesmo conteudo em "
            "**Manage app → ⋮ → Settings → Secrets**."
        )
        st.info(
            "A tabela e criada sozinha na primeira execucao. "
            "O `.gitignore` ja protege o secrets.toml — a senha nunca vai para o GitHub.",
            icon="🔐",
        )


def main() -> None:
    cabecalho(3, "✅ Lista de tarefas", "`st.session_state` e persistencia em banco")

    nuvem = tem_banco()
    erro_conexao = None

    if nuvem:
        try:
            conectar()
        except Exception as e:
            erro_conexao = e
            nuvem = False

    if erro_conexao is not None:
        st.error("Banco configurado, mas nao consegui conectar. Usando a memoria por enquanto.")
        st.caption(f"Detalhe tecnico: {str(erro_conexao)[:300]}")
        st.info(
            "Erro comum: usar a conexao **direta** do Supabase em vez do **Session pooler**. "
            "A direta so responde em IPv6 e o Streamlit Cloud e IPv4.",
            icon="💡",
        )

    if nuvem:
        st.success(
            "**Modo nuvem.** As tarefas ficam num Postgres na internet: sobrevivem ao F5, "
            "ao fechar o navegador e sao as mesmas para todos os visitantes.",
            icon="☁️",
        )
        listar, adicionar = banco_listar, banco_adicionar
        marcar, remover = banco_marcar, banco_remover
        limpar_feitas, apagar_tudo = banco_limpar_feitas, banco_apagar_tudo
    else:
        memoria_iniciar()
        st.warning(
            "**Modo memoria.** As tarefas vivem so nesta aba e somem ao recarregar a pagina. "
            "Veja abaixo como ligar a um banco de verdade.",
            icon="🧠",
        )
        listar, adicionar = memoria_listar, memoria_adicionar
        marcar, remover = memoria_marcar, memoria_remover
        limpar_feitas, apagar_tudo = memoria_limpar_feitas, memoria_apagar_tudo
        instrucoes_supabase()

    # ---------------- entrada ----------------
    with st.form("nova_tarefa", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        texto = c1.text_input("Nova tarefa", placeholder="O que precisa ser feito?")
        prioridade = c2.selectbox("Prioridade", list(PRIORIDADES.keys()), index=1)
        enviou = c3.form_submit_button("Adicionar", width="stretch")

    if enviou:
        if texto.strip():
            adicionar(texto, prioridade)
            st.rerun()
        else:
            st.warning("Escreva alguma coisa antes de adicionar.")

    tarefas = listar()

    if tarefas.empty:
        st.info("Nenhuma tarefa ainda. Adicione a primeira acima.")
        rodape(["`st.session_state` guarda entre reruns; um banco guarda entre visitas."])
        return

    # ---------------- progresso ----------------
    feitas = int(tarefas["feita"].sum())
    total = len(tarefas)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Concluidas", feitas)
    c3.metric("Pendentes", total - feitas)
    st.progress(feitas / total, text=f"{feitas} de {total} concluidas")

    st.divider()

    # ---------------- lista ----------------
    tarefas = tarefas.assign(_ordem=tarefas["prioridade"].map(ORDEM)).sort_values(
        ["feita", "_ordem", "id"]
    )

    for _, t in tarefas.iterrows():
        marca, corpo, lixo = st.columns([0.08, 0.77, 0.15])

        # A `key` precisa ser unica por widget, senao o Streamlit
        # confunde os checkboxes entre si.
        nova = marca.checkbox(
            "feita",
            value=bool(t["feita"]),
            key=f"chk_{t['id']}",
            label_visibility="collapsed",
        )
        if nova != bool(t["feita"]):
            marcar(t["id"], nova)
            st.rerun()

        rotulo = f"~~{t['texto']}~~" if t["feita"] else t["texto"]
        corpo.markdown(f"{PRIORIDADES.get(t['prioridade'], '⚪')} {rotulo}")
        quando = pd.to_datetime(t["criada_em"]).strftime("%d/%m %H:%M")
        corpo.caption(f"criada em {quando}")

        if lixo.button("Remover", key=f"del_{t['id']}", width="stretch"):
            remover(t["id"])
            st.rerun()

    st.divider()

    esq, dir_ = st.columns(2)
    if esq.button("Limpar concluidas", width="stretch", disabled=feitas == 0):
        limpar_feitas()
        st.rerun()
    if dir_.button("Apagar tudo", width="stretch"):
        apagar_tudo()
        st.rerun()

    if nuvem:
        st.caption(
            "Teste de verdade: aperte F5, feche o navegador, abra no celular. "
            "As tarefas continuam la — e sao as mesmas para todo mundo."
        )
    else:
        with st.expander("Ver o session_state por dentro"):
            st.json({"tarefas": st.session_state.tarefas})

    rodape([
        "`st.session_state` sobrevive aos reruns, mas nao ao F5.",
        "Inicialize sempre com `setdefault` ou `if 'chave' not in st.session_state`.",
        "Cada widget repetido precisa de uma `key` unica.",
        "`st.connection('nome', type='sql')` le a conexao do secrets — sem senha no codigo.",
        "`st.cache_resource` para a conexao; `ttl=0` na consulta para nao servir dado velho.",
        "Parametros `:nome` no SQL, nunca f-string: e o que evita SQL injection.",
        "No Community Cloud o disco e temporario — banco de verdade mora fora do servidor.",
    ])


main()
