# Guia de Contribuição - scriptLattes

Obrigado por considerar contribuir com o scriptLattes! Este documento fornece diretrizes para contribuir com melhorias, correções de bugs e novas funcionalidades.

## 🚀 Começando

### Pré-requisitos
- Python 3.6+
- Conhecimento básico de HTML parsing
- Familiaridade com o formato de dados do Currículo Lattes

### Configuração do Ambiente
```bash
git clone [repository-url]
cd scriptLattes
make install  # ou pip install -r requirements.txt
```

## 🐛 Reportando Bugs

### Antes de reportar
1. ✅ Verifique se o bug já foi reportado
2. ✅ Teste com dados de exemplo: `python scriptLattes.py exemplo/teste-01.config`
3. ✅ Consulte o [CHANGELOG.md](CHANGELOG.md) para bugs já corrigidos

### Template para Bug Report
```markdown
**Descrição do Bug**: [Descrição clara e concisa]

**Para Reproduzir**:
1. Arquivo de configuração usado: `[exemplo/teste-01.config]`
2. Comando executado: `[python scriptLattes.py ...]`
3. Resultado esperado vs obtido

**Dados de Teste**:
- Nome do pesquisador afetado: [Nome]
- Seção específica com problema: [Projetos/Áreas/etc.]

**Ambiente**:
- OS: [Ubuntu 20.04 / Windows 10 / macOS]
- Python: [3.8.5]
- Browser: [Chrome 91.0]

**JSON de Exemplo** (se aplicável):
```json
{
  "problema": "campo_ausente ou valor_incorreto"
}
```
```

## 🔧 Desenvolvendo Melhorias

### Estrutura do Projeto
```
scriptLattes/
├── scriptLattes.py          # Entry point principal
├── scriptLattes/
│   ├── parserLattes.py      # Parser principal HTML → Objetos
│   ├── membro.py           # Classe Membro + dados
│   ├── grupo.py            # Classe Grupo + JSON export
│   └── producoesUnitarias/ # Classes de dados específicas
│       ├── projetoDePesquisa.py
│       ├── projetoDeExtensao.py  
│       └── projetoDeDesenvolvimento.py  # ← Exemplo de nova funcionalidade
```

### Padrão para Novas Funcionalidades

#### 1. Criando Nova Classe de Dados
```python
# scriptLattes/producoesUnitarias/novoTipoDeProducao.py
from .base import ProducaoBase

class NovoTipoDeProducao(ProducaoBase):
    def __init__(self, linhas_html=None):
        super().__init__()
        self.tipo_novo = None
        self.campo_especifico = None
        
        if linhas_html:
            self._parse(linhas_html)
    
    def _parse(self, linhas):
        """Parsing específico do HTML"""
        # Implementar lógica de extração
        pass
        
    def json(self):
        """Serialização JSON"""
        return {
            'tipo': 'Novo Tipo de Produção',
            'tipo_novo': self.tipo_novo,
            'campo_especifico': self.campo_especifico
        }
        
    def compararCom(self, outro):
        """Comparação para detectar duplicatas"""
        # Implementar lógica de similaridade
        return 0.0
```

#### 2. Atualizando Parser Principal
```python
# scriptLattes/parserLattes.py

# Adicionar flag de controle
def __init__(self):
    self.achouNovoTipo = False

# Adicionar detecção de seção
def handle_starttag(self, tag, attrs):
    if tag == 'div':
        for attr_name, attr_value in attrs:
            if 'Nova seção identificada' in attr_value:
                self.achouNovoTipo = True
                
# Adicionar nas condições de processamento
def salvarParte3(self, dados):
    if (self.achouArtigo or ... or self.achouNovoTipo):
        # Lógica de processamento
```

#### 3. Integrando no Membro
```python
# scriptLattes/membro.py

def __init__(self):
    self.listaNovoTipo = []

# No método de parsing
if parser.achouNovoTipo:
    item = NovoTipoDeProducao(parser.parte3)
    self.listaNovoTipo.append(item)
```

#### 4. Exportação JSON
```python
# scriptLattes/grupo.py

def json(self):
    return {
        'novo_tipo_producoes': [item.json() for item in membro.listaNovoTipo]
    }
```

### Diretrizes de Código

#### Python Style
- Seguir PEP 8 para formatação
- Usar nomes descritivos em português (compatível com codebase)
- Documentar métodos complexos

#### Parser HTML
- **CRÍTICO**: Testar com múltiplos pesquisadores para evitar contaminação
- Reset de flags após processamento de cada membro
- Usar padrão `salvarParte3` para consistência
- Tratamento robusto de caracteres especiais

#### Regex Patterns
```python
# ✅ Correto: Captura até ponto final ou fim da linha
regex_correto = r'Campo:\s*([^.]+?)(?:\.|$)'

# ❌ Evitar: Pode perder dados com espaços
regex_problematico = r'Campo:\s*([^./]+)'
```

### Processo de Testing

#### Testes Obrigatórios
```bash
# 1. Teste básico
python scriptLattes.py exemplo/teste-01.config

# 2. Verificar JSON
jq keys json/*.json

# 3. Verificar contaminação (executar 2x)
python scriptLattes.py exemplo/teste-01.config
python scriptLattes.py exemplo/teste-01.config
diff json/ json_anterior/  # Deve ser idêntico

# 4. Teste com múltiplos pesquisadores
python scriptLattes.py exemplo/ensp2024.config
```

#### Validações Específicas
- ✅ Dados do Paulo: 9 pesquisa + 2 extensão + 7 desenvolvimento
- ✅ Dados do Daniel: 5 pesquisa + 0 extensão + 5 desenvolvimento  
- ✅ Áreas de atuação: múltiplas por pesquisador
- ✅ Especialidades: texto completo preservado

## 📋 Checklist para Pull Request

### Antes de Submeter
- [ ] ✅ Código testado com `exemplo/teste-01.config`
- [ ] ✅ JSON gerado sem erros: `jq . json/*.json`
- [ ] ✅ Não há contaminação entre pesquisadores
- [ ] ✅ Funcionalidades existentes não foram quebradas
- [ ] ✅ Documentação atualizada se necessário

### Informações Obrigatórias
- **Tipo**: [Bug Fix / Nova Funcionalidade / Melhoria]
- **Seções Afetadas**: [Projetos / Áreas / etc.]
- **Arquivos Modificados**: Lista dos arquivos alterados
- **Testes Realizados**: Comandos e resultados
- **Breaking Changes**: Sim/Não + detalhes

### Template de PR
```markdown
## Descrição
[Descrição clara da mudança]

## Motivação
[Por que esta mudança é necessária]

## Arquivos Alterados
- `scriptLattes/parserLattes.py`: [descrição]
- `scriptLattes/membro.py`: [descrição]

## Testes Realizados
```bash
python scriptLattes.py exemplo/teste-01.config
jq '.novo_campo' json/*.json
```

## Compatibilidade
- [ ] ✅ Backward compatible
- [ ] ✅ Não quebra JSONs existentes
- [ ] ✅ Documentação atualizada
```

## 🚀 Deployment e Versioning

### Processo de Release
1. **Update Version**: Atualizar número da versão em `scriptLattes.py`
2. **Update Changelog**: Adicionar entradas no `CHANGELOG.md`
3. **Testing**: Rodar suite completa de testes
4. **Documentation**: Atualizar `README.md` se necessário

### Git Workflow
```bash
# Feature branch
git checkout -b feature/nova-funcionalidade

# Commits descritivos
git commit -m "feat: adiciona extração de nova seção"
git commit -m "fix: corrige contaminação entre membros"
git commit -m "docs: atualiza README com novos campos"

# Pull request via GitHub/GitLab
```

### Commit Messages
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Apenas documentação
- `test:` Adiciona ou modifica testes
- `refactor:` Refatoração sem mudança funcional

## 🤝 Comunidade

### Comunicação
- **Discord**: [https://discord.gg/Xz8NZ3kBc3]
- **Email**: [jesus.mena@ufabc.edu.br]
- **Issues**: Use o sistema de issues do repositório

### Filosofia do Projeto
- **Simplicidade**: Manter código legível e manutenível
- **Robustez**: Sistema deve funcionar com dados reais e variados
- **Compatibilidade**: Preservar funcionamento de sistemas existentes
- **Documentação**: Código bem documentado facilita contribuições futuras

---

## 💡 Dicas Importantes

### Debug Efetivo
```python
# Adicione prints temporários para debugging
print(f"DEBUG: Flag ativa: {self.achouNovoTipo}")
print(f"DEBUG: Dados capturados: {parte3[:100]}...")

# Use JSONs para validar dados
import json
print(json.dumps(objeto.json(), indent=2, ensure_ascii=False))
```

### Armadilhas Comuns
- ❌ **Reset prematuro**: Não resetar flags antes de processar todos os itens
- ❌ **Estado global**: Não compartilhar estado entre diferentes membros
- ❌ **Regex frágil**: Testar regex com dados reais, não apenas exemplos
- ❌ **Codificação**: Atenção com caracteres especiais do português

### Recursos Úteis
- [Documentação Python HTMLParser](https://docs.python.org/3/library/html.parser.html)
- [Regex Testing](https://regex101.com/) para testar expressões regulares
- [JSON Validator](https://jsonlint.com/) para validar estruturas JSON

Obrigado por contribuir com o scriptLattes! 🎉