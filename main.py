"""Ponto de entrada do app multi-paginas.

Este arquivo nao desenha nada: ele so monta o menu e entrega o controle
para a pagina escolhida. Todo o conteudo vive na pasta `paginas/`.

Como rodar:
    .venv\\Scripts\\activate
    streamlit run main.py
"""

import streamlit as st

# set_page_config vale para o app inteiro e precisa ser a primeira
# chamada Streamlit do programa. Por isso mora aqui, e nao nas paginas.
st.set_page_config(
    page_title="Apps do Evandro",
    page_icon="🤖",
    layout="wide",
)

# Cada st.Page aponta para um arquivo. O titulo e o icone sao o que
# aparece no menu lateral; `default=True` marca a pagina de abertura.
paginas = [
    st.Page(
        "paginas/hello.py",
        title="Hello World",
        icon=":material/waving_hand:",
        default=True,
    ),
    st.Page(
        "paginas/painel.py",
        title="Painel de Automacoes",
        icon=":material/smart_toy:",
    ),
]


def main() -> None:
    # st.navigation desenha o menu e devolve a pagina ativa;
    # .run() executa o arquivo dela.
    st.navigation(paginas).run()


if __name__ == "__main__":
    main()
