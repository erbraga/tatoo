# Selecionar Múltiplos Arquivos — Spec

**Criado em:** 2026-08-16
**Status:** decisões resolvidas — aguardando aprovação final para virar plano

## Contexto (o que encontrei no código)

Estado atual da GUI, implementada em
[2026-08-16-utilizar_gui.md](2026-08-16-utilizar_gui.md):

- `src/tatoo/gui.py` — `build_window()` monta uma janela Tkinter/ttk fixa
  (360×220) com:
  - um `StringVar` `selected_path` guardando **um único** caminho de
    arquivo;
  - botão "Selecionar imagem" que chama
    `filedialog.askopenfilename(...)` (seleção **singular**), filtrado
    para `.png/.jpg/.jpeg/.webp`;
  - botão "Aplicar marca d'água" que chama `apply_watermark(path)` uma
    única vez, sobre o único arquivo selecionado, e mostra o resultado
    (ou erro) em um label.
- `src/tatoo/watermark.py` — `apply_watermark(image_path)` já opera
  sobre **um arquivo por vez** (recebe um único `Path`/`str`, devolve um
  único `Path` de saída). Não há função de lote hoje.
- `src/tatoo/__init__.py` — `main()` só abre a janela (`build_window().mainloop()`).
- `tests/test_gui.py` — testa a criação da janela e a existência dos
  widgets atuais (`select_button`, `apply_button`, `selected_label`,
  `result_label`), todos pensados para um único arquivo.
- A spec anterior (`utilizar_gui`) listou explicitamente **"Processamento
  em lote (batch) de múltiplas imagens"** como **fora de escopo**,
  adiando para uma feature futura — que é esta.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`selecionar_múltiplos_arquivos`). Esta spec assume a interpretação mais
provável — permitir escolher vários arquivos de uma vez no diálogo de
seleção e aplicar a marca d'água em todos eles — e lista como "Decisões
em aberto" os pontos que precisam da sua confirmação antes de virar
plano.

## Problema

Hoje o usuário só consegue selecionar e processar **uma imagem por vez**
na GUI. Para aplicar a marca d'água em várias fotos (o caso de uso mais
comum, já que o `img/` do projeto tem múltiplas fotos reais), é preciso
repetir manualmente "selecionar → aplicar" uma vez para cada arquivo.

## Objetivo

Permitir que o usuário selecione múltiplos arquivos de imagem de uma vez
no diálogo de seleção da GUI, e aplique a marca d'água em todos eles com
uma única ação (um clique).

## Fora de escopo

- Selecionar uma **pasta inteira** (todas as imagens de um diretório) —
  esta feature cobre apenas seleção múltipla manual via diálogo de
  arquivos, não varredura de diretório.
- Alterar os parâmetros hardcoded de `apply_watermark` (logo, posição,
  opacidade) — continuam fixos, como definido na spec anterior.
- Processamento assíncrono/paralelo real (threads, multiprocessing) —
  ver decisão em aberto sobre indicação de progresso.
- Remover ou reordenar arquivos da seleção antes de aplicar (ex.: uma
  lista editável com botão "remover este arquivo").
- Persistência de preferências do usuário.

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados** (unidade equivalente a "models" neste
projeto — módulos Python):
- `src/tatoo/gui.py` (alterado): troca `askopenfilename` por
  `askopenfilenames` (plural, nativo do Tkinter, já suporta seleção de
  1 ou N arquivos); troca o estado interno de "um caminho" para "lista de
  caminhos"; o botão "Aplicar marca d'água" passa a chamar
  `apply_watermark()` para cada arquivo da lista, em sequência.
- `src/tatoo/watermark.py`: não é alterado — continua expondo
  `apply_watermark(image_path)` para um arquivo por vez; a GUI itera
  sobre ela.
- `tests/test_gui.py` (alterado): ajustar as asserções para o novo
  estado (lista de arquivos) conforme necessário.

**Fluxo principal (passo a passo)**:
1. Usuário clica em "Selecionar imagem(ns)".
2. Diálogo nativo abre permitindo selecionar um ou vários arquivos
   `.png/.jpg/.jpeg/.webp` (Ctrl+clique / Shift+clique, conforme o SO).
3. A GUI mostra a **lista** dos arquivos selecionados (nomes),
   substituindo qualquer seleção anterior.
4. Usuário clica em "Aplicar marca d'água".
5. A GUI aplica `apply_watermark()` em cada arquivo selecionado, um a
   um, atualizando um label "Processando X de N..." a cada arquivo, e
   gerando os respectivos `*_marcada.*`. Se um arquivo falhar, o erro é
   registrado e o processamento continua para os próximos.
6. Ao final, a GUI mostra um resumo (ex.: "4 de 5 processadas com
   sucesso") seguido da lista dos arquivos gerados e dos que falharam.
7. A janela continua aberta, permitindo nova seleção (que substitui a
   anterior).

**Casos de borda relevantes**:
- Usuário seleciona só 1 arquivo (deve continuar funcionando igual a
  hoje).
- Usuário cancela o diálogo de seleção: a seleção anterior é mantida
  (cancelar não limpa a seleção já feita).
- Um ou mais arquivos falham durante o processamento em lote (ex.:
  arquivo corrompido) enquanto outros têm sucesso — todos são
  processados e reportados no resumo final.
- Usuário clica em "Aplicar" sem ter selecionado nenhum arquivo.

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — seleção múltipla via diálogo nativo
   (`askopenfilenames`), sem varredura de pasta e sem drag-and-drop.
2. **Exibição da seleção**: **lista completa** com o nome de cada
   arquivo selecionado (não só a contagem).
3. **Tratamento de erro em lote**: **continua processando** os demais
   arquivos mesmo se um falhar, e reporta o resumo (sucessos/falhas) no
   final.
4. **Nova seleção**: **substitui** a seleção anterior (mesmo
   comportamento do diálogo nativo) — não acumula.
5. **Feedback de resultado**: **resumo + lista** dos arquivos
   `*_marcada.*` gerados com sucesso e dos que falharam.
6. **Indicação de progresso**: um **label "Processando X de N..."**
   atualizado entre um arquivo e outro durante o processamento síncrono
   (sem barra gráfica, sem threads).
7. **Tamanho da janela**: a janela **cresce** (deixa de ser 360×220) para
   acomodar as listas de seleção e de resultado, continuando não
   redimensionável pelo usuário.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Nota de design: a spec define que `watermark.py` não é alterado e que "a
GUI itera" sobre `apply_watermark()`. Para manter essa lógica de lote
testável sem depender de simular cliques em widgets (mesmo padrão de teste
já usado em `utilizar_gui`), o loop de processamento fica em uma função
auxiliar **dentro de `src/tatoo/gui.py`** (não em `watermark.py`), chamada
pelo botão "Aplicar marca d'água" — isso respeita o "Módulos
afetados/criados" da spec (só `gui.py` e `test_gui.py` mudam) e permite
testar a função diretamente via import, sem GUI real.

### 1. Trocar seleção para múltiplos arquivos e ajustar a janela
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** troca `filedialog.askopenfilename` por
  `filedialog.askopenfilenames` (plural); o estado interno passa de um
  único caminho para uma lista de `Path`; o botão passa a se chamar
  "Selecionar imagem(ns)"; o label de seleção mostra a lista de nomes dos
  arquivos escolhidos (um por linha), substituindo a seleção anterior a
  cada nova escolha e mantendo a seleção atual se o diálogo for
  cancelado; a janela cresce (deixa de ser 360×220) para acomodar a
  lista.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 2. Implementar processamento em lote com progresso e resumo
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** adiciona uma função auxiliar (ex.: `_process_files`)
  que recebe a lista de caminhos, chama `apply_watermark()` para cada um,
  captura exceções por arquivo (sem interromper o lote) e devolve os
  caminhos gerados com sucesso e os que falharam (com a respectiva
  mensagem de erro). O botão "Aplicar marca d'água" passa a chamar essa
  função, atualizando um label "Processando X de N..." a cada arquivo
  processado (via callback de progresso), e ao final exibe um resumo
  (ex.: "4 de 5 processadas com sucesso") seguido da lista de arquivos
  gerados e dos que falharam. Clicar em "Aplicar" sem seleção mostra
  `messagebox.showerror`, como hoje.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos (testes
  automatizados da lógica vêm na tarefa 4).

### 3. Adicionar fixture de imagem corrompida
- **Arquivo(s):** `tests/conftest.py`
- **O que muda:** adiciona uma fixture (ex.: `broken_image`) que cria em
  `tmp_path` um arquivo com extensão de imagem (ex.: `.png`) mas conteúdo
  inválido, para simular o caso de borda "arquivo corrompido" no
  processamento em lote.
- **Validar:** `uv run pytest --collect-only` executa sem erro de coleta.

### 4. Atualizar e estender `tests/test_gui.py`
- **Arquivo(s):** `tests/test_gui.py`
- **O que muda:** ajusta as asserções existentes para o novo texto do
  botão ("Selecionar imagem(ns)") e para o estado inicial (lista vazia);
  adiciona testes para a função de processamento em lote (`_process_files`
  ou equivalente) cobrindo: (a) todos os arquivos com sucesso (usando as
  fixtures `png_image`, `jpg_image`, `webp_image`), (b) sucesso parcial —
  um arquivo bom e um `broken_image` no mesmo lote, verificando que o bom
  é processado e o quebrado aparece como falha, (c) lista vazia de
  arquivos.
- **Validar:** `uv run pytest -v` mostra todos os testes de GUI passando.

### 5. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Pedir para
  você rodar `uv run tatoo` manualmente e confirmar: seleção de várias
  fotos reais de `img/`, lista exibida corretamente, progresso "X de N"
  visível durante o processamento, e resumo final com os arquivos
  `*_marcada.*` gerados.
