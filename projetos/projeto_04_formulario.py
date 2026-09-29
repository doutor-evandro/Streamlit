"""PROJETO 04 — Formulario de inscricao.

CONCEITO NOVO: st.form e validacao de entrada.

Nos projetos anteriores, cada tecla digitada disparava um rerun. Num
formulario com oito campos isso e um desperdicio: o app reage antes de a
pessoa terminar de preencher.

`st.form` agrupa os campos e segura tudo ate o clique no botao de envio.
Um unico rerun, com todos os valores de uma vez.

Regra: dentro de um form so funciona `st.form_submit_button`.
Um `st.button` comum ali dentro levanta erro.

Como rodar sozinho:
    streamlit run projetos/projeto_04_formulario.py
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Formulario de inscricao", "📝")

AREAS = [
    "Automacao de processos",
    "Analise de dados",
    "Desenvolvimento web",
    "Ciencia de dados",
    "Outra",
]

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def validar(dados: dict) -> dict[str, str]:
    """Devolve {campo: mensagem} com os problemas encontrados.

    Validar em uma funcao separada — em vez de espalhar `if` pela tela —
    deixa as regras visiveis num lugar so e faceis de testar.
    """
    erros: dict[str, str] = {}

    if len(dados["nome"].strip()) < 3:
        erros["nome"] = "Informe o nome completo (minimo 3 letras)."
    elif " " not in dados["nome"].strip():
        erros["nome"] = "Informe nome e sobrenome."

    if not PADRAO_EMAIL.match(dados["email"].strip()):
        erros["email"] = "E-mail invalido. Exemplo: nome@dominio.com.br"

    idade = (date.today() - dados["nascimento"]).days / 365.25
    if idade < 16:
        erros["nascimento"] = "E preciso ter ao menos 16 anos."
    elif idade > 110:
        erros["nascimento"] = "Confira a data de nascimento."

    if dados["area"] == "Outra" and not dados["area_outra"].strip():
        erros["area_outra"] = "Descreva sua area de interesse."

    if not dados["aceite"]:
        erros["aceite"] = "E preciso aceitar os termos para se inscrever."

    return erros


def main() -> None:
    cabecalho(4, "📝 Formulario de inscricao", "`st.form` e validacao de entrada")

    if "inscricoes" not in st.session_state:
        st.session_state.inscricoes = []

    with st.form("inscricao"):
        st.subheader("Dados pessoais")

        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome completo *", placeholder="Maria Silva")
        email = c2.text_input("E-mail *", placeholder="maria@empresa.com.br")

        c3, c4 = st.columns(2)
        nascimento = c3.date_input(
            "Data de nascimento *",
            value=date(1990, 1, 1),
            min_value=date(1915, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )
        telefone = c4.text_input("Telefone", placeholder="(71) 90000-0000")

        st.subheader("Interesse")

        area = st.selectbox("Area principal *", AREAS)
        area_outra = st.text_input(
            "Qual area?",
            placeholder="preencha apenas se escolheu 'Outra'",
        )
        experiencia = st.select_slider(
            "Experiencia com programacao",
            options=["Nenhuma", "Pouca", "Media", "Muita"],
            value="Pouca",
        )
        comentario = st.text_area("Comentario (opcional)", max_chars=300)

        aceite = st.checkbox("Li e aceito os termos de uso *")

        st.caption("Campos marcados com * sao obrigatorios.")

        # Dentro do form, so este tipo de botao funciona.
        enviou = st.form_submit_button("Enviar inscricao", type="primary", width="stretch")

    if not enviou:
        st.caption(
            "Repare: digitar nos campos acima nao recarrega nada. "
            "O app so reage quando voce clica em Enviar."
        )
    else:
        dados = {
            "nome": nome,
            "email": email,
            "nascimento": nascimento,
            "telefone": telefone,
            "area": area,
            "area_outra": area_outra,
            "experiencia": experiencia,
            "comentario": comentario,
            "aceite": aceite,
        }
        erros = validar(dados)

        if erros:
            st.error(f"Corrija {len(erros)} item(ns) antes de enviar:")
            for campo, mensagem in erros.items():
                st.markdown(f"- **{campo}** — {mensagem}")
        else:
            registro = {
                "Nome": nome.strip(),
                "E-mail": email.strip().lower(),
                "Nascimento": nascimento.strftime("%d/%m/%Y"),
                "Telefone": telefone.strip() or "—",
                "Area": area_outra.strip() if area == "Outra" else area,
                "Experiencia": experiencia,
            }
            st.session_state.inscricoes.append(registro)
            st.success(f"Inscricao de {registro['Nome']} registrada.")
            st.toast("Inscricao enviada", icon="✅")
            st.balloons()

    # ---------------- inscricoes da sessao ----------------
    if st.session_state.inscricoes:
        st.divider()
        st.subheader(f"Inscricoes desta sessao ({len(st.session_state.inscricoes)})")

        tabela = pd.DataFrame(st.session_state.inscricoes)
        st.dataframe(tabela, hide_index=True, width="stretch")

        st.download_button(
            "Baixar em CSV",
            data=tabela.to_csv(index=False).encode("utf-8-sig"),
            file_name="inscricoes.csv",
            mime="text/csv",
        )
        st.caption(
            "Estes dados vivem apenas na memoria desta sessao. "
            "Fechar a aba apaga tudo — persistencia de verdade e o Projeto 08."
        )

    rodape([
        "`st.form` segura os campos ate o envio: um rerun em vez de dezenas.",
        "Dentro do form so funciona `st.form_submit_button`.",
        "Validar numa funcao separada mantem as regras num lugar so.",
        "A mensagem de erro precisa dizer o que corrigir, nao so que falhou.",
        "`st.toast` avisa sem ocupar espaco; `st.success` fica na tela.",
    ])


main()
