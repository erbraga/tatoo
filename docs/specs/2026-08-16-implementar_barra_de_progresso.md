# Implementar Barra de Progresso — Spec

**Criado em:** 2026-08-16
**Status:** aprovado

## Contexto (o que encontrei no código)

- `src/tatoo/gui.py::build_window()` já tem uma indicação de progresso
  **textual**, não visual: um `ttk.Label` (`progress_label`) ligado a
  `progress_text` (`tk.StringVar`), atualizado pela função interna
  `report_progress(index, total)`, que define o texto como
  `"Processando {index} de {total}..."` e chama `root.update_idletasks()`
  para forçar a atualização da tela durante o loop síncrono.
- `report_progress` é passada como o callback `on_progress` para
  `_process_files()` (em `_process_files`, chamado uma vez por arquivo,
  antes de processar cada um — ou seja, já sabemos o total (`len(paths)`)
  e o índice atual de cada arquivo, exatamente o que uma barra de
  progresso **determinada** (não indeterminada) precisa).
- Não existe nenhum `ttk.Progressbar` em nenhum lugar do código hoje —
  toda a indicação de progresso é textual.
- Ao final do processamento, `apply_to_selected()` limpa
  `progress_text.set("")` e escreve o resumo em `result_summary_text`
  (ex.: "4 de 5 processadas com sucesso").
- Layout atual (grid dentro do `frame`, linha por linha):
  `0` botão selecionar, `1` área de seleção com thumbnails (peso 1,
  estica), `2` botão aplicar, `3` `progress_label`, `4`
  `result_summary_label`, `5` lista de resultado (peso 1, estica).
  Há espaço na linha 3 (hoje só o texto) para acomodar ou substituir por
  uma barra visual.
- `tests/test_gui.py` testa a existência de `root.progress_label`
  (`winfo_exists()`), mas nada relacionado a uma barra de progresso
  visual, já que ela não existe ainda.
- **Importante para o fluxo de duas fases pedido**: `select_images()` /
  `_populate_selected_area()` (a etapa de "importar" as imagens
  selecionadas, gerando as miniaturas) **não tem nenhum callback de
  progresso hoje** — o loop que gera os thumbnails em
  `_populate_selected_area()` roda do início ao fim sem reportar
  índice/total, diferente de `_process_files()`, que já tem `on_progress`.
  Ou seja, o texto "importando X de N..." e a barra vermelha da fase de
  importação exigem adicionar um mecanismo de progresso novo, que hoje
  não existe em lugar nenhum do código (só existe para a fase de aplicar
  a marca d'água).
- `ttk.Progressbar` não tem um parâmetro simples de "cor" — mudar a cor
  do preenchimento (`red`/`green`) exige configurar um `ttk.Style`
  customizado (ex.: `style.configure("Vermelha.Horizontal.TProgressbar",
  background="red")`) e trocar o `style` da barra entre as fases. Isso só
  funciona de forma confiável em certos temas ttk (ex.: `clam`) — com o
  tema padrão do sistema (mantido por decisão do usuário, ver "Decisões
  em aberto" #8), a cor pode **não aparecer** em alguns temas/plataformas
  (ex.: Windows com tema nativo `vista`/`xpnative`, que costuma ignorar
  cor de fundo customizada em widgets ttk). Ciente do risco, o usuário
  optou por manter `ttk.Progressbar` mesmo assim, em vez de trocar para
  uma barra desenhada manualmente (`tk.Canvas`), que garantiria a cor em
  qualquer plataforma.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`implementar_barra_de_progresso`). O nome é direto — trocar/complementar
o texto de progresso atual por um `ttk.Progressbar` visual — mas há
detalhes de comportamento e layout sem valor definido, listados em
"Decisões em aberto".

## Problema

O progresso do processamento em lote hoje só é indicado por texto
("Processando 3 de 5..."), sem nenhum elemento visual. Para lotes
maiores, uma barra de progresso visual comunica o andamento de forma mais
imediata do que ler um número que muda.

## Objetivo

Adicionar uma barra de progresso visual (`ttk.Progressbar`) que reflita o
andamento em **duas fases** do fluxo da GUI: a **importação** das imagens
selecionadas (geração das miniaturas, barra vermelha, texto "importando X
de N...") e a **aplicação da marca d'água** (barra verde, texto
"Processando X de N..." já existente).

## Fora de escopo

- Processamento assíncrono/paralelo (threads) — a barra reflete o mesmo
  processamento síncrono já existente, só adiciona a visualização.
- Barra de progresso "geral" que sobreviva a múltiplas sessões/lotes
  (ex.: histórico).
- Cancelar o processamento em andamento pela barra (botão de cancelar).
- Mudar a lógica de `_process_files()` além de, se necessário, expor mais
  informação ao callback (o callback já recebe `index`/`total`, que é o
  suficiente para uma barra determinada).

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/gui.py` (alterado):
  - adiciona um `ttk.Progressbar` (`mode="determinate"`) na janela,
    visível desde a abertura (vazia, `value=0`), ao lado/abaixo do
    `progress_label` textual existente (que não é removido);
  - `_populate_selected_area()` ganha um parâmetro `on_progress` (mesmo
    formato de `_process_files`), chamado a cada miniatura gerada, para
    alimentar a fase de "importação";
  - `select_images()` passa um callback para `_populate_selected_area()`
    que atualiza a barra (cor vermelha) e um novo texto "importando X de
    N...";
  - `report_progress()` (fase de aplicar) continua atualizando a mesma
    barra, agora trocando para a cor verde, e o texto "Processando X de
    N..." já existente;
  - a cor da barra é trocada entre as fases via `ttk.Style` (dois estilos
    customizados, ex.: `Importando.Horizontal.TProgressbar` (vermelho) e
    `Processando.Horizontal.TProgressbar` (verde)), **sem** forçar o tema
    `clam` — mantendo o tema padrão do sistema, por decisão do usuário
    (a cor pode não aparecer em todas as plataformas/temas, risco aceito
    conscientemente);
  - o mesmo `progress_label`/`progress_text` existente é reaproveitado
    para os dois textos ("importando X de N..." / "Processando X de
    N..."), sem criar um label novo;
  - é a **mesma barra** (`ttk.Progressbar`) nas duas fases — reinicia
    (`value=0`) e troca de estilo/cor ao passar da importação para a
    aplicação.
- `tests/test_gui.py` (alterado): novos testes verificando que a barra é
  criada (`winfo_exists()`, `value` inicial 0), que responde ao callback
  de progresso da fase de importação e da fase de aplicar, e que o estilo
  (nome do style aplicado) muda entre as duas fases.

**Fluxo principal (passo a passo)**:
1. Janela abre com a barra de progresso vazia e visível.
2. Usuário clica em selecionar imagens.
3. Usuário seleciona imagens e clica em Open.
4. A barra vai enchendo com a cor **vermelha** conforme cada arquivo é
   importado (miniatura gerada), um a um, junto com o texto "importando X
   de N...".
5. Ao final da importação, a barra fica cheia (100%) e permanece assim
   até o próximo passo.
6. Usuário clica em "Aplicar marca d'água".
7. A barra vai enchendo com a cor **verde** conforme cada arquivo é
   processado, um a um, junto com o texto "Processando X de N..." já
   existente.
8. Ao final do lote, a barra fica cheia (100%) e permanece assim até a
   próxima seleção; o resumo de resultado é exibido como já acontece
   hoje.

**Casos de borda relevantes**:
- Lote de 1 arquivo só — a barra deve ir de 0% a 100% em uma única
  atualização, sem parecer "quebrada" (ex.: pular direto pra 100%, o que
  é esperado e correto).
- Usuário clica em "Aplicar" sem nada selecionado — nenhuma barra deve
  aparecer/mover (mesmo comportamento de erro já existente,
  `messagebox.showerror`, antes de chegar em `_process_files`).
- Novo lote depois de um lote já concluído — a barra deve resetar
  corretamente para o novo processamento, não continuar do estado do
  lote anterior.

## Decisões em aberto

Nenhuma pendente — todas as 8 decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — `ttk.Progressbar` determinado, sincronizado
   com o callback `on_progress` já existente em `_process_files()`.
2. **Relação com o texto atual**: **os dois convivem** — a barra visual
   fica ao lado/abaixo do texto "Processando X de N...", que **não** é
   removido.
3. **Estado após concluir o lote**: a barra **fica cheia (100%)** até a
   próxima seleção de arquivos.
4. **Estado inicial**: a barra aparece **vazia e visível desde a
   abertura da janela**, antes de qualquer processamento.
5. **Estratégia de validação**: confirmado — teste automatizado cobre a
   lógica (`maximum`/`value` respondendo ao callback), sem simular clique
   real; validação visual real fica por sua conta via `uv run tatoo`.
6. **Uma barra reaproveitada, não duas**: confirmado — a mesma
   `ttk.Progressbar` reinicia e troca de cor/estilo entre a fase de
   importação (vermelha) e a de aplicação (verde).
7. **Texto**: confirmado — o mesmo `progress_label`/`progress_text`
   existente troca de texto conforme a fase ("importando X de N..." →
   "Processando X de N..."), sem criar um label novo.
8. **Tema ttk**: o usuário optou por **manter o tema padrão do sistema**
   (não forçar `clam`), ciente de que isso significa que a cor
   vermelho/verde da barra **pode não aparecer** em algumas
   plataformas/temas (ex.: Windows com tema nativo). Perguntado se
   preferia trocar para uma barra desenhada manualmente (`tk.Canvas`, que
   garantiria a cor em qualquer plataforma), o usuário optou por manter
   `ttk.Progressbar` mesmo assim — risco aceito conscientemente.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Nota de design (testabilidade): `report_progress` (fase de aplicar) e o
novo callback da fase de importação são funções internas de
`build_window()` (closures), assim como `select_images`/`apply_to_selected`
já são hoje. Seguindo o mesmo padrão já usado no projeto para testar esse
tipo de função sem simular clique (expor widgets internos via atributos
em `root`, ex.: `root.select_button`, `root.selected_area`), este plano
expõe também os dois callbacks de progresso como `root.on_import_progress`
e `root.on_apply_progress`, e a própria barra como `root.progress_bar` —
permitindo chamar os callbacks diretamente nos testes e verificar
`value`/`maximum`/`style` resultantes.

Nota de layout: a barra é posicionada **acima** do `progress_label`
existente (linha 3), empurrando `result_summary_label` (linha 4→5) e a
lista de resultado (linha 5→6) uma posição abaixo; o peso de grid da
linha da lista de resultado (`frame.rowconfigure(5, weight=1)`) passa
para a linha 6.

### 1. Adicionar `ttk.Progressbar` ao layout e estilos de cor
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** adiciona `progress_bar = ttk.Progressbar(frame,
  mode="determinate", value=0)` na linha 3 do grid (acima do
  `progress_label`, que passa para a linha 4); ajusta as demais linhas do
  grid (`result_summary_label` → 5, `result_listbox` → 6) e o
  `rowconfigure` de peso correspondente; define dois `ttk.Style`
  customizados (`Importando.Horizontal.TProgressbar` em vermelho,
  `Processando.Horizontal.TProgressbar` em verde) via
  `ttk.Style().configure(...)`, **sem** chamar `theme_use()` (mantém o
  tema padrão do sistema, por decisão do usuário).
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos
  (validação funcional nas tarefas 2–4).

### 2. Progresso na fase de importação
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** `_populate_selected_area()` ganha um parâmetro
  `on_progress: Callable[[int, int], None] | None = None` (mesmo formato
  de `_process_files`), chamado a cada miniatura gerada, antes de
  processá-la; `select_images()` define um callback interno
  (`on_import_progress`) que reseta a barra (`value=0`), aplica o estilo
  vermelho, atualiza `maximum`/`value` e o texto para "importando X de
  N...", e passa esse callback para `_populate_selected_area()`; ao
  final da importação, a barra permanece cheia (100%). O callback é
  exposto como `root.on_import_progress` para testes.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 3. Progresso na fase de aplicar
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** `report_progress()` (já existente) passa a resetar a
  barra (`value=0`) no início do lote, aplicar o estilo verde, atualizar
  `maximum`/`value` junto com o texto "Processando X de N..." já
  existente, e a barra permanece cheia (100%) ao final do lote. O
  callback é exposto como `root.on_apply_progress` para testes.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 4. Testes da barra de progresso
- **Arquivo(s):** `tests/test_gui.py`
- **O que muda:** novo teste confirmando que `root.progress_bar` existe
  (`winfo_exists()`) e começa com `value == 0`; testes chamando
  `root.on_import_progress(i, total)` e `root.on_apply_progress(i,
  total)` diretamente (sem simular clique), verificando que `value` e
  `maximum` da barra refletem os argumentos, e que o `style` aplicado é
  o vermelho (`Importando...`) ou verde (`Processando...`) conforme a
  fase chamada.
- **Validar:** `uv run pytest -v` mostra os novos testes passando.

### 5. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Pedir para
  você rodar `uv run tatoo`, selecionar algumas imagens e aplicar a marca
  d'água, confirmando visualmente as duas fases da barra — lembrando que,
  por decisão já tomada (#8), a cor vermelho/verde pode não aparecer
  dependendo do tema do seu sistema, mesmo que o preenchimento
  (`value`/`maximum`) funcione normalmente.
