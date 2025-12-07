#!/usr/bin/python
# encoding: utf-8

import re

class ParticipacaoEmBanca:
    item = None
    idMembro = None
    
    natureza = ''
    titulo = ''
    ano = ''
    
    def __init__(self, idMembro, partesDoItem):
        self.idMembro = idMembro
        if len(partesDoItem) >= 2:
            self.item = partesDoItem[1]
        elif len(partesDoItem) == 1:
            self.item = partesDoItem[0]
        else:
            self.item = ''
        
        # Example format: 
        # "MOURA, E. S.; BARCELLOS, M. P.; NASCIMENTO, E. L.. Participação em banca de SILVA, N. D., PAULA, Z. E., MORAES, R. F..Sistema de Orçamento de Obra Distribuído. 2003. Trabalho de Conclusão de Curso (Graduação em Sistemas de Informação) - Faculdade Vitoriana de Ensino Superior."
        
        partes = self.item
        
        # Tenta extrair o ano
        match = re.search(r'\d{4}', self.item)
        if match:
            self.ano = match.group(0)
        else:
            self.ano = ''

        # Extract title/description
        # Usually starts after the authors and ends before the year/nature
        # This is a bit complex due to variability. For now, we'll store the full text as title/item
        # and try to extract specific parts if possible.
        
        self.titulo = partes # Default to full text
        
        # Try to clean up authors if possible, but Lattes format varies a lot for Bancas.
        # Common pattern: Authors. "Participação em banca de...". Year. Nature.
        
        # Let's try to extract the nature (e.g. "Trabalho de Conclusão de Curso", "Mestrado", etc)
        # Often at the end or near the year.
        
    def obter_tipo(self):
        texto = self.item.lower()
        
        if "doutorado" in texto or "tese" in texto:
            if "qualificação" in texto or "qualificacao" in texto:
                 return "Qualificação de Doutorado"
            return "Tese de Doutorado"
        
        if "mestrado" in texto or "dissertação" in texto or "dissertacao" in texto:
            if "qualificação" in texto or "qualificacao" in texto:
                return "Qualificação de Mestrado"
            return "Mestrado"
            
        if "graduação" in texto or "graduacao" in texto or "conclusão de curso" in texto or "conclusao de curso" in texto or "tcc" in texto:
            return "Trabalho de Conclusão de Curso de Graduação"
            
        if "qualificação" in texto or "qualificacao" in texto:
            return "Qualificação de Mestrado"
            
        return "Participação em banca"

    def obter_aluno(self):
        # Tenta extrair o nome do aluno após "Participação em banca de "
        # Procura até o próximo ponto (ou dois pontos) seguido de espaço e letra maiúscula/número que NÃO seja seguido de ponto (para evitar iniciais), ou fim da string
        match = re.search(r'Participação em banca de (.+?)(?=\.{1,2}\s*[A-Z0-9][^.]|$)', self.item, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def obter_membros(self):
        match = re.search(r'^(.+?)\.\s*Participação em banca de', self.item, re.IGNORECASE)
        if match:
            # Split by semicolon and strip whitespace
            membros = match.group(1).split(';')
            return [m.strip() for m in membros if m.strip()]
        return []

    def obter_titulo(self):
        # Tenta extrair o título: entre o aluno e o ano
        # Regex: Aluno (já extraído) . Título . Ano
        aluno = self.obter_aluno()
        if not aluno:
            return ""
        
        # Escape special characters in student name for regex
        aluno_escaped = re.escape(aluno)
        
        # Procura texto entre o aluno e o ano
        # Assumes format: ... aluno. Titulo. Ano. ...
        regex = r'Participação em banca de ' + aluno_escaped + r'\.+(.+?)\.+\s*' + str(self.ano)
        match = re.search(regex, self.item, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('.')
        return ""

    def obter_curso(self):
        # Tenta extrair o curso/natureza: entre o ano e " - " ou fim
        # Format: ... Ano. Curso - Universidade
        regex = str(self.ano) + r'\.\s*(.+?)(?=\s+-\s+|$)'
        match = re.search(regex, self.item)
        if match:
            return match.group(1).strip()
        return ""

    def obter_universidade(self):
        # Tenta extrair a universidade: após " - " no final
        match = re.search(r'\s+-\s+([^.-]+?)\.?$', self.item)
        if match:
            return match.group(1).strip()
        return ""

    def json(self):
        return {
            "descricao": self.item,
            "ano": int(self.ano) if str(self.ano).isdigit() else 0,
            "tipo": self.obter_tipo(),
            "aluno": self.obter_aluno(),
            "membros_banca": self.obter_membros(),
            "titulo_trabalho": self.obter_titulo(),
            "curso": self.obter_curso(),
            "universidade": self.obter_universidade()
        }
