#!/usr/bin/python
# encoding: utf-8
# filename: idioma.py
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


class Idioma:
    descricao = ''
    nome = ''
    proficiencia = ''

    def __init__(self, partesDoItem):
        # partesDoItem[0]: Nome do idioma
        # partesDoItem[1]: Descricao da proficiencia do idioma
        self.nome = partesDoItem[0].strip()
        self.proficiencia = partesDoItem[1].strip()

    # ------------------------------------------------------------------------ #
    def __str__(self):
        s = "\n[IDIOMA] \n"
        s += "+NOME        : " + self.nome.encode('utf8', 'replace') + "\n"
        s += "+PROFICIENCIA: " + self.proficiencia.encode('utf8', 'replace') + "\n"
        return s
