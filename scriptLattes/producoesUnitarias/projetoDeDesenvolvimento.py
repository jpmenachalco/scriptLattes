#!/usr/bin/python
# encoding: utf-8
# filename: projetoDeDesenvolvimento.py
#
#  scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
#
#  Este programa é um software livre; você pode redistribui-lo e/ou 
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como 
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da 
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util, 
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from .projetoDePesquisa import ProjetoDePesquisa
from ..util import similaridade_entre_cadeias


class ProjetoDeDesenvolvimento(ProjetoDePesquisa):
    tipo = 'Projeto de desenvolvimento'
    
    def __init__(self, idMembro, partesDoItem):
        try:
            super().__init__(idMembro, partesDoItem)
            self.tipo = 'Projeto de desenvolvimento'
        except Exception as e:
            # Fallback para inicialização manual se der erro
            self.idMembro = list([])
            self.idMembro.append(idMembro)
            self.integrantes = []
            
            if len(partesDoItem) >= 2:
                anos = partesDoItem[0].partition("-")
                self.anoInicio = anos[0].strip()
                self.anoConclusao = anos[2].strip()
                
                self.nome = partesDoItem[1].strip()
                if len(partesDoItem) >= 3:
                    self.descricao = partesDoItem[2:]
                    # Extrair integrantes da descrição se disponível
                    if len(partesDoItem) >= 3 and partesDoItem[2]:
                        self._extrair_integrantes(partesDoItem[2])
                else:
                    self.descricao = []
            else:
                self.anoInicio = ""
                self.anoConclusao = ""
                self.nome = ""
                self.descricao = []
            
            self.tipo = 'Projeto de desenvolvimento'
    
    def json(self):
        def nv(x):
            return x if x not in (None, '', []) else None

        # preparar integrantes para JSON
        integrantes_json = []
        if hasattr(self, 'integrantes') and self.integrantes:
            integrantes_json = [
                {
                    "nome": integrante["nome"],
                    "papel": integrante["papel"]
                }
                for integrante in self.integrantes
            ]

        # preparar financiadores para JSON
        financiadores_json = []
        if hasattr(self, 'financiadores') and self.financiadores:
            financiadores_json = [
                {
                    "nome": financiador["nome"],
                    "tipo_apoio": financiador["tipo_apoio"]
                }
                for financiador in self.financiadores
            ]

        result = {
            'nome': nv(self.nome),
            'ano_inicio': nv(str(self.anoInicio) if hasattr(self, 'anoInicio') and self.anoInicio else None),
            'ano_conclusao': nv(str(self.anoConclusao) if hasattr(self, 'anoConclusao') and self.anoConclusao else None),
            'descricao': nv(self.descricao if hasattr(self, 'descricao') else None),
            'tipo': self.tipo
        }

        # Adicionar integrantes se existirem
        if integrantes_json:
            result["integrantes"] = integrantes_json

        # Adicionar financiadores se existirem
        if financiadores_json:
            result["financiadores"] = financiadores_json

        return result
    
    def html(self):
        s = '\n<p><b>' + str(self.nome).encode('utf8', 'replace').decode('utf8') + '</b><br>'
        if hasattr(self, 'anoInicio') and self.anoInicio:
            s += 'Ano de início: ' + str(self.anoInicio) + '<br>'
        if hasattr(self, 'anoConclusao') and self.anoConclusao:
            s += 'Ano de conclusão: ' + str(self.anoConclusao) + '<br>'
        if hasattr(self, 'descricao') and self.descricao:
            for desc in self.descricao:
                if desc.strip():
                    s += str(desc).encode('utf8', 'replace').decode('utf8') + '<br>'
        s += '</p>'
        return s
    
    def compararCom(self, objeto):
        """Compara este projeto de desenvolvimento com outro objeto"""
        if not isinstance(objeto, ProjetoDeDesenvolvimento):
            return None
        
        # Compara nomes dos projetos    
        limiar = 0.6
        if similaridade_entre_cadeias(self.nome, objeto.nome) > limiar:
            return self  # Retorna o primeiro objeto por simplicidade
        
        return None
