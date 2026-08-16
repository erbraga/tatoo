# CLAUDE.md — Instruções do Projeto

## Sobre o projeto
Aplicação comercial desktop rodando localmente em ambiente Windows ou Linux.
Sem integração com IA no produto final — o Claude Code é usado apenas como ferramenta de desenvolvimento.

O domínio é aplicação de marcas d'água em imagens salvas nos formatos png, jpg ou webp.


## Stack
- Linguahem de programação: Python
- Biblioteca para GUI: Tkinter/ttk (biblioteca padrão do Python)
- gerenciador de dependências: uv
- versão do Python: >=3.12

## Fluxo de trabalho obrigatório (Spec-Driven Development)

Antes de implementar qualquer feature não-trivial, siga estas 4 fases.
NÃO pule direto para escrever código.

1. **Explorar** — leia os arquivos relevantes  antes de propor qualquer mudança. Não assuma estrutura sem
   confirmar lendo o código.
2. **Especificar (spec)** — escreva um documento curto em `docs/specs/AAAA-MM-DD-nome-da-feature.md` descrevendo: o problema, o que muda, o que fica de fora do escopo, e decisões de design em  aberto. Pare aqui e aguarde revisão antes de seguir.
3. **Planejar** — depois que a spec for aprovada, converta em um plano de tarefas pequenas e ordenadas, cada uma com arquivo(s) afetado(s) e como validar (comando de teste, migration, etc). Pare aqui e aguarde revisão antes de seguir.
4. **Implementar** — execute o plano tarefa por tarefa. Rode testes e `python manage.py check` antes de considerar uma tarefa concluída.

Use o template em `docs/specs/TEMPLATE.md` para novas specs.


## O que NÃO fazer
- Não implementar features fora do escopo da spec aprovada sem avisar.
- Não modificar arquivos de configuração de produção sem confirmação explícita.
- Não instalar novas dependências sem justificar a escolha.
- Não remover ou reescrever testes existentes para "fazer passar".

## Testes e validação
- Framework:  pytest .

- Antes de finalizar qualquer tarefa: rodar a suíte de testes e
  `python manage.py check --deploy` quando aplicável.

## Estado atual / débitos técnicos conhecidos
