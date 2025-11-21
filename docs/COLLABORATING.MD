# 📘 Guia de Colaboração 

Bem-vindo ao nosso guia de contribuição! Este documento define os padrões, boas práticas e o fluxo de trabalho para garantir que possamos colaborar de forma ágil e segura neste repositório único.

---

## 1. Princípios do Monorepo

Trabalhar em um monorepo significa que múltiplos projetos e bibliotecas compartilham o mesmo histórico de Git.

* **Atomicidade:** Suas mudanças devem ser pequenas e focadas.
* **Responsabilidade Compartilhada:** Se você alterar uma biblioteca compartilhada (`shared-lib`), é sua responsabilidade garantir que ela não quebre os projetos que dependem dela.
* **Visibilidade:** Todo código é visível. Antes de criar algo novo, verifique se já não existe um componente ou função utilitária pronta.

---

## 2. Estrutura de Branches

Utilizamos uma estratégia simplificada baseada em **Trunk Based Development**.

* **Branch Principal:** `main` (Deve estar sempre "deployable").
* **Branches de Feature:** Devem ter vida curta e ser mergeadas rapidamente.

### Convenção de Nomes
Use o padrão: `<tipo>/<escopo>/<descrição-curta>`

| Tipo | Descrição | Exemplo |
| :--- | :--- | :--- |
| **feat** | Nova funcionalidade | `feat/login/sso-integration` |
| **fix** | Correção de bug | `fix/cart/calc-error` |
| **chore** | Manutenção/Configuração | `chore/deps/upgrade-react` |
| **refactor** | Melhoria de código sem mudar comportamento | `refactor/ui/simplify-button` |
| **docs** | Apenas documentação | `docs/readme/update-setup` |

> **Nota:** O `<escopo>` refere-se ao projeto ou lib que você está alterando (ex: `backend`, `web-app`, `ui-kit`).

---

## 3. Padrão de Commits


**Formato:**
```text
<tipo>(<escopo opcional>): <descrição no imperativo>
```


### Exemplos

*   ✅ feat(ui-kit): adiciona variante primary no button
    
*   ✅ fix(api): corrige status code no endpoint de user
    
*   ✅ chore: atualiza .gitignore

## 4. Pull Requests

O PR é o momento de revisão de qualidade. Após finalizar as tasks referentes à branch em questão, abra um PR para análise da(s) task(s).

**Checklist Obrigatório:**

1.  \[ \] **Título Semântico:** Segue o mesmo padrão dos commits.
    
2.  \[ \] **Descrição:** Explica o porquê da mudança e como testar.
    
3.  \[ \] **Evidências:** Screenshots ou GIFs (obrigatório para mudanças visuais/frontend).
    
4.  \[ \] **Testes:** Passou nos testes locais e no CI.
    

**Revisão (Code Review):**

*   Aguarde a aprovação de pelo menos 1 revisor.
    
*   Não faça merge se o build estiver quebrado.