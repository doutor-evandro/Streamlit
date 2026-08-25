"""Pagina 1 -- o Hello World original.

Um arquivo de pagina nao tem funcao main() nem `if __name__`: o
Streamlit executa o arquivo inteiro, de cima a baixo, sempre que a
pagina e aberta ou algo nela muda.
"""

import streamlit as st

st.title("Hello World! 👋")
st.write("Meu primeiro programa em Streamlit.")

nome = st.text_input("Qual e o seu nome?", value="Evandro")

if st.button("Dizer ola"):
    st.success(f"Ola, {nome}! Bem-vindo ao Streamlit.")

st.divider()
st.caption("Use o menu a esquerda para ver o Painel de Automacoes.")
