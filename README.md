# tatoo

Aplicação desktop (Windows/Linux) para aplicar marcas d'água em imagens
PNG, JPG e WEBP.

## Stack

- Python >=3.12
- GUI: Tkinter/ttk (biblioteca padrão do Python)
- Gerenciador de dependências: [uv](https://docs.astral.sh/uv/)
- Testes: pytest
- Lint/format: ruff

## Setup

Instalar as dependências do projeto:

```bash
uv sync
```

Rodar a suíte de testes:

```bash
uv run pytest
```

Rodar lint e checagem de formatação:

```bash
uv run ruff check .
uv run ruff format --check .
```

## Requisitos do sistema

O Tkinter é parte da biblioteca padrão do Python, mas em algumas
distribuições Linux o suporte a GUI não vem pré-instalado com o Python do
sistema. Caso `uv run python -c "import tkinter"` falhe, instale o pacote
do seu gerenciador de pacotes, por exemplo:

```bash
sudo apt install python3-tk
```
