# Mostrar Thumbnails — Spec

**Criado em:** 2026-08-16
**Status:** decisões resolvidas — aguardando aprovação final para virar plano

## Contexto (o que encontrei no código)

Estado atual da GUI em `src/tatoo/gui.py` (após
[2026-08-16-utilizar_gui.md](2026-08-16-utilizar_gui.md),
[2026-08-16-selecionar_múltiplos_arquivos.md](2026-08-16-selecionar_múltiplos_arquivos.md)
e
[2026-08-16-permitir_redimensionar_janela.md](2026-08-16-permitir_redimensionar_janela.md)):

- A lista de arquivos selecionados (`selected_listbox`) e a lista de
  resultado (`result_listbox`) são ambas **`tk.Listbox`** — widgets que só
  exibem **texto puro** por linha (nome do arquivo, ou `"OK: nome"` /
  `"Falhou: nome (erro)"`). **`tk.Listbox` não suporta imagens por item.**
  Não há nenhuma pré-visualização visual das imagens hoje — só nomes de
  arquivo.
- A janela é redimensionável, com mínimo 420×420 e sem máximo (spec
  anterior); as duas listas esticam com peso de grid (`weight=1` nas
  linhas 1 e 5 do frame).
- `src/tatoo/watermark.py` — `apply_watermark(image_path)` já devolve o
  `Path` do arquivo gerado (`*_marcada.*`); nada relacionado a thumbnails
  existe hoje.
- `pyproject.toml` já tem **Pillow** como dependência de runtime — é a
  biblioteca natural para gerar thumbnails (`Image.thumbnail()`), sem
  precisar adicionar nova dependência.
- A spec `utilizar_gui` (primeira versão da GUI) tinha explicitamente
  decidido **"Sem preview de imagem nesta etapa"** ao perguntar sobre o
  escopo mínimo — esta feature reverte essa decisão, adicionando preview
  visual pela primeira vez.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`mostrar_thumbnails`). Esta spec assume a interpretação mais provável —
mostrar uma miniatura da imagem ao lado do nome do arquivo nas listas já
existentes — e lista como "Decisões em aberto" os pontos que precisam da
sua confirmação antes de virar plano.

## Problema

As listas de arquivos selecionados e de resultado mostram só texto (nome
do arquivo). Para confirmar visualmente que a imagem certa foi
selecionada, ou para ver rapidamente o resultado de cada marca d'água
aplicada, o usuário precisa abrir os arquivos manualmente fora da
aplicação — não há nenhuma pré-visualização dentro da GUI.

## Objetivo

Mostrar uma miniatura (thumbnail) de cada imagem ao lado do respectivo
nome de arquivo nas listas da GUI, para que o usuário identifique
visualmente as imagens sem precisar abri-las em outro programa.

## Fora de escopo

- Preview ampliado/em tela cheia ao clicar em uma imagem.
- Comparação lado a lado (antes/depois) de uma mesma imagem.
- Cache persistente de thumbnails em disco entre execuções da aplicação.
- Qualquer alteração nos parâmetros hardcoded de `apply_watermark` (logo,
  posição, opacidade).
- Alterar o comportamento de seleção múltipla, processamento em lote ou
  redimensionamento já implementados — só a exibição visual muda.
- **Thumbnails na lista de resultado** — nesta primeira versão, só a
  lista de arquivos selecionados ganha miniaturas (ver decisão #1); a
  lista de resultado continua como `tk.Listbox` de texto, sem alteração.
- Geração assíncrona/otimizada de thumbnails (threads, lazy loading) —
  geração síncrona é aceita nesta etapa (decisão #5).

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/gui.py` (alterado): a lista de arquivos **selecionados**
  troca de `tk.Listbox` para uma **área rolável customizada**
  (`Canvas`/`Frame` com `Scrollbar`, um `ttk.Label` de imagem + nome por
  "linha"); a lista de **resultado** permanece um `tk.Listbox` de texto,
  sem alteração. `minsize` da janela aumenta para acomodar as linhas com
  thumbnail de 96×96.
- Depende de **Pillow** (já presente) para gerar as miniaturas
  (`Image.thumbnail()` + conversão para `ImageTk.PhotoImage`).

**Fluxo principal (passo a passo)**:
1. Usuário seleciona uma ou mais imagens.
2. Para cada arquivo selecionado, a GUI gera uma miniatura 96×96 (usando
   Pillow) e mostra essa miniatura ao lado do nome do arquivo na área de
   seleção. Se a geração falhar, mostra um ícone/placeholder de erro no
   lugar, mantendo o nome do arquivo.
3. Usuário aplica a marca d'água normalmente — o restante do fluxo
   (progresso, resumo, lista de resultado em texto) não muda.

**Casos de borda relevantes**:
- Arquivo selecionado é inválido/corrompido — a linha mostra um
  ícone/placeholder de erro no lugar da miniatura, sem quebrar a
  aplicação.
- Muitos arquivos grandes selecionados de uma vez (as fotos reais do
  projeto são 4000×1848) — gerar várias miniaturas de forma síncrona pode
  levar um tempo perceptível antes da lista aparecer (aceito nesta
  etapa).

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Onde mostrar thumbnails**: **só na lista de arquivos selecionados**
   (antes de processar). A lista de resultado não ganha thumbnails nesta
   etapa.
2. **Conteúdo do thumbnail no resultado**: não se aplica — a lista de
   resultado não terá thumbnails.
3. **Widget usado**: **área rolável customizada** (`Canvas`/`Frame` com
   `Scrollbar`, `Label` de imagem + nome por linha), não `ttk.Treeview`.
4. **Tamanho do thumbnail**: **96×96** pixels.
5. **Geração síncrona**: **aceitável** — mesmo padrão já usado no
   processamento em lote, sem threads nem otimizações nesta etapa.
6. **Falha ao gerar thumbnail**: mostra um **ícone/placeholder de erro**
   no lugar da miniatura, mantendo o nome do arquivo na linha.
7. **Layout/tamanho da janela**: o `minsize` **aumenta** (deixa de ser
   420×420) para acomodar linhas com thumbnail de 96×96 — tamanho exato a
   definir na fase de plano.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Pré-checagem feita durante o planejamento: `PIL.ImageTk.PhotoImage` já
funciona neste ambiente (testado com `Image.new(...).thumbnail((96, 96))`
+ `ImageTk.PhotoImage(...)`), então não é preciso nenhuma dependência
nova além do Pillow já existente.

Nota de design (novo `minsize`): com thumbnails de 96×96, uma linha
completa (thumbnail + nome + espaçamento) precisa de ~110px de altura;
para mostrar pelo menos 2 linhas na área de seleção sem cortar, além dos
botões, labels de progresso/resumo e da lista de resultado, o plano
propõe **`MIN_WIDTH = 480`, `MIN_HEIGHT = 600`** (ajustável na revisão
deste plano, se preferir outro valor).

Nota de design (testabilidade): seguindo o mesmo padrão já usado em
`_process_files` (feature `selecionar_múltiplos_arquivos`), a geração de
thumbnail e a montagem das linhas da área de seleção ficam em funções
simples e independentes de clique (`_make_thumbnail_image`,
`_populate_selected_area`), testáveis via import direto, sem precisar
simular interação com a GUI.

### 1. Funções de geração de thumbnail e placeholder de erro
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** adiciona `_make_thumbnail_image(path, size=(96, 96))
  -> ImageTk.PhotoImage`, que abre a imagem com Pillow, gera a miniatura
  (`Image.thumbnail`) e converte para `ImageTk.PhotoImage`; adiciona
  `_placeholder_thumbnail_image(size=(96, 96)) -> ImageTk.PhotoImage`,
  um quadrado cinza simples indicando erro (mesmo estilo usado para gerar
  `img/logo.png` na feature `aplicar_marca_dagua_hardcoded`, mas gerado
  em código, não como script avulso). `_make_thumbnail_image` devolve o
  placeholder (em vez de lançar exceção) se a imagem não puder ser
  aberta/processada.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos (teste
  funcional das funções vem na tarefa 3, pois dependem de um `Tk()`
  ativo).

### 2. Trocar a lista de seleção por área rolável com thumbnails
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** substitui `selected_listbox` (`tk.Listbox`) por uma
  área rolável customizada (`_make_scrollable_frame`: `Canvas` + `Frame`
  interno + `Scrollbar`, seguindo o mesmo padrão de
  `_make_listbox_with_scrollbar`); adiciona
  `_populate_selected_area(container, paths) -> list[ImageTk.PhotoImage]`,
  que limpa as linhas antigas e cria uma linha por arquivo (thumbnail via
  `_make_thumbnail_image` + `ttk.Label` com o nome), devolvendo a lista
  de `PhotoImage` gerados; `select_images()` passa a chamar essa função e
  **guardar as referências retornadas** (ex.: em uma lista no escopo de
  `build_window`) para evitar que o Tkinter descarte as imagens por
  garbage collection. `MIN_WIDTH`/`MIN_HEIGHT` e `root.minsize(...)`
  passam para 480×600 (ver nota de design acima); a lista de
  **resultado** (`result_listbox`) não é alterada.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 3. Atualizar e estender `tests/test_gui.py`
- **Arquivo(s):** `tests/test_gui.py`
- **O que muda:** ajusta `test_build_window_creates_expected_widgets`
  para o novo atributo (ex.: `root.selected_area` no lugar de
  `root.selected_listbox`) e `test_build_window_is_resizable_with_minsize`
  para o novo `minsize` (480×600); adiciona testes para
  `_make_thumbnail_image` (gera uma `PhotoImage` válida a partir das
  fixtures `png_image`/`jpg_image`/`webp_image`, e devolve o placeholder
  sem lançar exceção para `broken_image`); adiciona um teste para
  `_populate_selected_area` confirmando que, para uma lista com um
  arquivo bom e um `broken_image`, são criadas 2 linhas na área, sem
  nenhuma exceção propagada.
- **Validar:** `uv run pytest -v` mostra todos os testes de GUI passando.

### 4. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Pedir para
  você rodar `uv run tatoo` manualmente e confirmar: ao selecionar várias
  fotos reais de `img/`, cada uma aparece com uma miniatura reconhecível
  ao lado do nome; selecionar um arquivo inválido (se quiser testar)
  mostra o placeholder de erro; o restante do fluxo (aplicar, progresso,
  resumo, lista de resultado em texto) continua funcionando normalmente.
