"""PROJETO 03 — Lista de tarefas.

CONCEITO NOVO: st.session_state, a memoria entre reruns.

Este e o degrau mais ingreme da trilha.

No Projeto 01 voce aprendeu que o script roda inteiro a cada interacao.
A consequencia: toda variavel comum e recriada do zero. Uma lista Python
declarada aqui dentro NUNCA acumula nada — ela nasce vazia de novo a cada
clique.

`st.session_state` e um dicionario que sobrevive aos reruns. E o unico
lugar onde a informacao do usuario pode ficar guardada durante a visita.

Como rodar sozinho:
    streamlit run projetos/projeto_03_tarefas.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Lista de tarefas", "✅")

PRIORIDADES = {"Alta": "🔴", "Media": "🟡", "Baixa": "🟢"}


def iniciar_estado() -> None:
    """Cria as chaves do session_state na primeira execucao.

    O `if ... not in` e essencial: sem ele, a lista seria zerada a cada
    rerun e nada nunca apareceria.
    """
    if "tarefas" not in st.session_state:
        st.session_state.tarefas = []
    if "proximo_id" not in st.session_state:
        st.session_state.proximo_id = 1


def adicionar(texto: str, prioridade: str) -> None:
    st.session_state.tarefas.append(
        {
            "id": st.session_state.proximo_id,
            "texto": texto.strip(),
            "prioridade": prioridade,
            "feita": False,
            "criada": datetime.now().strftime("%d/%m %H:%M"),
        }
    )
    st.session_state.proximo_id += 1


def remover(tarefa_id: int) -> None:
    st.session_state.tarefas = [t for t in st.session_state.tarefas if t["id"] != tarefa_id]


def main() -> None:
    cabecalho(3, "✅ Lista de tarefas", "`st.session_state` — memoria entre reruns")

    iniciar_estado()

    # Sincroniza o dicionario com o estado real dos checkboxes ANTES de
    # desenhar os indicadores. Sem isto, os numeros do topo ficariam um
    # clique atrasados: eles sao desenhados antes dos checkboxes.
    for t in st.session_state.tarefas:
        chave = f"chk_{t['id']}"
        if chave in st.session_state:
            t["feita"] = st.session_state[chave]

    # ---------------- entrada ----------------
    # clear_on_submit limpa o campo depois de enviar: o jeito mais simples
    # de zerar um widget sem mexer diretamente no session_state dele.
    with st.form("nova_tarefa", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        texto = c1.text_input("Nova tarefa", placeholder="O que precisa ser feito?")
        prioridade = c2.selectbox("Prioridade", list(PRIORIDADES.keys()), index=1)
        enviou = c3.form_submit_button("Adicionar", width="stretch")

    if enviou:
        if texto.strip():
            adicionar(texto, prioridade)
        else:
            st.warning("Escreva alguma coisa antes de adicionar.")

    tarefas = st.session_state.tarefas

    if not tarefas:
        st.info("Nenhuma tarefa ainda. Adicione a primeira acima.")
        st.caption(
            "Experimento: troque `st.session_state.tarefas` por uma lista comum "
            "no topo do arquivo e veja que nada nunca aparece."
        )
        rodape(["O `session_state` guarda dados entre reruns; variaveis comuns nao."])
        return

    # ---------------- progresso ----------------
    feitas = sum(1 for t in tarefas if t["feita"])
    total = len(tarefas)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Concluidas", feitas)
    c3.metric("Pendentes", total - feitas)

    st.progress(feitas / total, text=f"{feitas} de {total} concluidas")
    st.divider()

    # ---------------- lista ----------------
    ordem = {"Alta": 0, "Media": 1, "Baixa": 2}
    visiveis = sorted(tarefas, key=lambda t: (t["feita"], ordem[t["prioridade"]]))

    for t in visiveis:
        marca, corpo, lixo = st.columns([0.08, 0.77, 0.15])

        # A `key` precisa ser unica por widget. Sem ela, o Streamlit
        # confunde os checkboxes entre si.
        # Lemos o valor de volta e sincronizamos o dicionario. O widget
        # guarda o proprio estado pela `key`; `value` vale so na 1a vez.
        t["feita"] = marca.checkbox(
            "feita",
            value=t["feita"],
            key=f"chk_{t['id']}",
            label_visibility="collapsed",
        )

        rotulo = f"~~{t['texto']}~~" if t["feita"] else t["texto"]
        corpo.markdown(f"{PRIORIDADES[t['prioridade']]} {rotulo}")
        corpo.caption(f"criada em {t['criada']}")

        lixo.button(
            "Remover",
            key=f"del_{t['id']}",
            on_click=remover,
            args=(t["id"],),
            width="stretch",
        )

    st.divider()

    esq, dir_ = st.columns(2)
    if esq.button("Limpar concluidas", width="stretch", disabled=feitas == 0):
        st.session_state.tarefas = [t for t in tarefas if not t["feita"]]
        st.rerun()

    if dir_.button("Apagar tudo", width="stretch", type="secondary"):
        st.session_state.tarefas = []
        st.session_state.proximo_id = 1
        st.rerun()

    with st.expander("Ver o session_state por dentro"):
        st.write(
            "Isto e o conteudo real da memoria da sua sessao. Abra este app "
            "em duas abas: cada uma tem a sua, independente da outra."
        )
        st.json({"tarefas": st.session_state.tarefas, "proximo_id": st.session_state.proximo_id})

    rodape([
        "`st.session_state` e a unica memoria que sobrevive aos reruns.",
        "Inicialize sempre com `if 'chave' not in st.session_state`.",
        "Cada widget repetido precisa de uma `key` unica.",
        "`on_click` e `on_change` executam a funcao ANTES do proximo rerun.",
        "`st.rerun()` forca uma nova execucao imediata.",
        "A memoria e por sessao: cada aba do navegador tem a sua.",
    ])


main()
