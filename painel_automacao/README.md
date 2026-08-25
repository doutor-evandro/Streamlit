# Painel de Automacoes

App Streamlit de nivel intermediario: KPIs com comparacao de periodo,
filtros na barra lateral, graficos interativos, tabela formatada e
exportacao em CSV.

## Rodar localmente

```bash
cd painel_automacao
pip install -r requirements.txt
streamlit run main.py
```

## Arquivos

| Arquivo            | Papel                                                        |
|--------------------|--------------------------------------------------------------|
| `main.py`          | O app. Funcao `main()` como ponto de entrada.                |
| `dados.py`         | De onde vem o dado. Troque aqui para usar dados reais.       |
| `requirements.txt` | Dependencias instaladas no deploy.                           |

## Recursos do Streamlit demonstrados

- `@st.cache_data` — evita recarregar a base a cada clique
- `st.sidebar` + `date_input` / `multiselect` — filtros
- `st.columns` + `st.metric` com `delta` — KPIs comparativos
- `st.tabs` — organizacao em abas
- `st.bar_chart` / `st.area_chart` — graficos nativos
- `st.column_config` — barras de progresso e formatos na tabela
- `st.download_button` — exportacao
- `st.stop()` — encerra o script quando o filtro fica vazio
