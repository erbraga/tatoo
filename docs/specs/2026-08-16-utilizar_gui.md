# Utilizar GUI — Spec

**Criado em:** 2026-08-16
**Status:** aprovado

## Contexto (o que encontrei no código)

Estado atual do projeto (após
[2026-08-16-preparar-ambiente.md](2026-08-16-preparar-ambiente.md) e
[2026-08-16-aplicar_marca_dagua_hardcoded.md](2026-08-16-aplicar_marca_dagua_hardcoded.md)):

```
tatoo/
├── src/tatoo/
│   ├── __init__.py    → main() só imprime "Hello from tatoo!"
│   └── watermark.py   → apply_watermark(image_path) já funcional
├── tests/
│   ├── conftest.py    → fixtures de imagem (png/jpg sintéticas, webp real)
│   ├── test_smoke.py
│   └── test_watermark.py
├── img/                → logo.png, fotos reais .webp (fora do git)
└── pyproject.toml      → dependencies: pillow; [project.scripts] tatoo = "tatoo:main"
```

- `src/tatoo/watermark.py` já implementa `apply_watermark(image_path)`:
  abre a imagem com Pillow, sobrepõe `img/logo.png` **centralizado** com
  **30% de opacidade** (valores fixos no código — "hardcoded"), salva o
  resultado no mesmo diretório com sufixo `_marcada`, preservando o
  formato original (png/jpg/webp). Não há nenhum parâmetro configurável
  em tempo de execução.
- Não existe nenhum código de GUI no projeto ainda — nenhuma referência a
  `tkinter` em `src/`.
- `pyproject.toml` já declara `[project.scripts] tatoo = "tatoo:main"`,
  mas `main()` apenas imprime uma mensagem de exemplo — é o ponto de
  entrada natural para a aplicação, hoje sem uso real.
- `README.md` já documenta Tkinter/ttk como a biblioteca de GUI do
  projeto e inclui uma nota sobre o pacote de sistema `python3-tk` no
  Linux, mas isso ainda não foi exercitado por nenhum código.
- A spec anterior (`aplicar_marca_dagua_hardcoded`) marcou GUI e qualquer
  configuração pelo usuário como **fora de escopo**, adiando
  explicitamente para "uma feature futura" — que é esta.
- Não há nenhuma descrição adicional da feature além do nome do argumento
  (`utilizar_gui`). Por isso esta spec assume a interpretação mais
  provável — dar à função `apply_watermark` já existente uma primeira
  interface gráfica mínima — e lista como "Decisões em aberto" tudo que
  precisa da sua confirmação antes de virar plano.

## Problema

A lógica de aplicar marca d'água já funciona (`apply_watermark`), mas só
pode ser usada programaticamente (via testes ou REPL) — não há forma do
usuário final (que não escreve código) selecionar uma imagem e gerar o
resultado. Não existe nenhuma interface gráfica no projeto ainda, apesar
de Tkinter/ttk já estar definido como a biblioteca de GUI em `CLAUDE.md`
e no `README.md`.

## Objetivo

Dar à função `apply_watermark` já existente uma primeira interface
gráfica (Tkinter/ttk) que permita ao usuário selecionar uma imagem e
gerar a versão com marca d'água, sem precisar rodar código ou testes
manualmente.

## Fora de escopo

- Alterar os parâmetros hardcoded de `apply_watermark` (logo, posição,
  opacidade) — a GUI apenas aciona a função já existente, sem expor
  controles para esses valores nesta primeira versão.
- Processamento em lote (seleção de múltiplos arquivos de uma vez).
- Empacotamento/distribuição da aplicação (instalador Windows/Linux,
  ícone, etc.).
- Persistência de preferências do usuário (última pasta usada,
  configurações salvas em disco).
- Testes automatizados end-to-end da GUI (ex.: simulação de cliques) —
  ver decisão em aberto sobre estratégia de validação.

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados** (este projeto não tem models de banco de
dados — a unidade equivalente aqui são os módulos Python):
- `src/tatoo/gui.py` (novo): janela principal Tkinter/ttk.
- `src/tatoo/__init__.py` (alterado): `main()` passa a abrir a GUI em vez
  de imprimir a mensagem de exemplo, mantendo `uv run tatoo` como ponto
  de entrada.
- `src/tatoo/watermark.py`: não é alterado — a GUI só consome
  `apply_watermark()` como já existe hoje.

**Fluxo principal (passo a passo)**:
1. Usuário roda `uv run tatoo` (ou `uv run python -m tatoo`) e a janela
   abre.
2. Usuário clica em um botão "Selecionar imagem", que abre um diálogo
   nativo (`tkinter.filedialog.askopenfilename`) filtrado para
   `.png/.jpg/.jpeg/.webp`.
3. Usuário clica em "Aplicar marca d'água", que chama
   `apply_watermark()` sobre o arquivo selecionado.
4. A GUI mostra o resultado: caminho do arquivo gerado (`*_marcada.*`)
   como texto na própria janela, em caso de sucesso.
5. A janela continua aberta, permitindo repetir o processo com outra
   imagem sem reabrir a aplicação.

**Casos de borda relevantes**:
- Usuário cancela o diálogo de seleção de arquivo (nenhum arquivo
  escolhido).
- Usuário tenta aplicar marca d'água sem ter selecionado nenhum arquivo
  antes.
- `apply_watermark()` lança exceção (ex.: arquivo de imagem corrompido,
  `img/logo.png` ausente) — a GUI não pode quebrar com traceback cru.

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo funcional mínimo**: só selecionar arquivo, rodar
   `apply_watermark`, mostrar caminho do resultado ou erro. **Sem**
   preview visual (miniatura) nesta primeira versão.
2. **Seleção de arquivo**: `tkinter.filedialog.askopenfilename` restrito
   às extensões `.png/.jpg/.jpeg/.webp` — confirmado.
3. **Feedback de sucesso**: **texto na própria janela** (label), sem
   popup adicional.
4. **Tratamento de erro**: `messagebox.showerror` com a mensagem de erro,
   sem quebrar a aplicação com traceback no terminal — confirmado.
5. **Fluxo repetido**: a janela **continua aberta** após gerar uma
   imagem, permitindo processar outra sem reabrir o app.
6. **Ponto de entrada**: `main()` em `src/tatoo/__init__.py` passa a
   abrir a GUI diretamente (via `uv run tatoo`), substituindo o "Hello
   from tatoo!" atual — confirmado.
7. **Layout/tamanho da janela**: a critério da implementação — janela
   simples, título "tatoo", tamanho fixo pequeno, sem redimensionamento.
8. **Estratégia de validação/teste**: **teste básico automatizado** —
   um teste tenta criar a janela sem `mainloop()` só para garantir que a
   inicialização não quebra (sem simular cliques/interação).

## Critérios de aceite

- `uv run tatoo` abre uma janela Tkinter/ttk (em vez de imprimir texto no
  terminal).
- É possível selecionar um arquivo `.png`, `.jpg` ou `.webp` via diálogo
  nativo.
- Ao clicar em aplicar marca d'água, o arquivo `*_marcada.*` é gerado no
  mesmo diretório do arquivo de entrada (mesmo comportamento de
  `apply_watermark` hoje).
- A GUI exibe o caminho do arquivo gerado em caso de sucesso.
- Erros de `apply_watermark` (ex.: `img/logo.png` ausente) são
  capturados e exibidos na interface, sem o programa fechar com
  traceback no terminal.
- `uv run pytest` e `uv run ruff check .` continuam passando após a
  mudança.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Pré-checagem feita durante o planejamento: `DISPLAY=:0` está definido e
`tkinter.Tk()` consegue ser instanciado neste ambiente, então um teste
automatizado que cria a janela (sem `mainloop()`) é viável — confirma a
decisão #8 da spec.

### 1. Criar `src/tatoo/gui.py` com a janela principal
- **Arquivo(s):** `src/tatoo/gui.py` (novo)
- **O que muda:** implementa a janela Tkinter/ttk (título "tatoo",
  tamanho fixo pequeno) com: botão "Selecionar imagem" (abre
  `filedialog.askopenfilename` filtrado para `.png/.jpg/.jpeg/.webp`),
  label mostrando o caminho selecionado, botão "Aplicar marca d'água"
  (chama `apply_watermark()` sobre o arquivo selecionado e atualiza um
  label com o caminho do resultado), e `messagebox.showerror` para
  qualquer exceção de `apply_watermark()` ou tentativa de aplicar sem
  arquivo selecionado. A construção da janela fica em uma função own
  (ex.: `build_window()`) que **não** chama `mainloop()` — isso permite
  testar a criação da janela sem bloquear (ver tarefa 3).
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 2. Ligar `main()` à GUI em `src/tatoo/__init__.py`
- **Arquivo(s):** `src/tatoo/__init__.py`
- **O que muda:** `main()` passa a chamar `build_window().mainloop()` (ou
  uma função equivalente de `tatoo.gui`), substituindo o
  `print("Hello from tatoo!")` atual. `uv run tatoo` passa a abrir a
  aplicação gráfica.
- **Validar:** `uv run ruff check src/tatoo/__init__.py` sem
  apontamentos. Abrir a janela de fato (`uv run tatoo`) só é validado
  manualmente por você — rodar via terminal automatizado abriria um
  `mainloop()` bloqueante; a tarefa 3 cobre a criação da janela sem
  travar.

### 3. Escrever teste básico da GUI em `tests/test_gui.py`
- **Arquivo(s):** `tests/test_gui.py` (novo)
- **O que muda:** testa que `build_window()` roda sem erro (sem chamar
  `mainloop()`), que os widgets esperados existem (botão de seleção,
  botão de aplicar, labels), e destrói a janela ao final do teste. Não
  simula cliques nem interação — apenas garante que a inicialização não
  quebra, conforme decisão #8 da spec.
- **Validar:** `uv run pytest -v` mostra o novo teste passando.

### 4. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto e fecha os critérios de aceite da spec.
- **Validar:** `uv run pytest` (todos os testes passando, incluindo o
  novo `test_gui.py`), `uv run ruff check .` e
  `uv run ruff format --check .` sem apontamentos. Além disso, pedir para
  você rodar `uv run tatoo` manualmente e confirmar que: a janela abre,
  é possível selecionar uma imagem real de `img/`, aplicar a marca
  d'água gera o arquivo `*_marcada.*` esperado, e o fluxo pode ser
  repetido sem fechar a janela.
