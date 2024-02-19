#!/usr/bin/python
#  encoding: utf-8
#
#  scriptLattes
#  http://scriptlattes.sourceforge.net/
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

import pygraphviz
from PIL import Image


class GrafoDeColaboracoes:
    grupo = None
    cores = None

    grafoDeCoAutoriaSemPesos = None
    grafoDeCoAutoriaSemPesosCMAPX = None
    grafoDeCoAutoriaComPesos = None
    grafoDeCoAutoriaComPesosCMAPX = None
    grafoDeCoAutoriaNormalizado = None
    grafoDeCoAutoriaNormalizadoCMAPX = None

    def __init__(self, grupo, diretorioDeSaida):
        self.grupo = grupo

        # atribuicao de cores nos vértices
        for membro in self.grupo.listaDeMembros:
            corDoNoFG = '#FFFFFF'
            corDoNoBG = '#0A6EA4'
            if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
                indice = self.grupo.listaDeRotulos.index(membro.rotulo)
                cor = self.atribuirCorLegal(indice)
                corDoNoFG = cor[0]
                corDoNoBG = cor[1]
                self.grupo.atribuirCoNoRotulo(indice, corDoNoBG)
            membro.rotuloCorFG = corDoNoFG
            membro.rotuloCorBG = corDoNoBG

        self.grafoDeCoAutoriaSemPesos = self.criarGrafoDeCoAutoriaSemPesos()
        self.grafoDeCoAutoriaSemPesos.draw(path=diretorioDeSaida + '/grafoDeColaboracoesSemPesos.png', format='png')
        self.grafoDeCoAutoriaSemPesos.draw(path=diretorioDeSaida + '/grafoDeColaboracoesSemPesos.dot', format='dot')
        self.grafoDeCoAutoriaSemPesosCMAPX = self.grafoDeCoAutoriaSemPesos.draw(format='cmapx')

        self.grafoDeCoAutoriaComPesos = self.criarGrafoDeCoAutoriaComPesos()
        self.grafoDeCoAutoriaComPesos.draw(path=diretorioDeSaida + '/grafoDeColaboracoesComPesos.png', format='png')
        self.grafoDeCoAutoriaComPesos.draw(path=diretorioDeSaida + '/grafoDeColaboracoesComPesos.dot', format='dot')
        self.grafoDeCoAutoriaComPesosCMAPX = self.grafoDeCoAutoriaComPesos.draw(format='cmapx')

        '''
        self.grafoDeCoAutoriaNormalizado = self.criarGrafoDeCoAutoriaNormalizada()
        self.grafoDeCoAutoriaNormalizado.draw(path=diretorioDeSaida + '/grafoDeColaboracoesNormalizado.png', format='png')
        self.grafoDeCoAutoriaNormalizado.draw(path=diretorioDeSaida + '/grafoDeColaboracoesNormalizado.dot', format='dot')
        self.grafoDeCoAutoriaNormalizadoCMAPX = self.grafoDeCoAutoriaNormalizado.draw(format='cmapx')
        '''

        # Criamos um thumbnail do grafo sem pesos
        im = Image.open(diretorioDeSaida + '/grafoDeColaboracoesSemPesos.png')
        im.thumbnail((400, 400))
        im.save(diretorioDeSaida + '/grafoDeColaboracoesSemPesos-t.png')

    def criarGrafoDeCoAutoriaSemPesos(self):
        print("\n[CRIANDO GRAFOS DE COLABORACOES SEM PESOS]")

        grafo = pygraphviz.AGraph(directed=False, overlap="False", id="grafo1", name="grafo1")
        grafo.node_attr['shape'] = 'rectangle'
        grafo.node_attr['fontsize'] = '12'
        grafo.node_attr['style'] = 'filled'

        # Inserimos os nos
        for m in range(0, self.grupo.numeroDeMembros()):
            membro = self.grupo.listaDeMembros[m]
            nome = self.abreviarNome(membro.nomeCompleto) + " [" + str(int(self.grupo.vetorDeCoAutoria[m])) + "]"
            if self.grupo.vetorDeCoAutoria[m] > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
                try:
                    grafo.add_node(membro.idMembro, label=nome, fontcolor=membro.rotuloCorFG, color=membro.rotuloCorBG,
                                   height="0.2", URL="membro-" + membro.idLattes + ".html")
                except:
                    grafo.add_node(membro.idMembro, label=nome.encode('utf8'), fontcolor=membro.rotuloCorFG,
                                   color=membro.rotuloCorBG, height="0.2", URL="membro-" + membro.idLattes + ".html")

        # Inserimos as arestas
        for i in range(0, self.grupo.numeroDeMembros() - 1):
            for j in range(i, self.grupo.numeroDeMembros()):
                if self.grupo.matrizDeAdjacencia[i, j] > 0:
                    grafo.add_edge(i, j)

        grafo.layout('dot')  # circo dot neato
        return grafo

    def criarGrafoDeCoAutoriaComPesos(self):
        print("\n[CRIANDO GRAFOS DE COLABORACOES COM PESOS]")

        grafo = pygraphviz.AGraph(directed=False, overlap="False", id="grafo2", name="grafo2")
        grafo.node_attr['shape'] = 'rectangle'
        grafo.node_attr['fontsize'] = '12'
        grafo.node_attr['style'] = 'filled'

        # Inserimos os nos
        for m in range(0, self.grupo.numeroDeMembros()):
            membro = self.grupo.listaDeMembros[m]
            nome = self.abreviarNome(membro.nomeCompleto) + " [" + str(int(self.grupo.vetorDeCoAutoria[m])) + "]"
            if self.grupo.vetorDeCoAutoria[m] > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
                try:
                    grafo.add_node(membro.idMembro, label=nome, fontcolor=membro.rotuloCorFG, color=membro.rotuloCorBG,
                                   height="0.2", URL="membro-" + membro.idLattes + ".html")
                except:
                    grafo.add_node(membro.idMembro, label=nome.encode('utf8'), fontcolor=membro.rotuloCorFG,
                                   color=membro.rotuloCorBG, height="0.2", URL="membro-" + membro.idLattes + ".html")

        # Inserimos as arestas
        for i in range(0, self.grupo.numeroDeMembros() - 1):
            for j in range(i, self.grupo.numeroDeMembros()):
                if self.grupo.matrizDeAdjacencia[i, j] > 0:
                    grafo.add_edge(i, j, label=str(self.grupo.matrizDeAdjacencia[i, j]), fontsize='8')

        grafo.layout('dot')  # circo dot neato
        return grafo

    '''
    def criarGrafoDeCoAutoriaNormalizada(self):
        print "\n[CRIANDO GRAFOS DE COLABORACOES NORMALIZADO]"

        grafo = pygraphviz.AGraph(directed=True, overlap="False", id="grafo3", name="grafo3")
        grafo.node_attr['shape'] = 'rectangle'
        grafo.node_attr['fontsize'] = '8'
        grafo.node_attr['style'] = 'filled'

        # Inserimos os nos: This is SPARTA!!!
        for m in range(0, self.grupo.numeroDeMembros()):
            membro = self.grupo.listaDeMembros[m]
            nome = self.abreviarNome(membro.nomeCompleto) + " [" + str(int(self.grupo.vetorDeCoAutoria[m])) + "]"
            if self.grupo.vetorDeCoAutoria[m] > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
                try:
                    grafo.add_node(membro.idMembro, label=nome, fontcolor=membro.rotuloCorFG, color=membro.rotuloCorBG,
                                   height="0.2", URL="membro-" + membro.idLattes + ".html")
                except:
                    grafo.add_node(membro.idMembro, label=nome.encode('utf8'), fontcolor=membro.rotuloCorFG,
                                   color=membro.rotuloCorBG, height="0.2", URL="membro-" + membro.idLattes + ".html")

        # Inserimos as arestas
        for i in range(0, self.grupo.numeroDeMembros()):
            for j in range(0, self.grupo.numeroDeMembros()):
                valor = round(self.grupo.matrizDeFrequenciaNormalizada[i, j], 2)
                if valor > 0:
                    if self.grupo.obterParametro('grafo-mostrar_aresta_proporcional_ao_numero_de_colaboracoes'):
                        grossura = str(0.5 + 3 * valor)
                    else:
                        grossura = '1'
                    grafo.add_edge(i, j, label=str(valor), fontsize='8', penwidth=grossura, arrowhead='normal',
                                   arrowsize='0.75')

        grafo.layout('dot')  # dot
        return grafo
    '''

    '''
    def criarGrafoDeCoAutoriaCompleta(self):
        print "\n[CRIANDO GRAFOS DE COLABORACOES SEM PESOS - COMPLETA]"

        grafo = pygraphviz.AGraph(strict=False, directed=False, ratio="compress")
        grafo.node_attr['shape'] = 'rectangle'
        grafo.node_attr['fontsize'] = '8'
        grafo.node_attr['style'] = 'filled'

        # Inserimos os nos
        for m in range(0, self.grupo.numeroDeMembros()):
            membro = self.grupo.listaDeMembros[m]
            nome = self.abreviarNome(membro.nomeCompleto).encode('utf8') + " [" + str(
                int(self.grupo.vetorDeCoAutoria[m])) + "]"

            if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
                indice = self.grupo.listaDeRotulos.index(membro.rotulo)
                cor = self.atribuirCorLegal(indice)
                corDoNoFG = cor[0]
                corDoNoBG = cor[1]
                self.grupo.atribuirCoNoRotulo(indice, corDoNoBG)
            else:
                corDoNoFG = '#FFFFFF'
                corDoNoBG = '#003399'

            if self.grupo.vetorDeCoAutoria[m] > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
                grafo.add_node(membro.idMembro, label=nome, fontcolor=corDoNoFG, color=corDoNoBG, height="0.2",
                               URL="membro-" + membro.idLattes + ".html", root='True')

                for idColaborador in membro.listaIDLattesColaboradoresUnica:
                    inserir = 1
                    for mtmp in self.grupo.listaDeMembros:
                        if idColaborador == mtmp.idLattes:
                            inserir = 0

                    if inserir:
                        grafo.add_node(idColaborador, fontcolor='white', color='black', height="0.2", shape="point")
                        grafo.add_edge(idColaborador, membro.idMembro)

        # Inserimos as arestas
        for i in range(0, self.grupo.numeroDeMembros() - 1):
            for j in range(i, self.grupo.numeroDeMembros()):
                if self.grupo.matrizDeFrequenciaNormalizada[i, j] > 0:
                    grafo.add_edge(i, j)

        # grafo.layout('twopi')
        grafo.layout('circo')
        return grafo
    '''

    def atribuirCorLegal(self, indice):
        self.cores = [
            ['#FFFFFF', '#000099'],  # azul
            ['#FFFFFF', '#006600'],  # verde
            ['#FFFFFF', '#990000'],  # vermelho
            ['#FFFFFF', '#FF3300'],  # laranja
            ['#FFFFFF', '#009999'],  # esmeralda legal
            ['#000000', '#FF33CC'],  # pink
            ['#FFFFFF', '#333333'],  # cinza
            ['#000000', '#FFFF00'],  # amarelo
            ['#FFFFFF', '#0033FF'],  # azul eletric
            ['#FFFFFF', '#330000'],  # marrom
            ['#FFFFFF', '#330099'],  # roxo
            ['#000000', '#CC9999'],
            ['#000000', '#FF99CC'],
            ['#000000', '#FFCCFF'],
            ['#000000', '#999933'],
            ['#FFFFFF', '#339966'],
            ['#FFFFFF', '#660033'],
            ['#000000', '#00CC99'],
            ['#000000', '#99FFCC'],  # esmeralda
            ['#FFFFFF', '#330033'],  # roxo escuro
            ['#000000', '#FFFFFF']]

        if indice < len(self.cores):
            return self.cores[indice]
        else:
            return self.cores[-1]

    def abreviarNome(self, nome):
        # No grafo de colaboracoes nomes cumpridos não ajudam na visualização da co-autoria.
        # para tal, precisamos abreviar os nomes.
        # Ex.
        #     'Jesus Pascual Mena Chalco'         -> 'Jesus P. Mena Chalco'
        #     'Aaaaaa BBBBBB da CCCCCCC e DDDDDD' -> 'Aaaaaa B. da CCCCCCC e DDDDDD'
        partes = nome.split(' ')
        if len(partes) >= 4:
            indice = 2
            if len(partes[-2]) <= 3:
                indice = 3
            nomeAbreviado = partes[0]
            for i in range(1, len(partes) - indice):
                if len(partes[i]) >= 3:
                    nomeAbreviado += " " + partes[i][0] + "."
                else:
                    nomeAbreviado += " " + partes[i]
            for i in range(len(partes) - indice, len(partes)):
                nomeAbreviado += " " + partes[i]
        else:
            nomeAbreviado = nome
        return nomeAbreviado
