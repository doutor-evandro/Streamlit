"""Ponto de entrada do app multi-paginas.

Este arquivo nao desenha nada: ele so monta o menu e entrega o controle
para a pagina escolhida.

Cada projeto da trilha e um arquivo independente em `projetos/`, e funciona
de dois jeitos:

  1. Dentro deste menu, no mesmo endereco:
         streamlit run main.py

  2. Sozinho, com endereco proprio no Streamlit Cloud:
         streamlit run projetos/projeto_01_conversor.py
     (no Cloud, basta apontar o "Main file path" para o arquivo do projeto)
"""

import streamlit as st

# set_page_config vale para o app inteiro e precisa ser a primeira chamada
# Streamlit do programa. Por isso mora aqui, e nao nas paginas.
st.set_page_config(
    page_title="Apps do Evandro",
    page_icon="🤖",
    layout="wide",
)

INICIO = [
    st.Page("paginas/hello.py", title="Hello World",
            icon=":material/waving_hand:", default=True),
    st.Page("paginas/painel.py", title="Painel de Automacoes",
            icon=":material/smart_toy:"),
]

TRILHA = [
    st.Page("projetos/projeto_01_conversor.py", title="01 · Conversor de unidades",
            icon=":material/straighten:"),
    st.Page("projetos/projeto_02_ficha.py", title="02 · Ficha de produto",
            icon=":material/inventory_2:"),
    st.Page("projetos/projeto_03_tarefas.py", title="03 · Lista de tarefas",
            icon=":material/checklist:"),
    st.Page("projetos/projeto_04_formulario.py", title="04 · Formulario de inscricao",
            icon=":material/edit_note:"),
    st.Page("projetos/projeto_05_limpador.py", title="05 · Limpador de planilhas",
            icon=":material/cleaning_services:"),
    st.Page("projetos/projeto_06_painel.py", title="06 · Painel de vendas",
            icon=":material/bar_chart:"),
    st.Page("projetos/projeto_07_api.py", title="07 · Consulta a APIs",
            icon=":material/public:"),
    st.Page("projetos/projeto_08_banco.py", title="08 · Cadastro com banco",
            icon=":material/database:"),
    st.Page("projetos/projeto_09_senha.py", title="09 · App protegido",
            icon=":material/lock:"),
    st.Page("projetos/projeto_10_final.py", title="10 · Central de Automacoes",
            icon=":material/dashboard:"),
]


def main() -> None:
    # Passando um dicionario, o menu ganha secoes com titulo.
    st.navigation({"Inicio": INICIO, "Trilha de projetos": TRILHA}).run()


if __name__ == "__main__":
    main()
