# Processo — como um campo novo chega à produção

Mapeamento do processo de governança: da necessidade de negócio até o campo documentado em produção.

```mermaid
flowchart LR
    A[Área de negócio<br/>pede um novo dado] --> B[Analista de Dados<br/>escreve a especificação funcional]
    B --> C[Engenharia de Dados<br/>cria o campo no SQL]
    C --> D[Analista de Dados<br/>documenta no dicionário,<br/>glossário e regra RNxx]
    D --> E{Portão de governança<br/>validar_documentacao.py}
    E -- REPROVADO --> D
    E -- APROVADO --> F[Governança aprova<br/>o Pull Request]
    F --> G[Produção + Confluence<br/>+ Unity Catalog atualizados]
```

| Etapa | Responsável | Entregável | Onde fica |
|---|---|---|---|
| 1. Necessidade | Área de negócio | Pedido com a pergunta de negócio | Jira / e-mail |
| 2. Especificação | Analista de Dados | Especificação funcional | `docs/especificacao_funcional_*.md` |
| 3. Desenvolvimento | Engenharia de Dados | SQL do campo | `sql/` |
| 4. Documentação | Analista de Dados | Dicionário, glossário, regra, De x Para | `metadados/*.csv` |
| 5. Validação | Automática (CI) | Relatório do portão | GitHub Actions |
| 6. Aprovação | Governança | Pull Request aprovado | GitHub |
| 7. Publicação | Automática | Confluence e Unity Catalog | `src/gerar_documentacao.py` |

**Regra de ouro:** se a etapa 5 reprovar, o campo não vai para produção.
Demonstração: `python src/validar_documentacao.py --simular-campo-novo`
