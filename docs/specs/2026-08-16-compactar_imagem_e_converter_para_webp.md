# Compactar Imagem e Converter para WEBP — Spec

**Criado em:** 2026-08-16
**Status:** decisões resolvidas — aguardando aprovação final para virar plano

## Contexto (o que encontrei no código)

- `src/tatoo/watermark.py::apply_watermark()` hoje salva o resultado
  **no mesmo formato do arquivo de entrada**
  (`canvas.save(output_path, format=base_format)`), sem passar nenhum
  parâmetro de qualidade/compressão — usa os valores padrão do Pillow
  para cada formato (ex.: JPEG ≈ 75, WEBP ≈ 80, PNG sempre sem perda).
  Se a imagem é JPG, o resultado é `_marcada.jpg`; se é PNG, é
  `_marcada.png`; se é WEBP, é `_marcada.webp`.
- Essa decisão ("formato de saída igual ao de entrada") foi tomada
  **explicitamente** na spec anterior
  [2026-08-16-aplicar_marca_dagua_hardcoded.md](2026-08-16-aplicar_marca_dagua_hardcoded.md).
  Esta nova feature **reverte** essa decisão — vale deixar isso explícito
  para você confirmar antes de seguir.
- Conferi o tamanho de um arquivo real gerado
  (`img/20260226_114501_marcada.webp`, 487 KB) contra o original
  (`img/20260226_114501.webp`, 486 KB) — praticamente idêntico, ou seja,
  hoje não há nenhuma compressão adicional sendo aplicada além do que o
  formato de entrada já tinha.
- As fotos reais do projeto em `img/` são grandes: 4000×1848 pixels,
  480–590 KB cada em WEBP. Confirma que reduzir o tamanho do arquivo é um
  objetivo real e não hipotético.
- Não existe hoje nenhuma lógica de redimensionamento (resize) em
  `watermark.py` — só a composição do logo sobre a imagem, nas dimensões
  originais.
- `src/tatoo/gui.py` (lista de resultado, `_result_lines`) só usa
  `path.name` do arquivo retornado por `apply_watermark()` — ou seja, se
  a extensão do arquivo gerado mudar para `.webp`, a GUI reflete isso
  automaticamente, sem precisar de nenhuma mudança própria.
- `tests/test_watermark.py` tem 3 testes (`test_watermark_png`,
  `test_watermark_jpg`, `test_watermark_webp`) que hoje **esperam
  explicitamente** que a extensão de saída seja igual à de entrada (ex.:
  `output.name == "teste_marcada.png"`). Esses testes precisarão ser
  atualizados para reflet
  ir o novo comportamento (sempre `.webp`).
- O código atual converte para RGB (perdendo transparência) quando o
  formato final é JPEG ou WEBP (`if base_format in ("JPEG", "WEBP"):
  canvas = canvas.convert("RGB")`). Como WEBP suporta transparência
  (RGBA), isso é uma escolha específica a revisitar nesta feature.

Não há nenhuma descrição adicional da feature além do nome do argumento
(`compactar_imagem_e_converter_para_webp`). O nome é bem específico —
"compactar" (reduzir tamanho do arquivo) e "converter para webp"
(unificar o formato de saída) — mas ainda há vários parâmetros técnicos
sem valor definido, listados em "Decisões em aberto".

## Problema

O arquivo gerado por `apply_watermark()` hoje mantém o mesmo formato e,
na prática, o mesmo tamanho de arquivo da imagem original — sem nenhuma
compressão adicional. Isso significa que fotos grandes (ex.: 4000×1848,
quase 500 KB) geram resultados igualmente grandes, e usuários que
processam fotos em formatos diferentes (png, jpg, webp) recebem de volta
arquivos com extensões diferentes entre si.

## Objetivo

Fazer com que `apply_watermark()` sempre gere o resultado em **WEBP**,
com um nível de compressão que reduza o tamanho do arquivo de forma
perceptível, independente do formato da imagem de entrada (png, jpg ou
webp).

## Fora de escopo

- Interface para o usuário escolher o nível de compressão/qualidade —
  continua sendo um valor fixo no código, seguindo o padrão "hardcoded"
  já estabelecido no projeto.
- Redimensionar (mudar a resolução em pixels) da imagem — a menos que
  seja decidido incluir isso nesta feature (ver decisão em aberto #5).
- Mudar o filtro de seleção de arquivos na GUI (continua aceitando
  entrada em `.png/.jpg/.jpeg/.webp`) — a mudança é só no formato de
  **saída**.
- Qualquer alteração nos parâmetros do próprio logo (posição, opacidade).
- Processamento em lote com relatório de economia total de espaço.

## Proposta

Como vai funcionar, do ponto de vista do usuário e do código:

**Módulos afetados/criados**:
- `src/tatoo/watermark.py` (alterado): `apply_watermark()` passa a:
  - achatar sempre para RGB antes de salvar (mesmo comportamento que já
    existe hoje para JPEG/WEBP, agora aplicado também a PNGs com
    transparência);
  - salvar sempre com `format="WEBP"`, `quality=75`, sem `lossless`
    (compressão com perda);
  - nomear o arquivo de saída como `<stem>_<extensão-original>_marcada.webp`
    (ex.: `foto.png` → `foto_png_marcada.webp`, `foto.jpg` →
    `foto_jpg_marcada.webp`, `foto.webp` → `foto_webp_marcada.webp`),
    evitando colisão entre arquivos de entrada com formatos diferentes e
    mesmo nome-base;
  - **sem** redimensionar — as dimensões em pixels continuam as mesmas da
    imagem de entrada.
- `tests/test_watermark.py` (alterado): os 3 testes existentes são
  atualizados para esperar o novo nome de arquivo (`_png_marcada.webp`
  etc.) e formato WEBP na saída, para os três formatos de entrada.
- `src/tatoo/gui.py`: não deve precisar de alteração (usa `path.name` do
  retorno de `apply_watermark`).

**Fluxo principal (passo a passo)**:
1. Usuário seleciona uma ou mais imagens em qualquer formato do domínio
   (png, jpg, webp).
2. Usuário aplica a marca d'água normalmente.
3. Cada resultado é salvo como `<nome>_<extensão-original>_marcada.webp`,
   comprimido (WEBP lossy, qualidade 75), mesmo que o arquivo de entrada
   já fosse `.webp`.
4. A lista de resultado na GUI mostra os novos nomes `.webp` gerados.

**Casos de borda relevantes**:
- Entrada já é `.webp` — ainda assim passa pela recompressão (não é só
  copiada), respeitando o objetivo de "compactar".
- Entrada é PNG com transparência (canal alpha) — é achatada para RGB
  (perde transparência), mesmo comportamento já aplicado hoje a
  JPEG/WEBP.
- Colisão de nomes entre formatos diferentes: **resolvida** pelo novo
  padrão de nome (`<stem>_<ext>_marcada.webp`), que inclui a extensão
  original no nome de saída.

## Decisões em aberto

Nenhuma pendente — todas as decisões foram resolvidas pelo usuário:

1. **Escopo**: confirmado — `apply_watermark()` salva sempre como WEBP,
   para os três formatos de entrada, inclusive recomprimindo quando a
   entrada já é webp.
2. **Qualidade**: `quality=75`.
3. **Lossy/lossless**: **lossy** (com perda).
4. **Transparência**: **não preserva** — achata para RGB, mesmo
   comportamento já usado hoje para JPEG/WEBP.
5. **Redimensionamento**: **não** — só recompressão, dimensões em pixels
   inalteradas.
6. **Colisão de nomes**: resolvida incluindo a **extensão original no
   nome de saída** (`<stem>_<ext>_marcada.webp`).
7. **Testes existentes**: **sim**, atualizar os 3 testes de
   `test_watermark.py` para o novo comportamento.

## Plano de Implementação

Tarefas pequenas e ordenadas. Nenhum código é escrito nesta etapa — apenas
o plano de execução.

**Achado durante o planejamento** (fora do que a spec listou em "Módulos
afetados"): `tests/test_gui.py::test_process_files_partial_failure`
também quebra com a mudança, porque hoje ele afirma
`result.successes == [png_image.with_stem(f"{png_image.stem}_marcada")]`
— isso assume que a extensão de saída continua `.png`. Com o novo nome
(`teste_png_marcada.webp`), essa asserção passa a falhar. Por isso este
plano inclui uma tarefa extra para corrigir esse teste, além dos dois
arquivos já previstos na spec (`watermark.py` e `test_watermark.py`).

### 1. Atualizar `apply_watermark()` para sempre comprimir e converter para WEBP
- **Arquivo(s):** `src/tatoo/watermark.py`
- **O que muda:** remove a lógica que preserva o formato de entrada;
  depois de compor o logo, o canvas é sempre convertido para RGB (achata
  transparência, inclusive de PNGs); o arquivo é sempre salvo com
  `format="WEBP"`, `quality=75` (sem `lossless`); o nome de saída passa a
  ser `<stem>_<extensão-original-sem-ponto>_marcada.webp` (ex.:
  `foto.png` → `foto_png_marcada.webp`), no mesmo diretório da entrada.
  Dimensões em pixels não mudam.
- **Validar:** `uv run ruff check src/tatoo/watermark.py` e
  `uv run ruff format --check src/tatoo/watermark.py` sem apontamentos
  (validação funcional nas tarefas 2 e 3).

### 2. Atualizar `tests/test_watermark.py` para o novo comportamento
- **Arquivo(s):** `tests/test_watermark.py`
- **O que muda:** os 3 testes existentes (`test_watermark_png`,
  `test_watermark_jpg`, `test_watermark_webp`) passam a esperar o novo
  nome de arquivo (`teste_png_marcada.webp`, `teste_jpg_marcada.webp`, e
  o equivalente para o webp real) e confirmam que o arquivo gerado abre
  com `Image.open(output).format == "WEBP"`.
- **Validar:** `uv run pytest tests/test_watermark.py -v` mostra os 3
  testes passando com as novas expectativas.

### 3. Corrigir `tests/test_gui.py::test_process_files_partial_failure`
- **Arquivo(s):** `tests/test_gui.py`
- **O que muda:** atualiza a asserção do caminho de sucesso esperado para
  o novo padrão de nome de saída (`<stem>_png_marcada.webp`, já que a
  fixture usada é `png_image`), em vez do antigo
  `png_image.with_stem(f"{png_image.stem}_marcada")`.
- **Validar:** `uv run pytest tests/test_gui.py -v` mostra todos os
  testes de GUI passando.

### 4. Rodar suíte completa e lint
- **Arquivo(s):** nenhum (apenas validação)
- **O que muda:** nenhuma mudança de código; confirma que tudo funciona
  em conjunto.
- **Validar:** `uv run pytest` (suíte completa passando), `uv run ruff
  check .` e `uv run ruff format --check .` sem apontamentos. Como
  verificação extra do objetivo de "compactar", comparar manualmente o
  tamanho de um arquivo `*_marcada.webp` gerado para uma das fotos reais
  de `img/` contra o tamanho do arquivo original, confirmando que o
  resultado é visivelmente menor (ex.: com `ls -la`).
