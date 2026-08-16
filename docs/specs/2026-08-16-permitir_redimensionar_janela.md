# Permitir Redimensionar Janela — Spec

**Criado em:** 2026-08-16
**Status:** decisões resolvidas — aguardando aprovação final para virar plano

## Contexto (o que encontrei no código)

Estado atual da GUI em `src/tatoo/gui.py` (após
[2026-08-16-utilizar_gui.md](2026-08-16-utilizar_gui.md) e
[2026-08-16-selecionar_múltiplos_arquivos.md](2026-08-16-selecionar_múltiplos_arquivos.md)):

- `build_window()` cria a janela com `root.geometry("420x420")` e
  **`root.resizable(False, False)`** — o usuário não consegue redimensionar
  nem maximizar a janela hoje.
- O layout é um único `ttk.Frame(root, padding=16)` posicionado com
  `frame.grid()` (sem `sticky`), contendo, em coluna única: botão
  "Selecionar imagem(ns)", label de seleção (lista de nomes, texto
  quebrado em `wraplength=380`), botão "Aplicar marca d'água", label de
  progresso, label de resultado (resumo + lista de sucesso/falha).
- **Nenhum widget tem `sticky="nsew"` nem peso de grid configurado**
  (`grid_columnconfigure`/`grid_rowconfigure`) — ou seja, mesmo que a
  janela seja redimensionada, o frame interno e os labels não vão
  esticar/encolher para acompanhar; hoje isso não importa porque a
  janela é de tamanho fixo.
- As listas de arquivos (seleção e resultado) são exibidas em
  `ttk.Label` com `wraplength`, não em um widget com rolagem (`Listbox`
  ou `Text`) — texto longo hoje só quebra linha, sem scroll.
- `tests/test_gui.py::test_build_window_creates_expected_widgets` verifica
  título e existência dos widgets, mas nada relacionado a
  redimensionamento/`resizable`.
- Não há nenhuma decisão anterior registrada especificamente sobre
  redimensionamento — as specs de GUI anteriores só definiram "janela
  simples, tamanho fixo" (`utilizar_gui`) e depois "a janela cresce" para
  420×420 (`selecionar_múltiplos_arquivos`), sempre como tamanho fixo.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`permitir_redimensionar_janela`). Esta spec assume a interpretação mais
provável — deixar de travar o tamanho da janela e fazer o layout reagir
ao redimensionamento — e lista como "Decisões em aberto" os pontos que
precisam da sua confirmação antes de virar plano.

## Problema

A janela da aplicação tem tamanho fixo (420×420) e não pode ser
redimensionada nem maximizada. Como as listas de arquivos selecionados e
de resultado podem crescer bastante (múltiplos arquivos, nomes longos),
o usuário não tem como aumentar a janela para ver mais conteúdo de uma
vez — só o que já cabe no espaço fixo, com quebra de linha.

## Objetivo

Permitir que o usuário redimensione a janela da aplicação (arrastando as
bordas e/ou maximizando), com o conteúdo se ajustando ao novo tamanho em
vez de ficar preso a um espaço fixo com blocos de texto simplesmente
cortados/apertados.

## Fora de escopo

- Redesenhar o layout visual (cores, ícones, espaçamento) além do
  necessário para suportar redimensionamento.
- Lembrar/persistir o tamanho da janela entre execuções da aplicação.
- Modo tela cheia dedicado (fullscreen) além do comportamento padrão de
  maximizar do sistema operacional.
- Qualquer mudança de comportamento das features já implementadas
  (seleção múltipla, processamento em lote, mensagens de erro).

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/gui.py` (alterado): `root.resizable(True, True)` +
  `root.minsize(420, 420)`; configuração de peso de grid
  (`grid_columnconfigure`/`grid_rowconfigure`) no `root` e no `frame`
  para que os widgets estiquem (`sticky="nsew"`) e acompanhem o novo
  tamanho; `selected_label` e `result_label` são substituídos por um
  widget com rolagem (`Listbox` ou `Text` + `Scrollbar`) para as listas
  de arquivos selecionados e de resultado.
- `tests/test_gui.py` (alterado): pode precisar de um teste adicional
  verificando que a janela é redimensionável (`root.resizable()` ou
  atributos equivalentes).

**Fluxo principal (passo a passo)**:
1. Usuário abre a aplicação (`uv run tatoo`).
2. Usuário arrasta a borda da janela (ou clica em maximizar).
3. A janela muda de tamanho e o conteúdo interno se redistribui para
   ocupar o espaço disponível, sem sobrepor widgets nem cortar texto de
   forma inesperada.
4. O restante do fluxo (selecionar, aplicar, ver resultado) continua
   idêntico ao que já existe hoje.

**Casos de borda relevantes**:
- Usuário encolhe a janela até um tamanho muito pequeno — os widgets não
  podem sobrepor uns aos outros nem ficar inacessíveis (ver decisão sobre
  tamanho mínimo).
- Usuário maximiza a janela com pouquíssimos arquivos selecionados —
  muito espaço vazio sobra; comportamento aceitável ou precisa de algum
  ajuste (ex.: conteúdo alinhado ao topo, não esticado)?

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — só destravar o resize e ajustar o layout para
   acompanhar; sem redesenho visual nem persistência de tamanho entre
   sessões.
2. **Tamanho mínimo**: `root.minsize(420, 420)` — o tamanho atual vira o
   mínimo permitido.
3. **Tamanho máximo**: **sem limite** — o usuário pode maximizar
   livremente, restrito só pelo tamanho da tela.
4. **Widgets de lista**: as labels de texto (`selected_label`,
   `result_label`) são **trocadas por um widget com rolagem**
   (`Listbox`/`Text` com scrollbar) para as listas de arquivos
   selecionados e de resultado, aproveitando melhor o espaço extra ao
   redimensionar.
5. **Comportamento ao esticar**: os widgets **esticam para preencher** o
   espaço disponível (`sticky="nsew"` + peso de grid configurado em
   `root` e no frame).
6. **Estratégia de validação**: **teste automatizado básico** (confirma
   que a janela é criada com `resizable`/`minsize` configurados
   corretamente) **+ validação manual sua**, rodando `uv run tatoo` e
   redimensionando de fato.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Pré-checagem feita durante o planejamento: `root.resizable()` (sem
argumentos) devolve uma tupla `(1, 1)`/`(0, 0)` refletindo o estado atual,
e `root.minsize()` devolve a tupla `(largura, altura)` configurada — ambos
consultáveis programaticamente, então dá para testar essa configuração
sem precisar simular um resize real de janela.

### 1. Destravar redimensionamento e configurar peso de grid
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** troca `root.resizable(False, False)` por
  `root.resizable(True, True)`, adiciona `root.minsize(420, 420)` (sem
  `maxsize`), e configura peso de grid (`grid_columnconfigure`/
  `grid_rowconfigure` com `weight=1`) em `root` e no `frame`, com
  `frame.grid(sticky="nsew")`, para que o conteúdo interno acompanhe o
  redimensionamento.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 2. Trocar labels de lista por widgets com rolagem
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** substitui `selected_label` por um `tk.Listbox` +
  `ttk.Scrollbar` (um item por arquivo selecionado, populado em
  `select_images()`); substitui a parte de lista do `result_label` por
  outro `tk.Listbox` + `ttk.Scrollbar` (um item por resultado: `"OK:
  <nome>"` ou `"Falhou: <nome> (<erro>)"`), mantendo um label separado só
  para a linha de resumo (ex.: "4 de 5 processadas com sucesso");
  `progress_label` continua como está (texto de uma linha, não precisa de
  rolagem). Os dois `Listbox` recebem `sticky="nsew"` e peso de grid para
  esticar com a janela. `_process_files` não muda.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos (testes
  automatizados vêm na tarefa 3).

### 3. Atualizar `tests/test_gui.py`
- **Arquivo(s):** `tests/test_gui.py`
- **O que muda:** ajusta `test_build_window_creates_expected_widgets` para
  os novos atributos expostos (ex.: `root.selected_listbox`,
  `root.result_listbox`, `root.result_summary_label`) no lugar de
  `selected_label`/`result_label`; adiciona um teste novo verificando que
  `build_window()` cria a janela com `root.resizable() == (1, 1)` e
  `root.minsize() == (420, 420)`. Os testes de `_process_files` (sucesso
  total, parcial, vazio) continuam válidos sem alteração, já que a lógica
  de processamento não muda.
- **Validar:** `uv run pytest -v` mostra todos os testes de GUI passando.

### 4. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Pedir para
  você rodar `uv run tatoo` manualmente e confirmar: a janela pode ser
  redimensionada arrastando as bordas e maximizada; abaixo de 420×420 ela
  não encolhe mais; as listas de seleção e resultado esticam e ganham
  rolagem quando há mais itens do que cabe na tela; o restante do fluxo
  (selecionar, aplicar, ver resultado) continua funcionando normalmente.
