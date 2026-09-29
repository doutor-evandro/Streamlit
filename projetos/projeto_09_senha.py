"""PROJETO 09 — App protegido por senha.

CONCEITO NOVO: st.secrets — separar segredo de codigo.

Seu repositorio e publico. Tudo que voce escreve num arquivo .py e visivel
para o mundo inteiro, para sempre — inclusive no historico do Git, mesmo
que voce apague depois.

`st.secrets` le de um arquivo que NUNCA vai para o GitHub:

    local:     .streamlit/secrets.toml   (protegido pelo .gitignore)
    no Cloud:  Manage app → Settings → Secrets

O mesmo mecanismo serve para chave de API, senha de banco e token.

Como rodar sozinho:
    streamlit run projetos/projeto_09_senha.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from comum import cabecalho, configurar_pagina, rodape  # noqa: E402

configurar_pagina("Area protegida", "🔐")

SENHA_PADRAO = "trilha2026"   # so para o app funcionar antes de voce configurar
MAX_TENTATIVAS = 5


def senha_configurada() -> tuple[str, bool]:
    """Devolve (senha, veio_dos_secrets).

    `st.secrets` levanta erro quando nao existe arquivo nenhum — por isso
    o try/except. Assim o projeto roda mesmo antes de voce configurar.
    """
    try:
        return st.secrets["app"]["senha"], True
    except Exception:
        return SENHA_PADRAO, False


def conferir(digitada: str, correta: str) -> bool:
    """Compara os resumos (hash) em vez do texto puro.

    Nao e criptografia forte — e o habito certo: senha nao circula em
    texto puro pela memoria do programa mais do que o necessario.
    """
    return (
        hashlib.sha256(digitada.encode()).hexdigest()
        == hashlib.sha256(correta.encode()).hexdigest()
    )


def tela_de_acesso(correta: str, veio_dos_secrets: bool) -> None:
    st.subheader("🔒 Area restrita")

    if not veio_dos_secrets:
        st.warning(
            f"Nenhum segredo configurado — usando a senha padrao **{SENHA_PADRAO}**. "
            "Veja abaixo como configurar a sua.",
            icon="⚠️",
        )

    if st.session_state.tentativas >= MAX_TENTATIVAS:
        st.error("Muitas tentativas. Recarregue a pagina para tentar de novo.")
        st.stop()

    with st.form("acesso"):
        digitada = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", type="primary", width="stretch"):
            if conferir(digitada, correta):
                st.session_state.autenticado = True
                st.session_state.tentativas = 0
                st.rerun()
            else:
                st.session_state.tentativas += 1
                restantes = MAX_TENTATIVAS - st.session_state.tentativas
                st.error(f"Senha incorreta. {restantes} tentativa(s) restante(s).")

    with st.expander("Como configurar a senha de verdade"):
        st.markdown("**1. No seu computador** — crie `.streamlit/secrets.toml`:")
        st.code('[app]\nsenha = "sua-senha-aqui"\n\n[api]\nchave = "opcional"', language="toml")

        st.markdown("**2. Garanta que o arquivo esta no `.gitignore`:**")
        st.code(".streamlit/secrets.toml", language="text")

        st.markdown(
            "**3. No Streamlit Cloud** — abra o app publicado, clique em "
            "**Manage app** → menu **⋮** → **Settings** → **Secrets**, e cole "
            "o mesmo conteudo. O servidor nao le o arquivo do seu PC."
        )
        st.info(
            "Teste final: procure a senha no GitHub. Se encontrar, algo saiu errado.",
            icon="🔎",
        )


def conteudo_protegido() -> None:
    topo, sair = st.columns([3, 1])
    topo.success("Acesso liberado.")
    if sair.button("Sair", width="stretch"):
        st.session_state.autenticado = False
        st.rerun()

    st.divider()
    st.subheader("Conteudo restrito")
    st.write(
        "Tudo que estiver abaixo da checagem de senha so e executado para "
        "quem entrou. Aqui ficariam relatorios internos, dados de clientes "
        "ou qualquer coisa que nao pode ser publica."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento do mes", "R$ 184.320")
    c2.metric("Contratos ativos", "37")
    c3.metric("Inadimplencia", "2,4%", "-0,6 p.p.")

    st.caption("Numeros ficticios, apenas para ilustrar.")

    with st.expander("Outros segredos disponiveis"):
        try:
            chaves = list(st.secrets.keys())
            st.write("Secoes encontradas no secrets.toml:", chaves)
        except Exception:
            st.write("Nenhum arquivo de segredos configurado ainda.")
        st.caption(
            "Use a mesma estrutura para chave de API e senha de banco: "
            "`st.secrets['api']['chave']`."
        )


def main() -> None:
    cabecalho(9, "🔐 App protegido por senha", "`st.secrets` — segredo fora do codigo")

    st.session_state.setdefault("autenticado", False)
    st.session_state.setdefault("tentativas", 0)

    correta, veio_dos_secrets = senha_configurada()

    if not st.session_state.autenticado:
        tela_de_acesso(correta, veio_dos_secrets)
        # Sem o st.stop(), o conteudo abaixo seria executado e enviado ao
        # navegador mesmo sem login. Esta linha e a tranca de verdade.
        st.stop()

    conteudo_protegido()

    rodape([
        "Segredo nunca entra em arquivo `.py` — vai para `secrets.toml`.",
        "O `.gitignore` e o que impede o segredo de chegar ao GitHub.",
        "No Cloud, os segredos sao colados em Manage app → Settings → Secrets.",
        "`st.stop()` depois da checagem impede o conteudo de ser gerado sem login.",
        "O historico do Git guarda tudo: senha commitada uma vez precisa ser trocada.",
        "Para login com Google ou Microsoft existem `st.login()`, `st.logout()` e `st.user`.",
    ])


main()
