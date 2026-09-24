# Manual do Projeto Streamlit

**Para quem nunca mexeu com isto antes.**
Siga na ordem. Cada comando está pronto para copiar e colar.

- **App no ar:** https://doutor-evandro-hello.streamlit.app/
- **Código no GitHub:** https://github.com/doutor-evandro/Streamlit
- **Pasta no computador:** `C:\Python\0 - Categoria Automacao\Streamlit`

---

## 1. Entenda o desenho antes de digitar

O projeto vive em **três lugares**. Confundi-los é a causa de quase toda dúvida.

```
   SEU COMPUTADOR              GITHUB                  STREAMLIT CLOUD
   ==============              ======                  ===============
   Onde você escreve    →   Onde o código fica   →    Onde o app fica
   e testa o código          guardado e versionado      público na internet

   streamlit run main.py     git push                  (atualiza sozinho)
   → localhost:8501          → envia as mudanças        → endereço .streamlit.app
```

O fluxo é sempre da esquerda para a direita:

1. Você **edita** no computador e testa em `localhost`.
2. Você **envia** para o GitHub.
3. O Streamlit Cloud **percebe sozinho** e republica o site.

Você nunca envia arquivos direto para o servidor. O GitHub é a ponte obrigatória.

---

## 2. O que precisa estar instalado

Confira os três antes de começar. Abra o **Prompt de Comando** do Windows e digite cada linha:

| Digite | Deve aparecer | Se der erro |
|---|---|---|
| `python --version` | `Python 3.11...` | Instale em [python.org](https://python.org) e marque **"Add Python to PATH"** |
| `git --version` | `git version 2...` | Instale em [git-scm.com](https://git-scm.com/download/win), pode dar Next em tudo |
| `code --version` | um número | Instale o [VS Code](https://code.visualstudio.com) |

Você também precisa de uma conta no [GitHub](https://github.com) e uma no [Streamlit Cloud](https://share.streamlit.io) — a do Streamlit você cria entrando com a do GitHub.

---

## 3. Rodar no seu computador

### 3.1 Primeira vez (faz só uma vez)

Abra o VS Code, vá em **Arquivo → Abrir Pasta** e escolha a pasta do projeto. Depois abra o terminal com **Ctrl + '** e cole:

```bat
cd "C:\Python\0 - Categoria Automacao\Streamlit"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Depois do `activate`, o começo da linha passa a mostrar `(.venv)`. **Esse é o sinal de que deu certo.**

> **O que é o `.venv`?** Uma caixa de bibliotecas exclusiva deste projeto. Sem ela, instalar algo para um projeto pode quebrar outro — foi exatamente o que aconteceu neste aqui em agosto. A caixa fica na sua máquina e nunca vai para o GitHub.

### 3.2 Todas as outras vezes

```bat
cd "C:\Python\0 - Categoria Automacao\Streamlit"
.venv\Scripts\activate
streamlit run main.py
```

O navegador abre sozinho em **http://localhost:8501**.

### 3.3 O que você vai ver

Uma página com menu à esquerda e duas opções: **Hello World** e **Painel de Automações**.

### 3.4 Três avisos importantes

**Não use o botão ▶ Run do VS Code.** Ele roda `python main.py`, e aí nada acontece. App Streamlit só sobe com `streamlit run`.

**Deixe o terminal aberto.** Ele é o motor. Fechar o terminal ou apertar `Ctrl + C` derruba o site.

**`localhost` é só seu.** Quer dizer "este computador aqui". Ninguém de fora enxerga. Para o mundo ver, é preciso publicar — Parte 5.

### 3.5 Editar e ver a mudança

Altere algo em `paginas/hello.py`, salve com `Ctrl + S`, e volte ao navegador. Aparece um botão **Rerun** no canto superior direito — clique. É assim que se trabalha: edita, salva, atualiza.

---

## 4. Enviar as mudanças para o GitHub

São três comandos, sempre os mesmos, no terminal dentro da pasta do projeto:

```bat
git add -A
git commit -m "escreva aqui o que voce mudou"
git push
```

O que cada um faz:

- **`git add -A`** — separa tudo que mudou
- **`git commit -m "..."`** — embrulha num pacote com uma etiqueta; **fica só no seu PC**
- **`git push`** — envia o pacote para o GitHub

O `push` é o que realmente sobe. Parar no `commit` é o engano mais comum: parece que salvou, mas não saiu da máquina.

> **Pelo VS Code, se preferir clicar:** ícone de Controle de Código-Fonte (`Ctrl+Shift+G`) → escreva a mensagem na caixa → **Commit** → depois **Sync Changes**. São **dois** botões, nessa ordem. O segundo é o que envia.

### Pendência a resolver

A pasta antiga `painel_automacao` foi apagada do computador, mas a exclusão nunca foi confirmada — ela ainda aparece no GitHub. Para limpar, rode uma vez:

```bat
cd "C:\Python\0 - Categoria Automacao\Streamlit"
git add -A
git commit -m "remove pasta painel_automacao duplicada"
git push
```

Isso não afeta o app no ar: ele lê o `main.py` da raiz, não aquela pasta.

---

## 5. Publicar no servidor

### 5.1 O app já está publicado

Não é preciso fazer nada. O Streamlit Cloud guarda três informações — repositório `doutor-evandro/Streamlit`, branch `main`, arquivo `main.py` — e vigia o GitHub sozinho.

**Depois de cada `git push`, espere 1 a 2 minutos e recarregue a página.** A mudança aparece. Não existe botão de "publicar".

### 5.2 Se um dia precisar criar de novo

Em [share.streamlit.io](https://share.streamlit.io), botão **Create app**:

| Campo | Valor |
|---|---|
| Repository | `doutor-evandro/Streamlit` |
| Branch | `main` |
| Main file path | `main.py` |
| Endereço | um nome único, ex.: `doutor-evandro-hello` |

Clique em **Deploy** e espere de 3 a 5 minutos na primeira vez.

### 5.3 O repositório precisa ser público

No plano gratuito, repositório privado exige permissões extras e só permite **um** app privado. Se o link der erro 404 para outras pessoas, o repositório está privado: vá em **Settings → Danger Zone → Change visibility → Make public**.

### 5.4 O app "dorme"

Sem visitas por alguns dias, o app hiberna. Quem abrir vê um botão para acordá-lo e espera uns 30 segundos. **É normal no plano gratuito, não é defeito.**

### 5.5 Por que o `requirements.txt` é obrigatório

O servidor não tem o seu `.venv`. Ele lê esse arquivo e monta o ambiente do zero. **Biblioteca nova que você instalar tem que ser escrita ali**, senão funciona no seu PC e quebra no servidor.

---

## 6. O ciclo do dia a dia

```
1. cd "C:\Python\0 - Categoria Automacao\Streamlit"
2. .venv\Scripts\activate
3. streamlit run main.py        → testa em localhost:8501
4. edita, salva, confere
5. Ctrl + C                     → para o servidor local
6. git add -A
7. git commit -m "o que mudou"
8. git push                     → o site atualiza sozinho
```

---

## 7. Os arquivos

```
Streamlit\
├── main.py            ← porteiro: monta o menu, não desenha conteúdo
├── dados.py           ← de onde vêm os dados do painel
├── requirements.txt   ← lista de bibliotecas (o servidor lê isto)
├── README.md          ← descrição que aparece no GitHub
├── .gitignore         ← o que NÃO vai para o GitHub
├── paginas\
│   ├── hello.py       ← página 1
│   └── painel.py      ← página 2
├── .venv\             ← bibliotecas locais (não vai para o GitHub)
└── .git\              ← histórico do Git (não mexa)
```

**Para criar uma página nova:** crie o arquivo em `paginas\` e acrescente um `st.Page("paginas/nome.py", title="Nome")` na lista dentro do `main.py`. Não há passo 3.

**Detalhe:** arquivos em `paginas\` não têm `main()` nem `if __name__`. O Streamlit executa o arquivo inteiro, de cima a baixo, toda vez que a página é aberta.

---

## 8. Problemas e soluções

Todos abaixo aconteceram de verdade neste projeto.

### `ModuleNotFoundError: No module named 'dados'`
Você está na pasta errada. Rode o `cd` para a raiz do projeto.

### `ModuleNotFoundError: No module named 'streamlit'`
Esqueceu de ativar o ambiente. Rode `.venv\Scripts\activate` — confira se aparece `(.venv)`.

### `ValueError: numpy.dtype size changed`
Pandas e numpy de gerações incompatíveis. Solução definitiva — recriar o ambiente:
```bat
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### `fatal: Unable to create ... index.lock: File exists`
Um comando Git foi interrompido e deixou uma trava. Nada está quebrado. Apague o arquivo:
```bat
del "C:\Python\0 - Categoria Automacao\Streamlit\.git\index.lock"
```
Se disser que está em uso, feche o VS Code, reabra e repita.

### O link do GitHub dá 404 para outras pessoas
O repositório está privado. Veja o item 5.3.

### Rodei `python main.py` e não aconteceu nada
Use `streamlit run main.py`. Veja o item 3.4.

### Mudei o código e o site não atualizou
Faltou o `git push`. Só `commit` não envia. Confira em github.com/doutor-evandro/Streamlit se a mudança chegou.

---

## 9. Glossário

| Termo | Em português claro |
|---|---|
| **Streamlit** | Biblioteca que transforma código Python em site |
| **localhost:8501** | Endereço do site rodando no seu próprio PC |
| **Porta (8501)** | O "número da sala" do serviço dentro da máquina |
| **Repositório** | A pasta do projeto guardada no GitHub |
| **Commit** | Pacote de mudanças com etiqueta; fica no seu PC |
| **Push** | Envia os commits para o GitHub |
| **Branch `main`** | A linha principal do histórico |
| **Deploy** | Publicar o app no servidor |
| **Ambiente virtual (`.venv`)** | Caixa de bibliotecas exclusiva do projeto |
| **`requirements.txt`** | Lista de bibliotecas que o servidor precisa instalar |
| **`.gitignore`** | Lista do que não deve ir para o GitHub |

---

## 10. Histórico de desenvolvimento

### Etapa 1 — Hello World local *(24/08/2026)*
Criados `main.py` e `requirements.txt`. Primeira execução em `localhost:8501`.
**Aprendizado:** Streamlit sobe um servidor local; a página é o app.

### Etapa 2 — Publicação *(24/08/2026)*
Repositório criado pelo VS Code e publicado no Streamlit Cloud.
**Problema:** repositório nasceu privado, link dava 404 para terceiros. Resolvido tornando-o público.
**Commit:** `32a4ca3 first commit`

### Etapa 3 — Painel de Automações *(25/08/2026)*
App intermediário com filtros, KPIs comparativos, gráficos, tabela formatada e exportação CSV. Dados fictícios isolados em `dados.py`.
**Problema:** `ValueError: numpy.dtype size changed` — pandas antigo com numpy novo no Python geral do Windows. Resolvido criando um ambiente virtual.
**Aprendizado:** um `.venv` por projeto, sempre.

### Etapa 4 — App multi-páginas *(25/08/2026)*
Os dois apps unificados sob um endereço só, com `st.navigation`. O `main.py` deixou de desenhar conteúdo e virou apenas o menu.
**Problema:** `index.lock` travando o Git. Resolvido apagando o arquivo.
**Commit:** `fd80a5b app multi-paginas`

### Pendente
Confirmar a exclusão da pasta `painel_automacao`, que ainda consta no GitHub. Veja o item 4.

---

## 11. Para ir adiante

- Trocar os dados fictícios por uma planilha real: mexe só no `dados.py`
- Criar uma terceira página: item 7
- Documentação oficial: [docs.streamlit.io](https://docs.streamlit.io)
- Galeria de exemplos: [streamlit.io/gallery](https://streamlit.io/gallery)

---

*Manual gerado em 24/09/2026. Se a pasta ou os endereços mudarem, atualize o topo deste arquivo.*
