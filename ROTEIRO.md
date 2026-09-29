# Roteiro — 10 projetos depois do Hello World

Uma progressão para aprender Streamlit construindo. Cada projeto acrescenta
**um** conceito novo ao anterior. Faça na ordem: cada um pressupõe o que veio antes.

**Projeto 0 — Hello World.** Concluído. Você já sabe rodar local, versionar no
Git e publicar no Community Cloud. É a base de tudo que vem abaixo.

---

## Como fazer cada projeto

Cada projeto é uma **página nova** no app que você já tem. Nada de repositório
novo nem deploy novo — você reaproveita o endereço que já está no ar.

O ritual, sempre o mesmo:

```bat
cd "C:\Python\0 - Categoria Automacao\Streamlit"
.venv\Scripts\activate

REM 1. crie o arquivo em paginas\  (ex.: paginas\01_conversor.py)
REM 2. registre em main.py:  st.Page("paginas/01_conversor.py", title="Conversor")

streamlit run main.py

REM 3. teste em localhost:8501 ate funcionar
REM 4. publique:
git add -A
git commit -m "projeto 01 - conversor de unidades"
git push
```

Em 1 a 2 minutos a página nova está no ar. **Confira sempre no servidor
também**, não só no `localhost`: o que funciona na sua máquina pode quebrar lá
(biblioteca faltando no `requirements.txt` é a causa nº 1).

### Três regras

1. **Um conceito por vez.** Se um projeto ficou confuso, você provavelmente
   pulou um anterior.
2. **Escreva antes de copiar.** Digitar o código fixa; colar não.
3. **Publique mesmo o que está feio.** O objetivo é fechar o ciclo
   local → Git → servidor dez vezes, até virar automático.

---

## Projeto 1 — Conversor de unidades

**Conceito novo:** widgets e o modelo de rerun.

Construa um conversor de temperatura, distância ou moeda. O usuário escolhe a
unidade de origem e destino, digita o valor, e o resultado aparece.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.number_input`, `st.selectbox`, `st.radio`, `st.slider` |
| **Pronto quando** | O resultado muda sozinho ao mexer no campo, sem botão nenhum |
| **Armadilha** | Querer um botão "Calcular". Não precisa: o Streamlit reroda o script inteiro a cada mudança |

> **A ideia central do Streamlit está aqui.** A cada interação, o arquivo inteiro
> roda de cima a baixo. Não existe "atualizar só um pedaço da tela". Entender
> isto agora evita 90% da confusão nos projetos seguintes.

**Tempo:** 1 a 2 horas.

---

## Projeto 2 — Ficha de produto

**Conceito novo:** layout e organização visual.

Uma página que apresenta um produto, um animal ou um personagem: foto, nome,
descrição, três indicadores numéricos e uma seção de detalhes que abre e fecha.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.columns`, `st.tabs`, `st.expander`, `st.metric`, `st.sidebar`, `st.image`, `st.divider` |
| **Pronto quando** | A tela não é mais uma coluna única; a informação está agrupada e hierarquizada |
| **Armadilha** | Esquecer o `with`. É `with col1:` e não `col1.write(...)` solto no meio do código |

**Tempo:** 1 a 2 horas.

---

## Projeto 3 — Lista de tarefas

**Conceito novo:** `st.session_state` — memória entre reruns.

Um campo de texto, um botão "Adicionar", e a lista aparece embaixo com uma
caixa de marcar e um botão de remover em cada item. Um contador mostra quantas
faltam.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.session_state`, `st.checkbox`, `st.rerun()`, `st.button` com `key` |
| **Pronto quando** | Você adiciona três tarefas seguidas e as três continuam lá |
| **Armadilha** | Usar uma lista Python comum. Ela é recriada a cada rerun e some — tem que viver no `session_state` |

> **Este é o projeto mais importante da lista.** É o degrau onde a maioria trava,
> porque exige entender de verdade o modelo de rerun do Projeto 1. Se emperrar,
> volte e releia aquele.

**Tempo:** 3 a 4 horas.

---

## Projeto 4 — Formulário de inscrição

**Conceito novo:** `st.form` e validação de entrada.

Um cadastro com nome, e-mail, data de nascimento e área de interesse. Só envia
quando tudo estiver preenchido corretamente; mostra erro específico por campo.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.form`, `st.form_submit_button`, `st.date_input`, `st.text_area`, `st.error`, `st.success`, `st.toast` |
| **Pronto quando** | Digitar no formulário não dispara rerun; só o botão de envio dispara |
| **Armadilha** | Colocar um `st.button` comum dentro do form. Dentro do form só funciona o `st.form_submit_button` |

**Tempo:** 2 a 3 horas.

---

## Projeto 5 — Limpador de planilhas

**Conceito novo:** receber arquivo do usuário e devolver arquivo pronto.

O usuário envia um CSV ou Excel. O app mostra as primeiras linhas, quantas
linhas e colunas tem, quantos valores vazios, remove duplicatas, e devolve a
planilha limpa para download.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.file_uploader`, `st.download_button`, `st.dataframe`, `st.column_config`, `pandas` |
| **Pronto quando** | Funciona com uma planilha de verdade sua, não só com o exemplo |
| **Armadilha** | Não tratar o caso "nenhum arquivo enviado ainda". Use `if arquivo is None: st.info(...); st.stop()` |

> **Aqui o app deixa de ser exercício e vira ferramenta.** É o primeiro que você
> pode mandar para outra pessoa usar.

**Tempo:** 3 a 5 horas.

---

## Projeto 6 — Painel de vendas

**Conceito novo:** `@st.cache_data` e gráficos.

Um painel sobre dados reais (use uma planilha sua, ou dados públicos do
IBGE/gov.br): filtros na barra lateral, indicadores no topo com variação, e
dois ou três gráficos que respondem aos filtros.

| Item | Detalhe |
|---|---|
| **Funções novas** | `@st.cache_data`, `st.line_chart`, `st.bar_chart`, `st.area_chart`, `st.metric` com `delta`, `st.multiselect`, `st.date_input` com intervalo |
| **Pronto quando** | Mexer num filtro responde na hora, sem recarregar a base |
| **Armadilha** | Esquecer o cache. Sem ele, o arquivo é lido do disco a cada clique e o app fica lento |

Você já viu um pronto no `painel.py`. **Agora faça o seu, do zero**, com dados
que te interessam. Consultar o pronto vale; copiar não ensina.

**Tempo:** 5 a 8 horas.

---

## Projeto 7 — Consulta a uma API

**Conceito novo:** buscar dados de fora, com cache temporizado e tratamento de erro.

Escolha uma API pública e gratuita: ViaCEP (endereço por CEP), AwesomeAPI
(cotação de moedas) ou Open-Meteo (previsão do tempo). O usuário digita algo,
o app consulta e mostra o resultado formatado.

| Item | Detalhe |
|---|---|
| **Funções novas** | `requests`, `@st.cache_data(ttl=600)`, `st.spinner`, `st.status`, `try/except` |
| **Pronto quando** | Digitar um CEP inválido mostra mensagem clara em vez de tela vermelha de erro |
| **Armadilha** | Cachear para sempre. Cotação precisa de `ttl`; senão o app mostra o preço de ontem |

> **Lição de resiliência:** a internet falha. Todo acesso externo vai dentro de
> `try/except`, e o app precisa continuar utilizável quando a API não responde.

**Tempo:** 4 a 6 horas.

---

## Projeto 8 — Cadastro com banco de dados

**Conceito novo:** persistir dados de verdade, e por que isso é diferente no servidor.

Um CRUD completo: cadastrar, listar, editar e excluir registros em um banco
SQLite. Tabela editável direto na tela.

| Item | Detalhe |
|---|---|
| **Funções novas** | `sqlite3`, `st.data_editor`, `st.cache_resource`, `st.connection` |
| **Pronto quando** | Você fecha o app, abre de novo, e os dados continuam lá |
| **Armadilha** | **A grande lição deste projeto:** no Community Cloud o disco é temporário. O arquivo SQLite é apagado a cada reinício ou hibernação |

Publique mesmo assim e veja o dado sumir depois que o app dormir. Aí você
entende, por experiência própria, por que aplicações reais usam banco externo
(Supabase, Neon ou Google Sheets têm faixa gratuita) — e por que
`st.cache_resource` existe, separado do `cache_data`: conexão de banco se
reaproveita, não se copia.

**Tempo:** 6 a 10 horas.

---

## Projeto 9 — App protegido por senha

**Conceito novo:** `st.secrets` — separar segredo de código.

Uma tela de acesso antes do conteúdo. A senha **não** fica no código: fica em
`.streamlit/secrets.toml` localmente, e no painel do Streamlit Cloud quando
publicado.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.secrets`, `st.text_input(type="password")`, `st.stop()`, `.gitignore` |
| **Pronto quando** | Você procura a senha no GitHub e não a encontra em lugar nenhum |
| **Armadilha** | Commitar o `secrets.toml`. Confira o `.gitignore` **antes** do primeiro `git push` |

No Cloud: **Manage app → Settings → Secrets**, e cole o mesmo conteúdo do
arquivo local.

> Para login de verdade (Google, Microsoft), existem `st.login()`, `st.logout()`
> e `st.user`. Exigem configurar um provedor de identidade — deixe para depois,
> mas saiba que existem.

**Tempo:** 3 a 4 horas.

---

## Projeto 10 — Projeto final integrado

**Conceito novo:** juntar tudo, e desempenho.

Escolha um problema real do seu dia a dia e construa o app completo: várias
páginas, upload de arquivo, banco de dados, uma API externa, acesso protegido
e exportação de relatório.

| Item | Detalhe |
|---|---|
| **Funções novas** | `st.navigation` com seções, `st.fragment`, `st.query_params`, `st.set_page_config` avançado, tema em `.streamlit/config.toml` |
| **Pronto quando** | Outra pessoa usa sem você explicar como |
| **Armadilha** | Começar grande demais. Escreva as telas no papel antes de abrir o editor |

`st.fragment` é a novidade que fecha o ciclo: ele permite rerodar **só um
pedaço** da página, em vez do arquivo inteiro. É a resposta madura para a
limitação que você conheceu lá no Projeto 1.

Este é o app que vai no seu portfólio.

**Tempo:** 15 a 30 horas.

---

## Resumo da progressão

| # | Projeto | Conceito |
|---|---|---|
| 0 | Hello World | Rodar, versionar, publicar |
| 1 | Conversor de unidades | Widgets e o modelo de rerun |
| 2 | Ficha de produto | Layout e organização |
| 3 | Lista de tarefas | `session_state` — memória |
| 4 | Formulário de inscrição | `st.form` e validação |
| 5 | Limpador de planilhas | Entrada e saída de arquivos |
| 6 | Painel de vendas | Cache e gráficos |
| 7 | Consulta a uma API | Dados externos e falhas |
| 8 | Cadastro com banco | Persistência e disco efêmero |
| 9 | App protegido | Segredos fora do código |
| 10 | Projeto final | Integração e desempenho |

**Ritmo sugerido:** um projeto por semana. Em dois meses e meio você sai de
Hello World a um app publicado que outras pessoas usam.

---

## Onde consultar

- Referência de funções: [docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference)
- Exemplos prontos: [streamlit.io/gallery](https://streamlit.io/gallery)
- Fórum da comunidade: [discuss.streamlit.io](https://discuss.streamlit.io)
- Seu manual de operação: `MANUAL.md`, nesta mesma pasta

*Roteiro gerado em 24/09/2026.*
