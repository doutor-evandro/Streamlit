"""PROJETO 02 — Ficha de produto.

CONCEITO NOVO: layout e organizacao visual.

Ate aqui tudo era uma coluna unica, de cima para baixo. Este projeto usa
colunas, abas, barra lateral e expansores para agrupar a informacao.

A regra que mais confunde no inicio: use `with coluna:` para dizer onde
cada elemento entra. Fora do `with`, o elemento vai para a pagina toda.

Como rodar sozinho:
    streamlit run projetos/projeto_02_ficha.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Ficha de produto", "🪑", "wide")

CATALOGO = {
    "Cadeira Ergonomica Duo": {
        "cor": (58, 110, 122),
        "categoria": "Mobiliario de escritorio",
        "preco": 1289.90,
        "preco_antes": 1490.00,
        "nota": 4.6,
        "avaliacoes": 312,
        "estoque": 24,
        "peso": 14.2,
        "garantia": "5 anos",
        "resumo": "Apoio lombar ajustavel em 4 posicoes, braco 3D e base em aluminio polido.",
        "ficha": {
            "Material do encosto": "Tela mesh respiravel",
            "Regulagem de altura": "42 cm a 52 cm",
            "Capacidade": "Ate 130 kg",
            "Rodizios": "Nylon, para piso duro",
            "Certificacao": "NBR 13962",
        },
        "prós": ["Encosto respiravel", "Montagem em 15 min", "Pecas de reposicao disponiveis"],
        "contras": ["Apoio de cabeca vendido separado", "Peso alto para transporte"],
    },
    "Mesa Elevacao Fluxo": {
        "cor": (122, 92, 58),
        "categoria": "Mobiliario de escritorio",
        "preco": 2450.00,
        "preco_antes": 2450.00,
        "nota": 4.8,
        "avaliacoes": 87,
        "estoque": 6,
        "peso": 38.0,
        "garantia": "7 anos",
        "resumo": "Tampo em MDF 25 mm com motor eletrico duplo e memoria de 4 alturas.",
        "ficha": {
            "Dimensoes do tampo": "140 x 70 cm",
            "Faixa de altura": "68 cm a 118 cm",
            "Capacidade": "Ate 100 kg",
            "Ruido do motor": "Menos de 50 dB",
            "Consumo em espera": "0,1 W",
        },
        "prós": ["Motor silencioso", "Memoria de posicoes", "Passa-cabos incluso"],
        "contras": ["Preco elevado", "Precisa de duas pessoas para montar"],
    },
    "Luminaria Foco Pro": {
        "cor": (92, 84, 122),
        "categoria": "Iluminacao",
        "preco": 319.00,
        "preco_antes": 389.00,
        "nota": 4.2,
        "avaliacoes": 540,
        "estoque": 0,
        "peso": 1.1,
        "garantia": "2 anos",
        "resumo": "LED com temperatura de cor ajustavel de 2700K a 6500K e braco articulado.",
        "ficha": {
            "Potencia": "12 W",
            "Fluxo luminoso": "900 lumens",
            "Indice de reproducao de cor": "CRI 95",
            "Alcance do braco": "62 cm",
            "Alimentacao": "USB-C, 20 W",
        },
        "prós": ["CRI alto, cor fiel", "Nao esquenta", "Ocupa pouca base"],
        "contras": ["Fonte nao incluida", "Sem controle por aplicativo"],
    },
}


def imagem_do_produto(cor: tuple[int, int, int], largura=560, altura=340) -> np.ndarray:
    """Gera uma imagem de degrade, sem precisar de arquivo nem internet.

    Serve para mostrar que `st.image` aceita um array numpy, e nao apenas
    um caminho de arquivo ou uma URL.
    """
    y = np.linspace(0, 1, altura)[:, None]
    x = np.linspace(0, 1, largura)[None, :]
    rampa = (0.55 + 0.45 * (1 - y)) * (0.80 + 0.20 * x)

    img = np.zeros((altura, largura, 3), dtype=np.uint8)
    for canal, base in enumerate(cor):
        img[:, :, canal] = np.clip(base * rampa, 0, 255).astype(np.uint8)
    return img


def main() -> None:
    cabecalho(2, "🪑 Ficha de produto", "layout: colunas, abas, barra lateral e expansores")

    # ---------------- barra lateral ----------------
    st.sidebar.header("Catalogo")
    nome = st.sidebar.selectbox("Produto", list(CATALOGO.keys()))
    mostrar_tecnica = st.sidebar.toggle("Mostrar ficha tecnica", value=True)
    st.sidebar.divider()
    st.sidebar.caption(
        "A barra lateral e o lugar natural para filtros e opcoes: "
        "ela fica fora do fluxo de leitura da pagina."
    )

    p = CATALOGO[nome]

    # ---------------- cabecalho do produto ----------------
    foto, texto = st.columns([1, 1.3], gap="large")

    with foto:
        st.image(imagem_do_produto(p["cor"]), width="stretch")

    with texto:
        st.subheader(nome)
        st.caption(p["categoria"])
        st.write(p["resumo"])

        desconto = p["preco_antes"] - p["preco"]
        if desconto > 0:
            st.markdown(
                f"~~R$ {p['preco_antes']:,.2f}~~".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        st.markdown(f"### R$ {p['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        if p["estoque"] == 0:
            st.error("Fora de estoque")
        elif p["estoque"] < 10:
            st.warning(f"Ultimas {p['estoque']} unidades")
        else:
            st.success(f"{p['estoque']} unidades em estoque")

    st.divider()

    # ---------------- indicadores ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avaliacao", f"{p['nota']:.1f} / 5", f"{p['avaliacoes']} avaliacoes")
    c2.metric("Peso", f"{p['peso']:.1f} kg")
    c3.metric("Garantia", p["garantia"])
    c4.metric(
        "Desconto",
        f"R$ {desconto:,.0f}".replace(",", "."),
        None if desconto == 0 else f"-{desconto / p['preco_antes'] * 100:.0f}%",
    )

    st.divider()

    # ---------------- abas ----------------
    aba_desc, aba_ficha, aba_opiniao = st.tabs(["Descricao", "Ficha tecnica", "Pros e contras"])

    with aba_desc:
        st.write(p["resumo"])
        st.write(
            "Este bloco existe so para mostrar como as abas separam conteudos "
            "que competiriam pelo mesmo espaco na tela. Sem elas, tudo isto "
            "seria uma coluna unica e muito longa."
        )

    with aba_ficha:
        if mostrar_tecnica:
            linhas = [{"Caracteristica": k, "Valor": v} for k, v in p["ficha"].items()]
            st.dataframe(linhas, hide_index=True, width="stretch")
        else:
            st.info("Ative 'Mostrar ficha tecnica' na barra lateral.")

    with aba_opiniao:
        bom, ruim = st.columns(2)
        with bom:
            st.markdown("**A favor**")
            for item in p["prós"]:
                st.markdown(f"- {item}")
        with ruim:
            st.markdown("**Contra**")
            for item in p["contras"]:
                st.markdown(f"- {item}")

    with st.expander("Politica de entrega e devolucao"):
        st.write(
            "Envio em ate 2 dias uteis apos a confirmacao. Devolucao gratuita "
            "em 30 dias, com o produto na embalagem original."
        )
        st.caption("O expansor guarda o que nem todo mundo precisa ler.")

    rodape([
        "`st.columns` divide a largura; o `with` diz o que entra em cada coluna.",
        "`st.tabs` separa conteudos que disputam o mesmo espaco.",
        "`st.sidebar` e o lugar dos filtros e opcoes.",
        "`st.expander` esconde o detalhe que nem todos precisam.",
        "`st.image` aceita array numpy, nao so caminho de arquivo.",
        "`st.success`, `st.warning` e `st.error` comunicam estado pela cor.",
    ])


main()
