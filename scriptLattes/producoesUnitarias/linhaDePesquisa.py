#!/usr/bin/python
# encoding: utf-8
# filename: linhaDePesquisa.py
#
# scriptLattes V8.10, Copyright 2005-2018: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
# http://scriptlattes.sourceforge.net/
#
# Este programa é um software livre; você pode redistribui-lo e/ou 
# modifica-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 2 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser útil, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import sys
from ..util import *

class LinhaDePesquisa:
    nome = None
    objetivo = None
    idMembro = []
    
    def __init__(self, partesDoItem=None):
        self.idMembro = []
        
        if partesDoItem is None:
            return
            
        try:
            # Primeira parte geralmente contém o nome da linha de pesquisa
            self.nome = partesDoItem[1].strip() if len(partesDoItem) > 1 else ''
            
            # Segunda parte pode conter objetivo/descrição (se presente)
            self.objetivo = ''
            if len(partesDoItem) > 2 and partesDoItem[2].strip():
                # Procura por "Objetivo:" ou similar
                objetivo_texto = partesDoItem[2].strip()
                if 'Objetivo:' in objetivo_texto:
                    self.objetivo = objetivo_texto.replace('Objetivo:', '').strip()
                elif objetivo_texto and not objetivo_texto.startswith('Situação:') and not objetivo_texto.startswith('Integrantes:'):
                    self.objetivo = objetivo_texto
                    
            # Filtrar linhas vazias ou inválidas
            if not self.nome or len(self.nome.strip()) == 0:
                self.nome = None
                
        except Exception as e:
            print(f"Erro ao processar linha de pesquisa: {e}", file=sys.stderr)
            self.nome = None
            self.objetivo = ''

    def json(self):
        """Retorna representação JSON da linha de pesquisa"""
        if not self.nome or not self.nome.strip():
            return None
        return {
            'nome': self.nome.strip(),
            'objetivo': (self.objetivo or '').strip()
        }

    def __str__(self):
        return f"LinhaDePesquisa(nome='{self.nome}', objetivo='{self.objetivo[:50] if self.objetivo else ''}')"

    def compararCom(self, outraLinha):
        """
        Compara duas linhas de pesquisa para detectar duplicatas
        Retorna um valor de 0 a 1 (1 = idênticas, 0 = completamente diferentes)
        """
        if not isinstance(outraLinha, LinhaDePesquisa):
            return 0
            
        # Se ambos os nomes estão vazios, considera 0
        if not self.nome and not outraLinha.nome:
            return 0
            
        # Se um dos nomes está vazio, considera baixa similaridade
        if not self.nome or not outraLinha.nome:
            return 0.1
            
        try:
            from ..util import similaridade_entre_cadeias
            similaridade = similaridade_entre_cadeias(self.nome, outraLinha.nome)
            return similaridade
        except:
            # Fallback para comparação simples
            if self.nome.lower() == outraLinha.nome.lower():
                return 1.0
            return 0.3