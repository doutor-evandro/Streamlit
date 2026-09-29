"""PROJETO 01 — Conversor de unidades.

CONCEITO NOVO: widgets e o modelo de rerun.

A cada vez que voce mexe em qualquer widget, o Streamlit roda ESTE ARQUIVO
INTEIRO de cima a baixo, do zero. Nao existe "atualizar so um pedaco".
Por isso nao ha botao "Calcular": o resultado se recalcula sozinho.

Como rodar sozinho (endereco proprio):
    streamlit run projetos/projeto_01_conversor.py

Como rodar dentro do menu (mesmo endereco):
    ja registrado no main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Permite achar comum.py mesmo quando o arquivo roda sozinho.
sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Conversor de unidades", "📐")

# --------------------------------------------------------------------------
# Tabelas de conversao
#
# A ideia: escolher um "valor de referencia" por categoria e guardar quanto
# cada unidade vale nele. Converter vira entao uma conta so:
#     valor * fator_origem / fator_destino
# --------------------------------------------------------------------------
COMPRIMENTO = {           # referencia: metro
    "Metro (m)": 1.0,
    "Quilometro (km)": 1000.0,
    "Centimetro (cm)": 0.01,
    "Milimetro (mm)": 0.001,
    "Milha": 1609.344,
    "Pe (ft)": 0.3048,
    "Polegada (in)": 0.0254,
}

MASSA = {                 # referencia: quilograma
    "Quilograma (kg)": 1.0,
    "Grama (g)": 0.001,
    "Tonelada (t)": 1000.0,
    "Libra (lb)": 0.45359237,
    "Onca (oz)": 0.028349523125,
}

VOLUME = {                # referencia: litro
    "Litro (L)": 1.0,
    "Mililitro (mL)": 0.001,
    "Metro cubico (m3)": 1000.0,
    "Galao (US)": 3.785411784,
    "Xicara (240 mL)": 0.24,
}

TEMPERATURAS = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]


def converter_por_fator(valor: float, origem: str, destino: str, tabela: dict) -> float:
    """Converte usando a tabela de fatores. Serve para comprimento, massa e volume."""
    return valor * tabela[origem] / tabela[destino]


def converter_temperatura(valor: float, origem: str, destino: str) -> float:
    """Temperatura nao usa fator: cada escala tem seu zero proprio."""
    if origem == destino:
        return valor

    # Primeiro tudo vira Celsius...
    if origem.startswith("Fahrenheit"):
        celsius = (valor - 32) * 5 / 9
    elif origem.startswith("Kelvin"):
        celsius = valor - 273.15
    else:
        celsius = valor

    # ...depois Celsius vira o destino.
    if destino.startswith("Fahrenheit"):
        return celsius * 9 / 5 + 32
    if destino.startswith("Kelvin"):
        return celsius + 273.15
    return celsius


def formatar(numero: float) -> str:
    """Numero legivel: sem notacao cientifica e com virgula decimal."""
    if abs(numero) >= 1_000_000 or (numero != 0 and abs(numero) < 0.0001):
        texto = f"{numero:.6g}"
    else:
        texto = f"{numero:,.4f}".rstrip("0").rstrip(".")
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


def main() -> None:
    cabecalho(1, "📐 Conversor de unidades", "widgets e o modelo de rerun")

    categoria = st.radio(
        "Categoria",
        ["Comprimento", "Massa", "Volume", "Temperatura"],
        horizontal=True,
    )

    tabelas = {"Comprimento": COMPRIMENTO, "Massa": MASSA, "Volume": VOLUME}

    if categoria == "Temperatura":
        unidades = TEMPERATURAS
        tabela = None
    else:
        tabela = tabelas[categoria]
        unidades = list(tabela.keys())

    st.divider()

    esq, meio, dir_ = st.columns([2, 1, 2])

    with esq:
        origem = st.selectbox("De", unidades, index=0)
        valor = st.number_input("Valor", value=1.0, step=1.0, format="%.4f")

    with meio:
        st.markdown(
            "<div style='text-align:center;font-size:2.2rem;padding-top:2.2rem'>➜</div>",
            unsafe_allow_html=True,
        )

    with dir_:
        destino = st.selectbox("Para", unidades, index=min(1, len(unidades) - 1))

    if categoria == "Temperatura":
        resultado = converter_temperatura(valor, origem, destino)
    else:
        resultado = converter_por_fator(valor, origem, destino, tabela)

    st.divider()
    st.metric(
        label=f"{formatar(valor)} {origem}  em  {destino}",
        value=formatar(resultado),
    )

    # Sem botao "Calcular": o resultado acima ja se recalculou sozinho,
    # porque o script inteiro rodou de novo quando voce mexeu no widget.
    st.caption("Repare: nao existe botao. Mexa em qualquer campo e o resultado muda na hora.")

    with st.expander("Tabela de referencia desta categoria"):
        if categoria == "Temperatura":
            st.write("Temperatura nao tem fator fixo — cada escala tem seu proprio zero.")
            st.latex(r"°F = °C \times \frac{9}{5} + 32 \qquad K = °C + 273{,}15")
        else:
            base = list(tabela.keys())[0]
            linhas = [
                {"Unidade": u, f"Equivale em {base}": formatar(f)}
                for u, f in tabela.items()
            ]
            st.dataframe(linhas, hide_index=True)

    rodape([
        "`st.radio`, `st.selectbox` e `st.number_input` devolvem o valor escolhido na hora.",
        "O script roda inteiro a cada interacao — por isso nao precisa de botao.",
        "Separar o calculo em funcoes puras deixa o codigo testavel e legivel.",
        "`st.columns` coloca controles lado a lado.",
    ])


main()
