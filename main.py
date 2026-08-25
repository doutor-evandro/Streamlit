"""Hello World em Streamlit.

Como rodar:
    pip install streamlit
    streamlit run main.py
"""

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="Hello World", page_icon="👋")

    st.title("Hello World! 👋")
    st.write("Meu primeiro programa em Streamlit.")

    nome = st.text_input("Qual é o seu nome?", value="Evandro")

    if st.button("Dizer olá"):
        st.success(f"Olá, {nome}! Bem-vindo ao Streamlit.")


if __name__ == "__main__":
    main()
