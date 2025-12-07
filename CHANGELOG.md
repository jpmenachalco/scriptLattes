# Changelog - scriptLattes

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [Versão Atual] - 2024-12-06

### ✨ Adicionado
- **Nova funcionalidade**: Extração de Projetos de Desenvolvimento
  - Implementação completa da classe `ProjetoDeDesenvolvimento`
  - Parser atualizado para detectar seção "Projetos de desenvolvimento"
  - Export JSON com campo `projetos_desenvolvimento`
  - Estatísticas atualizadas com `total_projetos_desenvolvimento`

### 🔧 Corrigido
- **Bug crítico**: Contaminação de dados entre pesquisadores diferentes
  - Problema: Dados de um membro vazavam para outros membros
  - Solução: Estado isolado para cada membro durante o processamento
  - Afeta: Projetos, áreas de atuação, idiomas, etc.

- **Áreas de Atuação**: Extração de múltiplas áreas por pesquisador
  - Problema: Apenas primeira área sendo extraída
  - Solução: Remoção incorreta do reset de flags durante processamento
  - Resultado: Todas as áreas de atuação agora extraídas

- **Especialidades em Áreas de Atuação**: Regex melhorado
  - Problema: Especialidades com espaços não eram capturadas
  - Solução: Regex otimizado `r'Especialidade:\s*([^.]+?)(?:\.|$)'`
  - Exemplo: "Processamento de Sinais Biológicos" agora funciona

- **Múltiplos Idiomas**: Correção similar às áreas de atuação
  - Problema: Apenas primeiro idioma extraído por pesquisador
  - Solução: Flags de idioma não resetadas prematuramente
  - Resultado: Todos os idiomas e proficiências extraídos

### 🚀 Melhorado
- **Parser HTML**: Condições de processamento otimizadas
  - Adicionada flag `achouProjetoDeDesenvolvimento` nas condições principais
  - Padrão `salvarParte3` implementado para projetos de desenvolvimento
  - Tratamento de "Projeto certificado" adicionado

- **Exportação JSON**: Estrutura de dados aprimorada
  - Campo `areas_de_atuacao` padronizado (antes `areas_atuacao`)
  - Estrutura completa: grande_area, area, subarea, especialidade
  - Descrição completa preservada para compatibilidade

- **Estatísticas**: Contadores expandidos
  - Todos os tipos de projetos agora contabilizados
  - Estatísticas automáticas para desenvolvimento
  - Dados consistentes entre HTML e JSON

## Detalhes Técnicos

### Arquivos Modificados
- `scriptLattes/parserLattes.py`: Correções principais de parser
- `scriptLattes/producoesUnitarias/projetoDeDesenvolvimento.py`: Nova classe
- `scriptLattes/membro.py`: Adição de lista de projetos de desenvolvimento
- `scriptLattes/grupo.py`: Melhorias no parsing e export JSON
- `scriptLattes/compiladorDeListas.py`: Compilação de projetos de desenvolvimento

### Testes Realizados
- **Paulo**: 9 pesquisa + 2 extensão + 7 desenvolvimento + 6 áreas + 1 idioma
- **Daniel**: 5 pesquisa + 0 extensão + 5 desenvolvimento + 4 áreas + 3 idiomas

### Compatibilidade
- ✅ Backward compatible: JSONs antigos continuam funcionando
- ✅ Novos campos são adicionais, não substituem existentes
- ✅ HTML tradicional não afetado pelas mudanças

## Versões Anteriores

### [Baseline] - Versão Original
- Extração básica de produções bibliográficas
- Projetos de pesquisa e extensão
- Export HTML tradicional
- Funcionalidades básicas do scriptLattes original

---

## Como Contribuir

Se você encontrar bugs ou quiser sugerir melhorias:

1. Verifique se o problema já foi reportado
2. Teste com dados de exemplo primeiro
3. Forneça exemplos específicos do problema
4. Inclua informações do ambiente (Python, OS, etc.)

Para desenvolvedores:
- Siga o padrão existente de classes para novos tipos de dados
- Teste com múltiplos pesquisadores para evitar contaminação
- Mantenha compatibilidade com JSONs existentes
- Documente mudanças significativas neste changelog