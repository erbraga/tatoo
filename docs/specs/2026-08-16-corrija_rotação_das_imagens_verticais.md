# Corrija Rotação das Imagens Verticais — Spec

**Criado em:** 2026-08-16
**Status:** aprovado

## Contexto (o que encontrei no código)

- `img/` foi **trocado**: as fotos `.webp` antigas (sem nenhum metadado)
  saíram, e agora há **11 fotos `.jpg` reais** (`20260219_*.jpg`,
  4000×1848, ~1–2,5 MB cada) — provavelmente as "fotos originais" citadas
  na conversa anterior. Testei o EXIF de todas:

  ```
  20260219_105834.jpg  orientation tag: 1  (normal)
  20260219_110050.jpg  orientation tag: 1
  20260219_110115.jpg  orientation tag: 1
  20260219_110121.jpg  orientation tag: 6  (precisa rotacionar)
  20260219_110131.jpg  orientation tag: 1
  20260219_110735.jpg  orientation tag: 6
  20260219_111511.jpg  orientation tag: 1
  20260219_111516.jpg  orientation tag: 6
  20260219_112959.jpg  orientation tag: 6
  20260219_113011.jpg  orientation tag: 1
  20260219_113141.jpg  orientation tag: 6
  ```

  Diferente das fotos `.webp` antigas (nenhuma tinha EXIF), **essas JPGs
  têm EXIF de orientação de verdade** — 5 das 11 precisam de rotação
  (tag `6` = fotos tiradas na vertical, salvas com os pixels na
  orientação nativa do sensor).

- **Histórico relevante**: existe uma spec anterior,
  [2026-08-16-ajustar_orientação.md](2026-08-16-ajustar_orientação.md),
  que tentou resolver exatamente este problema (correção de orientação
  via EXIF, usando `PIL.ImageOps.exif_transpose()`). Ela foi **implementada
  e depois desfeita a pedido do usuário**, porque as fotos de teste
  disponíveis na época (`.webp`) não tinham nenhum EXIF — a correção
  virava um no-op e "não funcionava" nos dados de teste, mesmo estando
  tecnicamente correta. Agora, com fotos `.jpg` reais com EXIF válido em
  `img/`, essa mesma abordagem técnica é finalmente testável de forma
  significativa.

- `src/tatoo/watermark.py::apply_watermark()` (estado atual, já com a
  mudança da spec `compactar_imagem_e_converter_para_webp`, ainda não
  commitada) abre a imagem com `Image.open(image_path)` **sem nenhum
  tratamento de EXIF**, compõe o logo, e salva sempre como WEBP. Como o
  código não lê mais `base.format` (o formato de saída agora é sempre
  `WEBP`, fixo), a ressalva da spec anterior sobre "`exif_transpose()` não
  preservar `.format`" **deixou de ser relevante** — simplifica a
  implementação desta vez.
- `src/tatoo/gui.py::_make_thumbnail_image()` também abre a imagem
  diretamente, sem tratamento de EXIF — mesmo problema na miniatura da
  lista de seleção.
- `tests/conftest.py` tem fixtures sintéticas (`png_image`, `jpg_image`,
  `webp_image`, `broken_image`), nenhuma com EXIF de orientação. Como
  agora há fotos reais com `orientation=6` em `img/`, dá para criar uma
  fixture que **copia um arquivo real** (mesmo padrão já usado por
  `webp_image`, que copia `img/20260226_114501.webp`) em vez de gerar
  uma imagem sintética com EXIF forjado.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`corrija_rotação_das_imagens_verticais`). Dado o histórico e a evidência
no código, esta spec assume a mesma interpretação da tentativa anterior —
corrigir a orientação da imagem com base no EXIF, antes de aplicar a
marca d'água e ao gerar thumbnails — e lista como "Decisões em aberto" os
pontos que precisam da sua confirmação.

## Problema

Fotos tiradas na vertical (celular girado) ficam com os pixels salvos na
orientação "deitada" do sensor, e a orientação real fica só no metadado
EXIF. Como `apply_watermark()` e a geração de thumbnails não leem esse
metadado, o resultado final (e a pré-visualização) aparecem rotacionados
incorretamente para essas fotos — confirmado agora com 5 das 11 fotos
reais em `img/` (`orientation=6`).

## Objetivo

Fazer com que `apply_watermark()` e a geração de thumbnails apliquem a
rotação indicada pelo EXIF antes de processar a imagem, para que fotos
verticais apareçam corretamente orientadas tanto na miniatura de seleção
quanto no arquivo final gerado.

## Fora de escopo

- Qualquer outra correção de metadado EXIF além da orientação.
- Permitir que o usuário rotacione manualmente uma imagem pela GUI.
- Corrigir retroativamente arquivos `*_marcada.*` já gerados em execuções
  anteriores.
- Detecção de orientação por conteúdo/heurística visual para imagens sem
  EXIF (ex.: as antigas `.webp` sem metadado) — sem informação alguma,
  não há como corrigir automaticamente; isso ficaria para uma feature
  separada, se necessário.
- Mudar os parâmetros hardcoded de `apply_watermark` (logo, posição,
  opacidade, compressão WEBP) além do necessário para a correção de
  orientação.

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/watermark.py` (alterado): `apply_watermark()` aplica
  `ImageOps.exif_transpose()` na imagem aberta, antes de compor o logo,
  para normalizar a orientação segundo o EXIF.
- `src/tatoo/gui.py` (alterado): `_make_thumbnail_image()` aplica a mesma
  normalização antes de gerar a miniatura.
- `tests/conftest.py` (alterado): nova fixture que copia uma foto real
  com `orientation=6` de `img/` (ex.: `20260219_110121.jpg`) para
  `tmp_path`, seguindo o padrão já usado por `webp_image`.

**Fluxo principal (passo a passo)**:
1. Usuário seleciona uma foto vertical com EXIF de orientação (ex.:
   `20260219_110121.jpg`, tag `6`).
2. A miniatura na lista de seleção aparece em pé (orientação corrigida).
3. Ao aplicar a marca d'água, o arquivo `*_marcada.webp` gerado também
   aparece em pé, com o logo centralizado corretamente.

**Casos de borda relevantes**:
- Foto com `orientation=1` (normal) — nenhuma rotação aplicada,
  comportamento idêntico ao atual (6 das 11 fotos reais são desse tipo).
- Foto sem EXIF nenhum (ex.: as antigas `.webp` sem metadado, se
  reaparecerem) — `exif_transpose()` não faz nada, imagem processada como
  está hoje (sem correção possível, por falta de informação).
- Dimensões trocadas após a correção (foto vertical que "deitada" nos
  pixels crus passa a ficar "em pé") — o arquivo final tem largura/altura
  invertidas em relação ao arquivo de entrada.

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — corrigir a orientação da imagem com base no
   EXIF (`ImageOps.exif_transpose()`), aplicado tanto em
   `apply_watermark()` quanto na geração de thumbnails.
2. **Fixture de teste**: usar uma **foto real de `img/`** com
   `orientation=6` (ex.: `20260219_110121.jpg`), copiada para `tmp_path`
   nos testes — mesmo padrão já usado por `webp_image`.
3. **Dimensões após correção**: **aceitável** que largura/altura do
   arquivo gerado mudem em relação ao arquivo de entrada quando a
   correção rotaciona a imagem 90°/270°.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Pré-checagem feita durante o planejamento: `img/20260219_110121.jpg` tem
`orientation=6`, tamanho bruto `(4000, 1848)`; depois de
`ImageOps.exif_transpose()`, o tamanho corrigido é `(1848, 4000)` — a
inversão de dimensões esperada, confirmada com o arquivo real que será
usado como fixture.

### 1. Corrigir orientação em `apply_watermark()`
- **Arquivo(s):** `src/tatoo/watermark.py`
- **O que muda:** logo após `base = Image.open(image_path)`, aplica
  `base = ImageOps.exif_transpose(base)` para normalizar a orientação
  antes de `base.convert("RGBA")` e do cálculo de posição do logo
  (`canvas.width`/`canvas.height` já refletem as dimensões corrigidas
  automaticamente). Diferente da tentativa anterior, não é preciso
  capturar `base.format` antes — o código atual já não depende mais dele
  (saída sempre em WEBP).
- **Validar:** `uv run ruff check src/tatoo/watermark.py` e
  `uv run ruff format --check src/tatoo/watermark.py` sem apontamentos
  (teste funcional na tarefa 3).

### 2. Corrigir orientação na geração de thumbnails
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** em `_make_thumbnail_image()`, aplica
  `img = ImageOps.exif_transpose(img)` logo após `Image.open(path)` (e
  antes de `img.convert("RGB")` / `img.thumbnail(size)`), para que a
  miniatura reflita a orientação corrigida.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 3. Fixture de foto real com orientação vertical
- **Arquivo(s):** `tests/conftest.py`
- **O que muda:** adiciona uma fixture (ex.: `rotated_jpg_image`) que
  copia `img/20260219_110121.jpg` (`orientation=6`) para `tmp_path`,
  seguindo o mesmo padrão de `webp_image` (que copia
  `img/20260226_114501.webp` — ajustar a constante de origem, já que
  aquele arquivo `.webp` específico não existe mais em `img/`).
- **Validar:** `uv run pytest --collect-only` executa sem erro de coleta.

### 4. Testes de correção de orientação
- **Arquivo(s):** `tests/test_watermark.py`, `tests/test_gui.py`
- **O que muda:**
  - em `test_watermark.py`, novo teste que aplica `apply_watermark()` em
    `rotated_jpg_image` e confirma que as dimensões do arquivo `.webp`
    gerado são `(1848, 4000)` — a orientação corrigida, invertida em
    relação ao bruto `(4000, 1848)`;
  - em `test_gui.py`, novo teste que confirma que
    `_make_thumbnail_image(rotated_jpg_image)` produz uma miniatura com
    altura maior que largura (reflete a imagem "em pé" após a correção).
- **Validar:** `uv run pytest -v` mostra os novos testes passando.

### 5. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto, incluindo os casos de borda da spec (fotos com
  `orientation=1`, sem alteração de comportamento).
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Pedir para
  você rodar `uv run tatoo`, selecionar uma das fotos verticais reais
  (ex.: `20260219_110121.jpg` ou `20260219_110735.jpg`) e confirmar que
  ela aparece em pé tanto na miniatura da lista de seleção quanto no
  arquivo `*_marcada.webp` gerado.
