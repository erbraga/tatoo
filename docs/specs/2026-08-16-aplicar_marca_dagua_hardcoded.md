# Spec: Aplicar marca d'água (hardcoded)

> Nota: `docs/specs/TEMPLATE.md` está vazio no repositório. Esta spec segue a
> mesma estrutura usada em `docs/specs/2026-08-16-preparar-ambiente.md`
> (problema / o que muda / fora de escopo / decisões em aberto).

- **Data:** 2026-08-16
- **Feature:** aplicar_marca_dagua_hardcoded
- **Status:** aprovado

> 📁 **Nota sobre `img/`**: o `.gitignore` já foi atualizado para ignorar
> `img/` — é lá que o logotipo (`img/logo.png`) e as imagens de teste vão
> ficar, fora do controle de versão. Isso significa que os testes
> automatizados desta feature dependem de arquivos que não estão no
> repositório: se alguém clonar o projeto sem a pasta `img/` preenchida, os
> testes vão falhar. Aceitável para esta etapa exploratória, mas vale
> revisitar antes de a suíte de testes virar parte de um pipeline
> automatizado (CI), já sinalizado como fora do escopo do bootstrap.

## Contexto (o que encontrei no código)

Estado atual do projeto (pós-bootstrap do ambiente, ver
[2026-08-16-preparar-ambiente.md](2026-08-16-preparar-ambiente.md)):

```
tatoo/
├── src/tatoo/__init__.py   → só tem main() com "Hello from tatoo!"
├── tests/test_smoke.py     → smoke test trivial (import tatoo)
├── pyproject.toml          → sem nenhuma dependência de runtime ainda
└── README.md
```

- `pyproject.toml` tem `dependencies = []` — nenhuma biblioteca de
  manipulação de imagem (ex.: Pillow) foi adicionada até agora.
- Não existe nenhum módulo, função ou teste relacionado a imagens ou marca
  d'água no repositório.
- Não há nenhuma imagem de exemplo/fixture no projeto (png, jpg ou webp).
- `CLAUDE.md` confirma o domínio: aplicação de marcas d'água em imagens
  PNG/JPG/WEBP, GUI em Tkinter/ttk, mas a spec de GUI ainda não existe —
  esta feature, pelo nome ("hardcoded"), parece ser a primeira validação da
  lógica central de aplicar marca d'água, sem GUI e sem parâmetros
  configuráveis pelo usuário ainda.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`aplicar_marca_dagua_hardcoded`). Por isso esta spec assume a interpretação
mais provável — provar a lógica de negócio central com valores fixos no
código — e lista como "Decisões em aberto" tudo que precisa da sua
confirmação antes de virar plano.

## Problema

O projeto ainda não tem nenhuma lógica de domínio implementada — apenas o
esqueleto do ambiente. Antes de construir a GUI (Tkinter/ttk) ou qualquer
fluxo de configuração pelo usuário, é preciso validar que é possível abrir
uma imagem, aplicar uma marca d'água nela e salvar o resultado, usando
parâmetros fixos ("hardcoded") no próprio código — sem input do usuário.

## O que muda

Bootstrap da lógica de marca d'água, com todas as decisões abaixo
confirmadas pelo usuário:

- **Biblioteca de imagem**: adicionar **Pillow** como dependência de
  runtime (`uv add pillow`), para abrir, manipular e salvar png/jpg/webp.
- **Tipo de marca d'água**: **imagem/logotipo** sobreposto (não é texto).
  O arquivo do logotipo é `img/logo.png`, fornecido manualmente pelo
  usuário (fora do git — ver nota sobre `img/` no topo desta spec).
- **Posição**: **centro** da imagem.
- **Opacidade**: **30%** (marca discreta).
- **Formato de saída**: **igual ao formato de entrada** (PNG entra como
  PNG, JPG como JPG, WEBP como WEBP).
- **Onde salvar**: **sufixo no nome do arquivo** (ex.: `teste.png` →
  `teste_marcada.png`), no mesmo diretório da entrada. Não sobrescreve o
  original.
- **Escopo de formatos**: cobrir os **3 formatos do domínio** (png, jpg,
  webp) já nesta primeira versão.
- **Imagens de teste**: também fornecidas manualmente pelo usuário em
  `img/` (ex.: `img/teste.png`, `img/teste.jpg`, `img/teste.webp` — nomes
  exatos a confirmar na fase de plano, junto com o usuário).
- **Forma de execução**: só cobertura por **testes automatizados
  (pytest)** nesta etapa — sem entrypoint manual de linha de comando
  (a GUI virá em uma feature futura).
- Criar um módulo dentro de `src/tatoo/` (ex.: `watermark.py`) com uma
  função que recebe o caminho de uma imagem de entrada, aplica a marca
  d'água (`img/logo.png`, centralizada, 30% de opacidade) e salva o
  resultado com sufixo no nome, preservando o formato original.
- Adicionar teste(s) automatizados que validem, para cada um dos 3
  formatos, que a função roda sem erro e produz um arquivo de saída
  distinto do original (ex.: dimensões preservadas, conteúdo alterado).

## Fora de escopo

- Interface gráfica (Tkinter/ttk) para selecionar imagem, texto ou opções
  de marca d'água.
- Qualquer configuração pelo usuário (arquivo de config, argumentos de
  linha de comando, GUI).
- Processamento em lote (batch) de múltiplas imagens.
- Empacotamento/distribuição da aplicação.
- Suporte a formatos de imagem além dos já definidos no domínio do produto
  (png, jpg, webp).

## Decisões em aberto

Nenhuma pendente. Na fase de plano, encontramos `img/` já com 4 fotos reais
em `.webp` (sem `.png`/`.jpg`) e sem `img/logo.png`. Decisões adicionais
resolvidas com o usuário nesse momento:

- **Logo ausente**: gero um placeholder simples (retângulo + texto) via
  Pillow em `img/logo.png`, até o logotipo real ser fornecido.
- **Imagens de teste**: uso `img/20260226_114501.webp` (arquivo real) para
  o caso webp; para png e jpg, os testes geram imagens sintéticas pequenas
  via Pillow em tempo de execução (não versionadas em `img/`).

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

### 1. Adicionar Pillow como dependência de runtime
- **Arquivo(s):** `pyproject.toml`, `uv.lock`
- **O que muda:** roda `uv add pillow`, registrando Pillow como
  dependência de runtime do projeto (necessária para png/jpg/webp).
- **Validar:** `uv run python -c "import PIL; print(PIL.__version__)"`
  executa sem erro.

### 2. Gerar logotipo placeholder em `img/logo.png`
- **Arquivo(s):** `img/logo.png` (novo, fora do git — `img/` já está no
  `.gitignore`)
- **O que muda:** cria um logotipo simples (ex.: retângulo com o texto
  "TATOO") via Pillow, com canal alfa, usado como marca d'água até o
  logotipo comercial real ser fornecido.
- **Validar:** `uv run python -c "from PIL import Image; im = Image.open('img/logo.png'); print(im.size, im.mode)"`
  executa sem erro e mostra modo `RGBA`.

### 3. Criar módulo `src/tatoo/watermark.py`
- **Arquivo(s):** `src/tatoo/watermark.py` (novo)
- **O que muda:** implementa a função central que recebe o caminho de uma
  imagem de entrada, abre com Pillow, sobrepõe `img/logo.png` centralizado
  com 30% de opacidade, e salva o resultado no mesmo diretório da entrada,
  com sufixo `_marcada` no nome e preservando o formato original
  (png/jpg/webp).
- **Validar:** `uv run ruff check src/tatoo/watermark.py` sem apontamentos
  (ainda sem teste automatizado nesta tarefa — vem nas próximas).

### 4. Criar fixtures de teste em `tests/conftest.py`
- **Arquivo(s):** `tests/conftest.py` (novo)
- **O que muda:** adiciona fixtures pytest que (a) geram imagens PNG e JPG
  pequenas via Pillow em um diretório temporário (`tmp_path`), e (b) copiam
  `img/20260226_114501.webp` para um diretório temporário antes de cada
  teste, evitando gravar arquivos de saída na pasta real `img/` do
  usuário.
- **Validar:** `uv run pytest --collect-only` executa sem erro de coleta.

### 5. Escrever testes da função de marca d'água para os 3 formatos
- **Arquivo(s):** `tests/test_watermark.py` (novo)
- **O que muda:** testa, para PNG, JPG e WEBP, que a função roda sem erro,
  gera um arquivo de saída com o sufixo `_marcada` esperado, preserva as
  dimensões da imagem original e produz um conteúdo diferente do arquivo
  de entrada.
- **Validar:** `uv run pytest -v` reporta os novos testes passando.

### 6. Rodar suíte completa e lint
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (todos os testes passando, incluindo o
  smoke test existente) e `uv run ruff check .` / `uv run ruff format --check .`
  sem apontamentos.
