# Ajustar Orientação — Spec

**Criado em:** 2026-08-16
**Status:** decisões resolvidas — aguardando aprovação final para virar plano

## Contexto (o que encontrei no código)

- `src/tatoo/watermark.py::apply_watermark()` abre a imagem com
  `Image.open(image_path)` **sem nenhum tratamento de orientação EXIF**.
  Câmeras de celular frequentemente gravam a foto com os pixels na
  orientação "nativa" do sensor e guardam a rotação real como metadado
  EXIF (`Orientation`, tag 274) — sem aplicar essa rotação, o Pillow
  processa a imagem "deitada" mesmo que ela apareça em pé em qualquer
  visualizador que respeite o EXIF.
- O `canvas.save(output_path, format=base_format)` atual **não recebe
  `exif=...`**, então qualquer metadado EXIF do arquivo original —
  incluindo a tag de orientação — **se perde** no arquivo gerado
  (`*_marcada.*`). Se o original dependia do EXIF para aparecer em pé, o
  resultado gerado por `apply_watermark` pode aparecer "deitado" em
  visualizadores que respeitam EXIF, mesmo que o original parecesse
  correto.
- `src/tatoo/gui.py::_make_thumbnail_image()` também abre a imagem
  diretamente com `Image.open(path)` e gera a miniatura sem considerar
  orientação EXIF — sofre do mesmo problema ao exibir a lista de
  seleção.
- Testei as 4 fotos reais em `img/` (`20260226_*.webp`, 4000×1848): **nenhuma
  delas tem tag de orientação EXIF** (`exif.get(274)` retornou `None` para
  todas). Ou seja, o bug de orientação não aparece com os arquivos de
  teste atuais do projeto — ele afeta especificamente fotos (tipicamente
  `.jpg` de celular) que carregam a tag EXIF `Orientation` diferente de
  "normal".
- Não existe hoje nenhum tratamento de EXIF em nenhuma parte do código
  (`watermark.py` ou `gui.py`), nem nenhuma fixture de teste com EXIF de
  orientação em `tests/conftest.py`.
- O logo (`img/logo.png`) é 400×160 (paisagem/retangular) — relevante
  porque, se a orientação da imagem de entrada for corrigida e as
  dimensões largura/altura se inverterem (foto em pé vs. deitada), a
  centralização do logo continua funcionando automaticamente (usa
  `canvas.width`/`canvas.height` após abrir a imagem), desde que a
  correção de orientação aconteça **antes** de calcular a posição.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`ajustar_orientação`). Pela evidência no código (nenhum tratamento de
EXIF em nenhum lugar, e esse é um problema real e comum em fotos de
celular), esta spec assume que a feature é **corrigir a orientação da
imagem com base no metadado EXIF antes de aplicar a marca d'água (e ao
gerar thumbnails)**, e lista como "Decisões em aberto" os pontos que
precisam da sua confirmação — inclusive a confirmação do próprio escopo,
já que o nome da feature é genérico o suficiente para, em tese, significar
outra coisa.

## Problema

Fotos de celular frequentemente guardam a orientação correta como
metadado EXIF em vez de rotacionar os pixels. Como `apply_watermark()` e
a geração de thumbnails não consideram esse metadado, uma foto tirada em
pé pode ser processada como se estivesse deitada — e o EXIF de
orientação do arquivo original nem é preservado no resultado gerado — o
que pode fazer a imagem final (ou a miniatura) aparecer com a orientação
errada em relação ao que o usuário via na câmera/galeria.

## Objetivo

Fazer com que `apply_watermark()` (e a geração de thumbnails) considerem
a orientação real da imagem (segundo o EXIF, quando presente), para que o
resultado final apareça na mesma orientação em que a imagem original era
exibida, em qualquer visualizador.

## Fora de escopo

- Qualquer outra correção de metadado EXIF além da orientação (ex.: data,
  geolocalização, informações de câmera).
- Permitir que o usuário rotacione manualmente uma imagem pela GUI.
- Corrigir retroativamente os arquivos `*_marcada.*` já gerados em `img/`
  em execuções anteriores.
- Mudar os parâmetros hardcoded de `apply_watermark` (logo, posição,
  opacidade) além do necessário para a correção de orientação.

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/watermark.py` (alterado): `apply_watermark()` passa a
  normalizar a orientação da imagem de entrada (ex.: via
  `PIL.ImageOps.exif_transpose()`) antes de calcular a posição do logo e
  compor a marca d'água.
- `src/tatoo/gui.py` (alterado): `_make_thumbnail_image()` passa a
  aplicar a mesma normalização antes de gerar a miniatura, para a
  pré-visualização bater com a orientação real da imagem.
- `tests/conftest.py` (alterado): precisa de uma fixture nova com uma
  imagem que tenha uma tag EXIF de orientação diferente de "normal", já
  que nenhuma fixture ou imagem real do projeto tem essa tag hoje.

**Fluxo principal (passo a passo)**:
1. Usuário seleciona uma foto tirada com o celular na vertical, que tem
   uma tag EXIF de orientação (ex.: `Orientation = 6`).
2. Ao gerar a miniatura na lista de seleção, a imagem aparece em pé
   (orientação correta), não deitada.
3. Ao aplicar a marca d'água, o resultado gerado também aparece em pé, com
   o logo centralizado corretamente na imagem já orientada.

**Casos de borda relevantes**:
- Imagem sem tag EXIF de orientação (caso de todas as imagens de teste
  atuais do projeto) — comportamento deve continuar idêntico ao de hoje.
- Imagem com tag EXIF de orientação "normal" (valor 1) — nenhuma rotação
  deve ser aplicada.
- Formato WEBP: PIL/Pillow lê EXIF de arquivos WEBP também, mas é menos
  comum esse formato carregar a tag de orientação (normalmente já vem
  com os pixels corrigidos); o tratamento deve ser genérico o bastante
  para cobrir os 3 formatos do domínio (png/jpg/webp) sem assumir que só
  JPG tem o problema.

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — corrigir a orientação da imagem com base no
   metadado EXIF, antes de aplicar a marca d'água e ao gerar thumbnails.
2. **Onde aplicar**: **nas duas** — `apply_watermark()` (`watermark.py`)
   e a geração de thumbnails (`gui.py`).
3. **Abordagem técnica**: **gravar a rotação diretamente nos pixels**
   (`PIL.ImageOps.exif_transpose()`); o arquivo gerado não depende mais
   de EXIF para aparecer correto em qualquer visualizador.
4. **Dimensões após correção**: **aceitável** que largura/altura se
   invertam quando a correção rotaciona a imagem 90°/270°.
5. **Fixture de teste**: **gerar sinteticamente** uma imagem com tag EXIF
   de orientação (ex.: `Orientation = 6`) via Pillow, seguindo o mesmo
   padrão das fixtures existentes em `tests/conftest.py`.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

Pré-checagem feita durante o planejamento (sem precisar de `piexif` — só
Pillow puro):

```python
img = Image.new("RGB", (300, 200), (10, 20, 30))
exif = img.getexif()
exif[274] = 6  # Orientation
img.save(path, format="JPEG", exif=exif)

reopened = Image.open(path)              # size (300, 200), orientation tag 6
transposed = ImageOps.exif_transpose(reopened)
# size (200, 300) — largura/altura invertidas, como esperado
# transposed.format é None — .format NÃO é preservado pela transposição
```

**Achado importante**: `ImageOps.exif_transpose()` não preserva o atributo
`.format` da imagem original. Isso significa que `base_format =
base.format` em `apply_watermark()` precisa ser capturado **antes** de
chamar `exif_transpose()`, senão o `canvas.save(..., format=base_format)`
quebra (formato `None`). Isso vira uma nota de implementação na tarefa 1.

### 1. Corrigir orientação em `apply_watermark()`
- **Arquivo(s):** `src/tatoo/watermark.py`
- **O que muda:** logo após `base = Image.open(image_path)`, captura
  `base_format = base.format` (antes de qualquer transposição, conforme
  achado da pré-checagem) e então aplica
  `base = ImageOps.exif_transpose(base)` para normalizar a orientação
  antes de `base.convert("RGBA")` e do cálculo de posição do logo
  (`canvas.width`/`canvas.height` já refletem as dimensões corrigidas
  automaticamente, sem mudança adicional na lógica de centralização).
- **Validar:** `uv run ruff check src/tatoo/watermark.py` e
  `uv run ruff format --check src/tatoo/watermark.py` sem apontamentos
  (teste funcional de orientação vem na tarefa 4).

### 2. Corrigir orientação na geração de thumbnails
- **Arquivo(s):** `src/tatoo/gui.py`
- **O que muda:** em `_make_thumbnail_image()`, aplica
  `img = ImageOps.exif_transpose(img)` logo após `Image.open(path)` (e
  antes de `img.convert("RGB")` / `img.thumbnail(size)`), para que a
  miniatura reflita a orientação corrigida.
- **Validar:** `uv run ruff check src/tatoo/gui.py` e
  `uv run ruff format --check src/tatoo/gui.py` sem apontamentos.

### 3. Fixture de imagem com EXIF de orientação
- **Arquivo(s):** `tests/conftest.py`
- **O que muda:** adiciona uma fixture (ex.: `rotated_jpg_image`) que cria
  uma imagem JPEG retangular (largura ≠ altura, ex.: 300×200) com a tag
  EXIF `Orientation = 6`, salva em `tmp_path`, seguindo o mesmo padrão de
  `png_image`/`jpg_image` já existentes.
- **Validar:** `uv run pytest --collect-only` executa sem erro de coleta.

### 4. Testes de correção de orientação
- **Arquivo(s):** `tests/test_watermark.py`, `tests/test_gui.py`
- **O que muda:**
  - em `test_watermark.py`, novo teste que aplica `apply_watermark()` em
    `rotated_jpg_image` e confirma que as dimensões do arquivo gerado
    correspondem à orientação **corrigida** (largura/altura invertidas em
    relação ao arquivo bruto, ex.: bruto 300×200 → gerado 200×300);
  - em `test_gui.py`, novo teste que confirma que
    `_make_thumbnail_image(rotated_jpg_image)` produz uma miniatura cuja
    proporção reflete a orientação corrigida (ex.: altura ≥ largura para
    uma imagem que passa a ser "em pé" após a correção).
- **Validar:** `uv run pytest -v` mostra os novos testes passando.

### 5. Rodar suíte completa, lint e validação manual final
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto, incluindo os casos de borda da spec (imagem sem tag EXIF,
  imagem com orientação "normal").
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Se você
  tiver alguma foto real de celular com orientação vertical à mão, pedir
  para rodar `uv run tatoo` manualmente e confirmar que ela aparece em pé
  tanto na miniatura da lista de seleção quanto no arquivo `*_marcada.*`
  gerado.
