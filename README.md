# Apps Streamlit — Evandro

App multi-paginas: um unico endereco servindo varias telas, com menu lateral.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

## Estrutura

```
main.py              # ponto de entrada: monta o menu (st.navigation)
dados.py             # de onde vem o dado -- troque aqui para usar dados reais
paginas/
  hello.py           # pagina 1: Hello World
  painel.py          # pagina 2: Painel de Automacoes
requirements.txt     # dependencias instaladas no deploy
```

## Como adicionar uma pagina nova

1. Crie o arquivo em `paginas/`.
2. Acrescente um `st.Page(...)` na lista dentro de `main.py`.

Nao ha passo 3.

## Recursos do Streamlit demonstrados

- `st.navigation` + `st.Page` — navegacao multi-paginas
- `@st.cache_data` — evita recarregar a base a cada clique
- `st.sidebar` + `date_input` / `multiselect` — filtros
- `st.columns` + `st.metric` com `delta` — KPIs comparativos
- `st.tabs` — organizacao em abas
- `st.bar_chart` / `st.area_chart` — graficos nativos
- `st.column_config` — barras de progresso e formatos na tabela
- `st.download_button` — exportacao
- `st.stop()` — encerra o script quando o filtro fica vazio
