# Spec: Preparar ambiente

> Nota: `docs/specs/TEMPLATE.md` está vazio no repositório. Esta spec segue a
> estrutura descrita em `.claude/commands/spec.md` (problema / o que muda /
> fora de escopo / decisões em aberto). Se existir um template desejado,
> favor preenchê-lo e eu re-adapto esta spec a ele.

- **Data:** 2026-08-16
- **Feature:** preparar ambiente
- **Status:** aprovado

> ⚠️ **Desvio do CLAUDE.md**: a seção "Stack" do `CLAUDE.md` define PySimpleGUI
> como biblioteca de GUI. Nesta spec, por decisão explícita do usuário, a GUI
> passa a ser **Tkinter/ttk** (biblioteca padrão do Python, sem custo de
> licença). Recomendo atualizar o `CLAUDE.md` para refletir essa mudança de
> stack quando esta spec for aprovada — não fiz essa edição aqui pois é um
> arquivo de configuração do projeto.

## Contexto (o que encontrei no código)

O diretório do projeto está praticamente vazio:

```
tatoo/
├── .claude/commands/   (implementar.md, plan.md, spec.md)
├── CLAUDE.md
└── docs/specs/TEMPLATE.md  (vazio)
```

- Não há `pyproject.toml`, `requirements.txt`, `.python-version`, código-fonte
  ou testes.
- Não é um repositório git (`git status` não se aplica — não há `.git/`).
- Ferramentas já disponíveis no sistema:
  - `uv 0.11.28` instalado em `~/.local/bin/uv`.
  - `python3 --version` → `3.12.3` (bate com o exigido no CLAUDE.md).
- CLAUDE.md define a stack: Python 3.12.3, PySimpleGUI para GUI, `uv` como
  gerenciador de dependências, pytest para testes, e fluxo spec-driven
  obrigatório.
- Domínio do produto: aplicativo desktop comercial (Windows/Linux) para
  aplicar marcas d'água em imagens PNG/JPG/WEBP. Sem integração com IA no
  produto final.

Como não há nenhum artefato de projeto ainda, "preparar ambiente" é
essencialmente o bootstrap inicial do repositório Python antes de qualquer
feature de negócio ser implementada.

## Problema

Não existe ainda um ambiente de desenvolvimento funcional para o projeto:
sem gerenciamento de dependências, sem estrutura de pastas para código e
testes, sem forma reprodutível de instalar/rodar/testar a aplicação. Isso
bloqueia o início de qualquer implementação (inclusive a primeira feature de
marca d'água).

## O que muda

Bootstrap do ambiente, com todas as decisões abaixo confirmadas pelo usuário:

- **Controle de versão**: rodar `git init` e criar o primeiro commit com o
  esqueleto do projeto.
- **GUI**: usar **Tkinter/ttk** (biblioteca padrão do Python) em vez de
  PySimpleGUI — evita dependência externa e custo de licença comercial. Ver
  aviso de desvio do `CLAUDE.md` no topo desta spec.
- **Gerenciador de dependências**: inicializar o projeto com `uv init`,
  gerando `pyproject.toml`.
- **Versão do Python**: `pyproject.toml` com `requires-python = ">=3.12"`
  (sem limite superior fixo); `.python-version` apontando para 3.12 para
  reprodutibilidade local do `uv`.
- **Layout do projeto**: src-layout — código em `src/tatoo/`.
- **Dependências de desenvolvimento**: `pytest` (testes) e `ruff` (lint +
  format), via `uv add --dev`.
- **Testes iniciais**: um smoke test simples (ex.: `import tatoo`) apenas
  para validar que `uv run pytest` funciona de ponta a ponta.
- Adicionar `.gitignore` apropriado para projeto Python (`.venv/`,
  `__pycache__/`, artefatos de build, etc.).
- Documentar no `README.md` os passos para instalar dependências e rodar a
  aplicação/testes localmente.

## Fora de escopo

- Qualquer lógica de negócio da aplicação (aplicar marca d'água, manipular
  imagens, telas da GUI).
- Empacotamento/distribuição final para Windows/Linux (instalador, PyInstaller
  etc.).
- CI/CD (pipelines de build/teste automatizados em serviço externo).
- Definição de arquitetura interna da aplicação (camadas, módulos de domínio,
  telas Tkinter específicas).
- Atualização do `CLAUDE.md` para refletir a troca de GUI (fica sinalizada
  como recomendação, não executada nesta tarefa).

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário e estão
refletidas na seção "O que muda" acima.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

### 1. Inicializar repositório git
- **Arquivo(s):** `.git/` (novo)
- **O que muda:** cria o repositório git local vazio na raiz do projeto.
- **Validar:** `git status` executa sem erro e mostra a branch inicial sem
  histórico de commits.

### 2. Inicializar projeto uv com layout src (`uv init --package`)
- **Arquivo(s):** `pyproject.toml`, `src/tatoo/__init__.py`,
  `.python-version`, `README.md` (gerados pelo `uv init --package`)
- **O que muda:** cria a estrutura de pacote Python instalável
  `src/tatoo/`, já no formato src-layout definido na spec, com
  `pyproject.toml` e `uv.lock` iniciais.
- **Validar:** `uv run python -c "import tatoo"` executa sem erro.

### 3. Ajustar versão do Python exigida
- **Arquivo(s):** `pyproject.toml`, `.python-version`
- **O que muda:** garante `requires-python = ">=3.12"` no `pyproject.toml`
  (sem limite superior) e `.python-version` apontando para 3.12 (a versão
  instalada localmente, 3.12.3, deve satisfazer o pin).
- **Validar:** `uv sync` roda sem erro e resolve o ambiente usando
  Python 3.12.3 (`uv run python --version`).

### 4. Revisar/completar `.gitignore`
- **Arquivo(s):** `.gitignore`
- **O que muda:** garante que `.venv/`, `__pycache__/`, `dist/`,
  `.pytest_cache/`, `.ruff_cache/` e `uv.lock`-relacionados (se aplicável)
  estejam cobertos, complementando o que `uv init` já gera.
- **Validar:** após `uv sync` e `uv run pytest`, `git status` não lista
  `.venv/`, `__pycache__/` nem diretórios de cache.

### 5. Adicionar `pytest` como dependência de desenvolvimento
- **Arquivo(s):** `pyproject.toml`, `uv.lock`
- **O que muda:** roda `uv add --dev pytest`, registrando pytest como
  dependência de dev do projeto.
- **Validar:** `uv run pytest --version` executa sem erro.

### 6. Criar smoke test
- **Arquivo(s):** `tests/test_smoke.py` (novo)
- **O que muda:** adiciona um teste trivial que importa o pacote `tatoo`
  e confirma que o ambiente de testes está funcional.
- **Validar:** `uv run pytest` reporta 1 teste passando.

### 7. Adicionar `ruff` (lint + format) como dependência de desenvolvimento
- **Arquivo(s):** `pyproject.toml` (incluindo seção `[tool.ruff]` mínima),
  `uv.lock`
- **O que muda:** roda `uv add --dev ruff` e define uma configuração
  mínima de lint/format para o projeto.
- **Validar:** `uv run ruff check .` e `uv run ruff format --check .`
  executam sem apontar erros.

### 8. Validar disponibilidade do Tkinter no ambiente
- **Arquivo(s):** nenhum arquivo de código; possível nota em `README.md`
  sobre o pacote de sistema `python3-tk` no Linux.
- **O que muda:** confirma que o Tkinter/ttk (escolhido como GUI na spec)
  está disponível no ambiente Python local antes de depender dele em
  features futuras.
- **Validar:** `uv run python -c "import tkinter; print(tkinter.TkVersion)"`
  executa sem erro. Se falhar no Linux, documentar no README a instalação
  do pacote de sistema `python3-tk` (fora do escopo de dependências uv).

### 9. Documentar setup no `README.md`
- **Arquivo(s):** `README.md`
- **O que muda:** adiciona instruções de instalação/execução: `uv sync`,
  `uv run pytest`, `uv run ruff check .`, e a nota sobre `python3-tk` no
  Linux quando aplicável.
- **Validar:** revisão manual do conteúdo do README.

> O primeiro commit do projeto será feito manualmente pelo usuário — não faz
> parte deste plano de implementação.
