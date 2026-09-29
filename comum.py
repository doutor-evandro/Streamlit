"""Funcoes compartilhadas por todos os projetos da trilha.

Cada projeto precisa funcionar de dois jeitos:

1. Sozinho, com endereco proprio:
       streamlit run projetos/projeto_01_conversor.py

2. Dentro do menu do app principal, no mesmo endereco:
       registrado com st.Page(...) no main.py

O problema: `st.set_page_config` so pode ser chamado UMA vez por app.
No modo 1 quem chama e o proprio projeto; no modo 2 quem ja chamou foi o
main.py. A funcao abaixo resolve isso tentando configurar e ignorando o
erro quando alguem ja configurou antes.
"""

from __future__ import annotations

import streamlit as st


def configurar_pagina(titulo: str, icone: str = "🧪", largura: str = "centered") -> None:
    """Configura a pagina, funcionando tanto sozinha quanto dentro do menu."""
    try:
        st.set_page_config(page_title=titulo, page_icon=icone, layout=largura)
    except Exception:
        # Ja configurado pelo main.py. Nada a fazer.
        pass


def cabecalho(numero: int, titulo: str, conceito: str) -> None:
    """Cabecalho padrao de um projeto da trilha."""
    st.caption(f"Projeto {numero:02d} · trilha Streamlit")
    st.title(titulo)
    st.info(f"**Conceito novo deste projeto:** {conceito}")


def rodape(pontos: list[str]) -> None:
    """Lista, no fim da pagina, o que este projeto ensinou."""
    st.divider()
    with st.expander("O que este projeto ensina"):
        for p in pontos:
            st.markdown(f"- {p}")
