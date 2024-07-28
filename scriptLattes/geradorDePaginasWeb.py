#!/usr/bin/python
# encoding: utf-8
#
#
# scriptLattes
# http://scriptlattes.sourceforge.net/
#
# Este programa é um software livre; você pode redistribui-lo e/ou
# modifica-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
from collections import defaultdict
import datetime
import os
import re
import unicodedata
from .highcharts import *  # highcharts
from . import membro


class GeradorDePaginasWeb:
    grupo = None
    dir = None
    version = None
    extensaoPagina = None
    arquivoRis = None

    def __init__(self, grupo):
        self.grupo = grupo
        self.version = 'V9'
        self.dir = self.grupo.obterParametro('global-diretorio_de_saida')

        if self.grupo.obterParametro('global-criar_paginas_jsp'):
            self.extensaoPagina = '.jsp'
            self.html1 = '<%@ page language="java" contentType="text/html; charset=ISO8859-1" pageEncoding="ISO8859-1"%> <%@ taglib prefix="f" uri="http://java.sun.com/jsf/core"%> <f:verbatim>'
            self.html2 = '</f:verbatim>'
        else:
            self.extensaoPagina = '.html'
            self.html1 = '<html>'
            self.html2 = '</html>'

        # geracao de arquivo RIS com as publicacoes
        if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
            prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro('global-prefixo') == '' else ''
            self.arquivoRis = open(self.dir + "/" + prefix + "publicacoes.ris", 'w', encoding='utf8')

        self.gerar_pagina_de_membros()
        self.gerar_pagina_de_metricas()
        #self.gerar_pagina_de_producao_qualificado_por_membro()
        self.gerarPaginasDeProducoesBibliograficas()
        self.gerarPaginasDeProducoesTecnicas()
        self.gerarPaginasDeProducoesArtisticas()
        self.gerarPaginasDePatentes()


        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            self.gerarPaginasDeOrientacoes()

        if self.grupo.obterParametro('relatorio-incluir_projeto'):
            self.gerarPaginasDeProjetos()

        if self.grupo.obterParametro('relatorio-incluir_premio'):
            self.gerarPaginasDePremios()

        if self.grupo.obterParametro('relatorio-incluir_participacao_em_evento'):
            self.gerarPaginasDeParticipacaoEmEventos()

        if self.grupo.obterParametro('relatorio-incluir_organizacao_de_evento'):
            self.gerarPaginasDeOrganizacaoDeEventos()

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            self.gerarPaginaDeGrafosDeColaboracoes()

        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            self.gerarPaginasDeInternacionalizacao()

        # final do fim!
        self.gerarPaginaPrincipal()

        if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
            self.arquivoRis.close()


    def gerarPaginaPrincipal(self):
        nomeGrupo = self.grupo.obterParametro('global-nome_do_grupo')

        s = self.html1 + ' \
        <head> \
           <title>' + nomeGrupo + '</title> \
           <meta name="Generator" content="scriptLattes"> \
           <link rel="stylesheet" href="css/scriptLattes.css" type="text/css">  \
           <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"> \
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        #if self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
        #    s += self.grupo.mapaDeGeolocalizacao.mapa  #.encode("utf8")

        s += '</head> \n \
        <body onload="initialize()" onunload="GUnload()"> <div id="header">  \
        <center> <h2> ' + nomeGrupo + '</h2>'

        #| <a href=producao_membros' + self.extensaoPagina + '>Produção qualificado por membro</a> \
        s += '[ <a href=membros' + self.extensaoPagina + '><b>Membros</b></a> \
            | <a href=#producaoBibliografica>Produção bibliográfica</a> \
            | <a href=#producaoTecnica>Produção técnica</a> \
            | <a href=#producaoArtistica>Produção artística</a> '

        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            s += '| <a href=#orientacoes>Orientações</a> '

        if self.grupo.obterParametro('relatorio-incluir_projeto'):
            s += '| <a href=#projetos>Projetos</a> '

        if self.grupo.obterParametro('relatorio-incluir_premio'):
            s += '| <a href=#premios>Prêmios</a> '

        if self.grupo.obterParametro('relatorio-incluir_participacao_em_evento') or self.grupo.obterParametro(
                'relatorio-incluir_organizacao_de_evento'):
            s += '| <a href=#eventos>Eventos</a> '

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '| <a href=#grafo>Grafo de colaborações</a> '

        #if self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
        #    s += '| <a href=#mapa>Mapa de geolocalização</a> '

        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            s += '| <a href=#internacionalizacao>Internacionalização</a> '

        if self.grupo.obterParametro('relatorio-incluir_producao_com_colaboradores'):
            s += '| <a href=producao-com-colaboradores/index' + self.extensaoPagina + '><b>Produção com colaboradores</b></a> '

        if self.grupo.obterParametro('relatorio-incluir_metricas'):
            s += '| <a href=metricas' + self.extensaoPagina + '><b>Métricas</b></a> '

        s += ' ] </center><br></div>'
        s += '<h3 id="producaoBibliografica">Produção bibliográfica</h3> <ul>'

        if self.nPB0 > 0:
            s += '<li> <a href="PB0-0' + self.extensaoPagina + '">Artigos completos publicados em periódicos</a> '+ '(' + str(self.nPB0) + ')'
        if self.nPB1 > 0:
            s += '<li> <a href="PB1-0' + self.extensaoPagina + '">Livros publicados/organizados ou edições</a> '+ '(' + str(self.nPB1) + ')'
        if self.nPB2 > 0:
            s += '<li> <a href="PB2-0' + self.extensaoPagina + '">Capítulos de livros publicados </a> '+ '(' + str(self.nPB2) + ')'
        if self.nPB3 > 0:
            s += '<li> <a href="PB3-0' + self.extensaoPagina + '">Textos em jornais de notícias/revistas </a> '+ '(' + str(self.nPB3) + ')'
        if self.nPB4 > 0:
            s += '<li> <a href="PB4-0' + self.extensaoPagina + '">Trabalhos completos publicados em anais de congressos </a> '+ '(' + str(self.nPB4) + ')'
        if self.nPB5 > 0:
            s += '<li> <a href="PB5-0' + self.extensaoPagina + '">Resumos expandidos publicados em anais de congressos </a> '+ '(' + str(self.nPB5) + ')'
        if self.nPB6 > 0:
            s += '<li> <a href="PB6-0' + self.extensaoPagina + '">Resumos publicados em anais de congressos </a> '+ '(' + str(self.nPB6) + ')'
        if self.nPB7 > 0:
            s += '<li> <a href="PB7-0' + self.extensaoPagina + '">Artigos aceitos para publicação </a> '+ '(' + str(self.nPB7) + ')'
        if self.nPB8 > 0:
            s += '<li> <a href="PB8-0' + self.extensaoPagina + '">Apresentações de trabalho </a> '+ '(' + str(self.nPB8) + ')'
        if self.nPB9 > 0:
            s += '<li> <a href="PB9-0' + self.extensaoPagina + '">Demais tipos de produção bibliográfica </a> '+ '(' + str(self.nPB9) + ')'
        if self.nPB > 0:
            s += '<li> <a href="PB-0' + self.extensaoPagina + '">Total de produção bibliográfica</a> '+ '(' + str(self.nPB) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'

        s += '</ul> <h3 id="producaoTecnica">Produção técnica</h3> <ul>'
        if self.nPT0 > 0:
            s += '<li> <a href="PT0-0' + self.extensaoPagina + '">Programas de computador com registro</a> '+ '(' + str(self.nPT0) + ')'
        if self.nPT1 > 0:
            s += '<li> <a href="PT1-0' + self.extensaoPagina + '">Programas de computador sem registro</a> '+ '(' + str(self.nPT1) + ')'
        if self.nPT2 > 0:
            s += '<li> <a href="PT2-0' + self.extensaoPagina + '">Produtos tecnológicos</a> '+ '(' + str(self.nPT2) + ')'
        if self.nPT3 > 0:
            s += '<li> <a href="PT3-0' + self.extensaoPagina + '">Processos ou técnicas</a> '+ '(' + str(self.nPT3) + ')'
        if self.nPT4 > 0:
            s += '<li> <a href="PT4-0' + self.extensaoPagina + '">Trabalhos técnicos</a> ' + '(' + str(
                self.nPT4) + ')'
        if self.nPT5 > 0:
            s += '<li> <a href="PT5-0' + self.extensaoPagina + '">Demais tipos de produção técnica</a> '+ '(' + str(self.nPT5) + ')'
        if self.nPT > 0:
            s += '<li> <a href="PT-0' + self.extensaoPagina + '">Total de produção técnica</a> '+ '(' + str(self.nPT) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'


            # s+='</ul> <h3 id="patenteRegistro">Patente e Registro</h3> <ul>'
        #if self.nPR0>0:
        #	s+= '<li> <a href="PR0-0'+self.extensaoPagina+'">Patente</a> ''
        # if self.nPR1>0:
        #	s+= '<li> <a href="PR1-0'+self.extensaoPagina+'">Programa de computador</a> ''
        #if self.nPR2>0:
        #	s+= '<li> <a href="PR2-0'+self.extensaoPagina+'">Desenho industrial</a> ''
        #if self.nPR0 == 0 and self.nPR1 == 0 and self.nPR2 == 0:
        #	s+= '<i>Nenhum item achado nos currículos Lattes</i>'


        s += '</ul> <h3 id="producaoArtistica">Produção artística</h3> <ul>'
        if self.nPA > 0:
            s += '<li> <a href="PA-0' + self.extensaoPagina + '">Total de produção artística</a> '+ '(' + str(self.nPA) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'

        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            s += '</ul> <h3 id="orientacoes">Orientações</h3> <ul>'
            s += '<li><b>Orientações em andamento</b>'
            s += '<ul>'
            if self.nOA0 > 0:
                s += '<li> <a href="OA0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '+ '(' + str(self.nOA0) + ')'
            if self.nOA1 > 0:
                s += '<li> <a href="OA1-0' + self.extensaoPagina + '">Tese de doutorado</a> '+ '(' + str(self.nOA1) + ')'
            if self.nOA2 > 0:
                s += '<li> <a href="OA2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '+ '(' + str(self.nOA2) + ')'
            if self.nOA3 > 0:
                s += '<li> <a href="OA3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '+ '(' + str(self.nOA3) + ')'
            if self.nOA4 > 0:
                s += '<li> <a href="OA4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '+ '(' + str(self.nOA4) + ')'
            if self.nOA5 > 0:
                s += '<li> <a href="OA5-0' + self.extensaoPagina + '">Iniciação científica</a> '+ '(' + str(self.nOA5) + ')'
            if self.nOA6 > 0:
                s += '<li> <a href="OA6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '+ '(' + str(self.nOA6) + ')'
            if self.nOA > 0:
                s += '<li> <a href="OA-0' + self.extensaoPagina + '">Total de orientações em andamento</a> '+ '(' + str(self.nOA) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

            s += '<li><b>Supervisões e orientações concluídas</b>'
            s += '<ul>'
            if self.nOC0 > 0:
                s += '<li> <a href="OC0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '+ '(' + str(self.nOC0) + ')'
            if self.nOC1 > 0:
                s += '<li> <a href="OC1-0' + self.extensaoPagina + '">Tese de doutorado</a> '+ '(' + str(self.nOC1) + ')'
            if self.nOC2 > 0:
                s += '<li> <a href="OC2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '+ '(' + str(self.nOC2) + ')'
            if self.nOC3 > 0:
                s += '<li> <a href="OC3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '+ '(' + str(self.nOC3) + ')'
            if self.nOC4 > 0:
                s += '<li> <a href="OC4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '+ '(' + str(self.nOC4) + ')'
            if self.nOC5 > 0:
                s += '<li> <a href="OC5-0' + self.extensaoPagina + '">Iniciação científica</a> '+ '(' + str(self.nOC5) + ')'
            if self.nOC6 > 0:
                s += '<li> <a href="OC6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '+ '(' + str(self.nOC6) + ')'
            if self.nOC > 0:
                s += '<li> <a href="OC-0' + self.extensaoPagina + '">Total de orientações concluídas</a> '+ '(' + str(self.nOC) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_projeto'):
            s += '</ul> <h3 id="projetos">Projetos de pesquisa</h3> <ul>'
            if self.nPj > 0:
                s += '<li> <a href="Pj-0' + self.extensaoPagina + '">Total de projetos de pesquisa</a> '+ '(' + str(self.nPj) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_premio'):
            s += '</ul> <h3 id="premios">Prêmios e títulos</h3> <ul>'
            if self.nPm > 0:
                s += '<li> <a href="Pm-0' + self.extensaoPagina + '">Total de prêmios e títulos</a> '+ '(' + str(self.nPm) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_participacao_em_evento'):
            s += '</ul> <h3 id="eventos">Participação em eventos</h3> <ul>'
            if self.nEp > 0:
                s += '<li> <a href="Ep-0' + self.extensaoPagina + '">Total de participação em eventos</a> '+ '(' + str(self.nEp) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

        if self.grupo.obterParametro('relatorio-incluir_organizacao_de_evento'):
            s += '</ul> <h3 id="eventos">Organização de eventos</h3> <ul>'
            if self.nEo > 0:
                s += '<li> <a href="Eo-0' + self.extensaoPagina + '">Total de organização de eventos</a> '+ '(' + str(self.nEo) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'
            s += '</ul>'

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '</ul> <h3 id="grafo">Grafo de colaborações</h3> <ul>'
            s += '<a href="grafoDeColaboracoes' + self.extensaoPagina + '"><img src="grafoDeColaboracoesSemPesos-t.png" border=1> </a>'
        s += '</ul>'

        '''
        if self.grupo.obterParametro('mapa-mostrar_mapa_de_geolocalizacao'):
            s += '<h3 id="mapa">Mapa de geolocaliza&ccedil;&atilde;o</h3> <br> <div id="map_canvas" style="width: 800px; height: 600px"></div> <br>'
            s += '<b>Legenda</b><table>'
            if self.grupo.obterParametro('mapa-incluir_membros_do_grupo'):
                s += '<tr><td> <img src=lattesPoint0.png></td> <td> Membro (orientador) </td></tr>'
            if self.grupo.obterParametro('mapa-incluir_alunos_de_pos_doutorado'):
                s += '<tr><td> <img src=lattesPoint1.png></td> <td>  Pesquisador com pós-doutorado concluído e ID Lattes cadastrado no currículo do supervisor </td></tr>'            
            if self.grupo.obterParametro('mapa-incluir_alunos_de_doutorado'):
                s += '<tr><td> <img src=lattesPoint2.png></td> <td>  Aluno com doutorado concluído e ID Lattes cadastrado no currículo do orientador </td></tr>'            
            if self.grupo.obterParametro('mapa-incluir_alunos_de_mestrado'):
                s += '<tr><td> <img src=lattesPoint3.png></td> <td>  Aluno com mestrado e ID Lattes cadastrado no currículo do orientador </td></tr>'            
            s += '</table>'
        '''

        '''
        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            s += '</ul> <h3 id="internacionalizacao">Internacionalização</h3> <ul>'
            if self.nIn0 > 0:
                s += '<li> <a href="In0-0' + self.extensaoPagina + '">Coautoria e internacionalização</a> '+ '(' + str(self.nIn0) + ')'
            else:
                s += '<i>Nenhuma publicação com DOI disponível para análise</i>'
            s += '</ul>'
        '''

        s += self.paginaBottom()
        self.salvarPagina("index" + self.extensaoPagina, s)


    def gerarPaginasDeProducoesBibliograficas(self):
        self.nPB0 = 0
        self.nPB1 = 0
        self.nPB2 = 0
        self.nPB3 = 0
        self.nPB4 = 0
        self.nPB5 = 0
        self.nPB6 = 0
        self.nPB7 = 0
        self.nPB8 = 0
        self.nPB9 = 0
        self.nPB = 0

        if self.grupo.obterParametro('relatorio-incluir_artigo_em_periodico'):
            self.nPB0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaArtigoEmPeriodico,
                                                       "Artigos completos publicados em periódicos", "PB0", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_livro_publicado'):
            self.nPB1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaLivroPublicado,
                                                       "Livros publicados/organizados ou edições", "PB1", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_capitulo_de_livro_publicado'):
            self.nPB2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaCapituloDeLivroPublicado,
                                                       "Capítulos de livros publicados", "PB2", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_texto_em_jornal_de_noticia'):
            self.nPB3 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaTextoEmJornalDeNoticia,
                                                       "Textos em jornais de notícias/revistas", "PB3", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_trabalho_completo_em_congresso'):
            self.nPB4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaTrabalhoCompletoEmCongresso,
                                                       "Trabalhos completos publicados em anais de congressos", "PB4",
                                                       ris=True)
        if self.grupo.obterParametro('relatorio-incluir_resumo_expandido_em_congresso'):
            self.nPB5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaResumoExpandidoEmCongresso,
                                                       "Resumos expandidos publicados em anais de congressos", "PB5",
                                                       ris=True)
        if self.grupo.obterParametro('relatorio-incluir_resumo_em_congresso'):
            self.nPB6 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaResumoEmCongresso,
                                                       "Resumos publicados em anais de congressos", "PB6", ris=True)
        if self.grupo.obterParametro('relatorio-incluir_artigo_aceito_para_publicacao'):
            self.nPB7 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaArtigoAceito,
                                                       "Artigos aceitos para publicação", "PB7")
        if self.grupo.obterParametro('relatorio-incluir_apresentacao_de_trabalho'):
            self.nPB8 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaApresentacaoDeTrabalho,
                                                       "Apresentações de trabalho", "PB8")
        if self.grupo.obterParametro('relatorio-incluir_outro_tipo_de_producao_bibliografica'):
            self.nPB9 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOutroTipoDeProducaoBibliografica,
                "Demais tipos de produção bibliográfica", "PB9")
        # Total de produção bibliográfica
        self.nPB = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPB,
                                                  "Total de produção bibliográfica", "PB")


    def gerarPaginasDeProducoesTecnicas(self):
        self.nPT0 = 0
        self.nPT1 = 0
        self.nPT2 = 0
        self.nPT3 = 0
        self.nPT4 = 0
        self.nPT5 = 0
        self.nPT = 0

        if self.grupo.obterParametro('relatorio-incluir_software_com_patente'):
            self.nPT0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaSoftwareComPatente,
                                                       "Softwares com registro de patente", "PT0")
        if self.grupo.obterParametro('relatorio-incluir_software_sem_patente'):
            self.nPT1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaSoftwareSemPatente,
                                                       "Softwares sem registro de patente", "PT1")
        if self.grupo.obterParametro('relatorio-incluir_produto_tecnologico'):
            self.nPT2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProdutoTecnologico,
                                                       "Produtos tecnológicos", "PT2")
        if self.grupo.obterParametro('relatorio-incluir_processo_ou_tecnica'):
            self.nPT3 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProcessoOuTecnica,
                                                       "Processos ou técnicas", "PT3")
        if self.grupo.obterParametro('relatorio-incluir_trabalho_tecnico'):
            self.nPT4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaTrabalhoTecnico,
                                                       "Trabalhos técnicos", "PT4")
        if self.grupo.obterParametro('relatorio-incluir_outro_tipo_de_producao_tecnica'):
            self.nPT5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOutroTipoDeProducaoTecnica,
                                                       "Demais tipos de produção técnica", "PT5")
        # Total de produções técnicas
        self.nPT = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPT, "Total de produção técnica",
                                                  "PT")


    def gerarPaginasDeProducoesArtisticas(self):
        self.nPA0 = 0
        self.nPA = 0

        if self.grupo.obterParametro('relatorio-incluir_producao_artistica'):
            self.nPA0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProducaoArtistica,
                                                       "Produção artística/cultural", "PA0")
        # Total de produções técnicas
        self.nPA = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPA, "Total de produção artística",
                                                  "PA")


    def gerarPaginasDePatentes(self):
        self.nPR0 = 0
        self.nPR1 = 0
        self.nPR2 = 0
        self.nPR = 0

        # if self.grupo.obterParametro('relatorio-incluir_patente'):

        #	self.nPR0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPatente, "Patente", "PR0")
        #	self.nPR1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProgramaComputador, "Programa de computador", "PR1")
        #	self.nPR2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaDesenhoIndustrial, "Desenho industrial", "PR2")

        # Total de produções técnicas

    #self.nPR = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPR, "Total de patentes e registros", "PR")


    def gerarPaginasDeOrientacoes(self):
        self.nOA0 = 0
        self.nOA1 = 0
        self.nOA2 = 0
        self.nOA3 = 0
        self.nOA4 = 0
        self.nOA5 = 0
        self.nOA6 = 0
        self.nOA = 0

        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_pos_doutorado'):
            self.nOA0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOASupervisaoDePosDoutorado,
                                                       "Supervisão de pós-doutorado", "OA0")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_doutorado'):
            self.nOA1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOATeseDeDoutorado,
                                                       "Tese de doutorado", "OA1")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_mestrado'):
            self.nOA2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOADissertacaoDeMestrado,
                                                       "Dissertação de mestrado", "OA2")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_monografia_de_especializacao'):
            self.nOA3 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOAMonografiaDeEspecializacao,
                                                       "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                                                       "OA3")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_tcc'):
            self.nOA4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOATCC,
                                                       "Trabalho de conclusão de curso de graduação", "OA4")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_iniciacao_cientifica'):
            self.nOA5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOAIniciacaoCientifica,
                                                       "Iniciação científica", "OA5")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_em_andamento_outro_tipo'):
            self.nOA6 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOAOutroTipoDeOrientacao,
                                                       "Orientações de outra natureza", "OA6")
        # Total de orientações em andamento
        self.nOA = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOA,
                                                  "Total de orientações em andamento", "OA")

        self.nOC0 = 0
        self.nOC1 = 0
        self.nOC2 = 0
        self.nOC3 = 0
        self.nOC4 = 0
        self.nOC5 = 0
        self.nOC6 = 0
        self.nOC  = 0

        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_pos_doutorado'):
            self.nOC0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCSupervisaoDePosDoutorado,
                                                       "Supervisão de pós-doutorado", "OC0")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_doutorado'):
            self.nOC1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCTeseDeDoutorado,
                                                       "Tese de doutorado", "OC1")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_mestrado'):
            self.nOC2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCDissertacaoDeMestrado,
                                                       "Dissertação de mestrado", "OC2")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_monografia_de_especializacao'):
            self.nOC3 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCMonografiaDeEspecializacao,
                                                       "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                                                       "OC3")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_tcc'):
            self.nOC4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCTCC,
                                                       "Trabalho de conclusão de curso de graduação", "OC4")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_iniciacao_cientifica'):
            self.nOC5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCIniciacaoCientifica,
                                                       "Iniciação científica", "OC5")
        if self.grupo.obterParametro('relatorio-incluir_orientacao_concluida_outro_tipo'):
            self.nOC6 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOCOutroTipoDeOrientacao,
                                                       "Orientações de outra natureza", "OC6")
        # Total de orientações concluídas
        self.nOC = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOC,
                                                  "Total de orientações concluídas", "OC")


    def gerarPaginasDeProjetos(self):
        self.nPj = 0
        self.nPj = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProjetoDePesquisa,
                                                  "Total de projetos de pesquisa", "Pj")


    def gerarPaginasDePremios(self):
        self.nPm = 0
        self.nPm = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPremioOuTitulo,
                                                  "Total de prêmios e títulos", "Pm")

    def gerarPaginasDeParticipacaoEmEventos(self):
        self.nEp = 0
        self.nEp = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaParticipacaoEmEvento,
                                                  "Total de participação em eventos", "Ep")

    def gerarPaginasDeOrganizacaoDeEventos(self):
        self.nEo = 0
        self.nEo = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOrganizacaoDeEvento,
                                                  "Total de organização de eventos", "Eo")

    def gerarPaginasDeInternacionalizacao(self):
        self.nIn0 = 0
        self.nIn0 = self.gerarPaginaDeInternacionalizacao(self.grupo.listaDePublicacoesEinternacionalizacao,
                                                          "Coautoria e internacionalização", "In0")

    @staticmethod
    def arranjar_publicacoes(listaCompleta):
        l = []
        for ano in sorted(list(listaCompleta.keys()), reverse=True):
            publicacoes = sorted(listaCompleta[ano], key=lambda x: x.chave.lower())
            for indice, publicacao in enumerate(publicacoes):
                l.append((ano, indice, publicacao))
        return l

    @staticmethod
    def chunks(lista, tamanho):
        ''' Retorna sucessivos chunks de 'tamanho' a partir da 'lista'
        '''
        for i in range(0, len(lista), tamanho):
            yield lista[i:i + tamanho]

    @staticmethod
    def template_pagina_de_producoes():
        st = '''
                {top}
                {grafico}
                <h3>{titulo}</h3> <br>
                    <div id="container" style="min-width: 310px; max-width: 1920px; height: {height}; margin: 0"></div>
                    Número total de itens: {numero_itens}<br>
                    {totais_qualis}
                    {indice_paginas}
                    {producoes}
                    </table>
                {bottom}
              '''
        return st

    @staticmethod
    def template_producao():
        s = '''
            <tr valign="top"><td>{indice}. &nbsp;</td> <td>{publicacao}</td></tr>
            '''
        return s

    @staticmethod
    def gerar_grafico_de_producoes(listaCompleta, titulo):
        chart = highchart(type=chart_type.column)
        chart.set_y_title('Quantidade')
        # chart.set_x_title(u'Ano')
        # chart.set_x_categories(sorted(listaCompleta.keys()))
        # chart['xAxis']['type'] = 'categories'

        categories = []
        areas_map = {None: 0}
        estrato_area_ano_freq = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for ano, publicacoes in sorted(listaCompleta.items()):
            if ano!=0:
                categories.append(ano)
                for pub in publicacoes:
                    try:
                        #if not pub.qualis:
                        #    logger.debug("qualis is None")
                        estrato_area_ano_freq[None][None][ano] += 1  # sem qualis
                        #else:
                        #    if type(pub.qualis) is str:  # sem area
                        #        logger.debug("publicação com qualis string (sem área): '{}'".format(pub.qualis))
                        #    else:
                        #        for area, estrato in sorted(pub.qualis.items()):
                        #            estrato_area_ano_freq[estrato][area][ano] += 1
                        #            if area not in areas_map:
                        #                areas_map[area] = len(areas_map)
                    except AttributeError:
                        logger.debug("publicação sem atributo qualis")
                        estrato_area_ano_freq[None][None][ano] += 1  # producao que nao tem qualis

        series = []
        if not list(estrato_area_ano_freq.keys()):  # produções vazias
            producoes_vazias = True
            #logger.debug("produções vazias")
        ###elif len(estrato_area_ano_freq.keys()) == 1 and None in estrato_area_ano_freq.keys():  # gráfico normal sem qualis
        else:  # gráfico normal sem qualis
            chart.settitle(titulo)
            chart['plotOptions']['column']['stacking'] = None
            chart['chart']['height'] = 300
            # chart['legend']['title'] = {'text': 'Ano'}
            chart['legend']['enabled'] = jscmd('false')
            chart['xAxis']['type'] = 'category'

            # freq = [estrato_area_ano_freq[None][None][ano] for ano in categories]
            # series.append({'name': u'Total', 'data': freq})
            # chart.set_x_categories(categories)

            data = []
            for ano in categories:
                freq = estrato_area_ano_freq[None][None][ano]
                data.append([ano, freq])
            series.append({'name': 'Total', 'data': data})

            # for ano, pub in sorted(listaCompleta.items()):
            #     series.append({'name': ano, 'data': [len(pub)]}) #, 'y': [len(pub)]})
        '''
        else:  # temos informações sobre qualis
            chart.settitle(u'Publicações por ano agrupadas por área e estrato Qualis')
            chart['chart']['type'] = 'bar'
            chart['chart']['height'] = 1080
            # chart['plotOptions']['column']['stacking'] = 'normal'
            chart['plotOptions']['bar']['stacking'] = 'normal'
            chart['legend']['title'] = {'text': 'Estrato Qualis'}
            chart['legend']['enabled'] = jscmd('true')
            chart['xAxis']['type'] = 'category'
            # chart['yAxis']['stackLabels']['rotation'] = 90
            # chart['yAxis']['stackLabels']['textAlign'] = 'right'

            drilldown_series = []
            for estrato, area_ano_freq in sorted(estrato_area_ano_freq.items()):
                if not estrato:
                    estrato = 'Sem Qualis'
                data = []
                # for area, ano_freq in area_ano_freq.items():
                for area in sorted(areas_map.keys()):
                    ano_freq = area_ano_freq[area]
                    freq = [ano_freq[ano] for ano in categories]
                    if not area:
                        area = u'Sem área'
                    data.append({'name': area, 'y': sum(freq), 'drilldown': area + estrato})

                    drilldown_series.append(
                        {'id': area + estrato, 'name': estrato, 'data': [[ano, ano_freq[ano]] for ano in categories]})
                one_serie = {'name': estrato, 'data': data}  #, 'stack': area}
                series.append(one_serie)
            chart['drilldown'] = {'series': drilldown_series}
        '''
        chart.set_series(series)

        return chart

    def gerar_pagina_de_producoes(self, lista_completa, titulo_pagina, prefixo, ris=False):
        totais_qualis = ""
        if self.grupo.obterParametro('global-identificar_publicacoes_com_qualis'):
            if self.grupo.obterParametro('global-arquivo_qualis_de_periodicos'):  # FIXME: nao está mais sendo usado agora que há qualis online
                if prefixo == 'PB0':
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB0)
                elif prefixo == 'PB7':
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB7)
            if self.grupo.obterParametro('global-arquivo_qualis_de_congressos'):
                if prefixo == 'PB4':
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB4)
                elif prefixo == 'PB5':
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB5)

        total_producoes = sum(len(v) for v in list(lista_completa.values()))

        keys = sorted(list(lista_completa.keys()), reverse=True)
        if keys:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            max_elementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
            #total_paginas = int(math.ceil( total_producoes / (max_elementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)
            total_paginas = total_producoes // max_elementos + (1 if total_producoes % max_elementos != 0 else 0)

            grafico = self.gerar_grafico_de_producoes(lista_completa, titulo_pagina)  # FIXME: é o mesmo gráfico em todas as páginas

            anos_indices_publicacoes = self.arranjar_publicacoes(lista_completa)
            itens_por_pagina = self.chunks(anos_indices_publicacoes, max_elementos)
            for numero_pagina, itens in enumerate(itens_por_pagina):
                producoes_html = ''
                for indice_na_pagina, (ano, indice_no_ano, publicacao) in enumerate(itens):
                    # armazenamos uma copia da publicacao (formato RIS)
                    if ris and self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
                        self.salvarPublicacaoEmFormatoRIS(publicacao)

                    if indice_na_pagina == 0 or indice_no_ano == 0:
                        if indice_na_pagina > 0:
                            producoes_html += '</table></div>'
                        producoes_html += '<div id="dv-year-{0}"><h3 class="year">{0}</h3> <table>'.format(
                            ano if ano else '*itens sem ano')

                    producao_html = self.template_producao()
                    producao_html = producao_html.format(indice=indice_no_ano + 1,
                                                         publicacao=publicacao.html(self.grupo.listaDeMembros))
                    producoes_html += producao_html
                producoes_html += '</table></div>'

                pagina_html = self.template_pagina_de_producoes()
                pagina_html = pagina_html.format(top=self.pagina_top(), bottom=self.paginaBottom(),
                                                 grafico=grafico.html(), height=grafico['chart']['height'],
                                                 titulo=titulo_pagina, numero_itens=str(total_producoes),
                                                 totais_qualis=totais_qualis,
                                                 indice_paginas=self.gerarIndiceDePaginas(total_paginas, numero_pagina,
                                                                                          prefixo),
                                                 producoes=producoes_html)
                self.salvarPagina(prefixo + '-' + str(numero_pagina) + self.extensaoPagina, pagina_html)
        return total_producoes

    def gerarIndiceDePaginas(self, numeroDePaginas, numeroDePaginaAtual, prefixo):
        if numeroDePaginas == 1:
            return ''
        else:
            s = 'Página: '
            for i in range(0, numeroDePaginas):
                if i == numeroDePaginaAtual:
                    s += '<b>' + str(i + 1) + '</b> &nbsp;'
                else:
                    s += '<a href="' + prefixo + '-' + str(i) + self.extensaoPagina + '">' + str(i + 1) + '</a> &nbsp;'
            return '<center>' + s + '</center>'


    def gerarPaginaDeInternacionalizacao(self, listaCompleta, tituloPagina, prefixo):
        numeroTotalDeProducoes = 0
        gInternacionalizacao = GraficoDeInternacionalizacao(listaCompleta)
        htmlCharts = gInternacionalizacao.criarGraficoDeBarrasDeOcorrencias()

        keys = list(listaCompleta.keys())
        keys.sort(reverse=True)
        if len(keys) > 0:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            for ano in keys:
                numeroTotalDeProducoes += len(listaCompleta[ano])

            maxElementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
            #numeroDePaginas = int(math.ceil(numeroTotalDeProducoes / (maxElementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)
            numeroDePaginas = numeroTotalDeProducoes // maxElementos + (1 if numeroTotalDeProducoes % maxElementos != 0 else 0)

            numeroDeItem = 1
            numeroDePaginaAtual = 0
            s = ''

            for ano in keys:
                anoRotulo = str(ano) if not ano == 0 else '*itens sem ano'

                s += '<h3 class="year">' + anoRotulo + '</h3> <table>'

                elementos = listaCompleta[ano]
                elementos.sort(
                    key=lambda x: x.chave.lower())  # Ordenamos a lista em forma ascendente (hard to explain!)

                for index in range(0, len(elementos)):
                    pub = elementos[index]
                    s += '<tr valign="top"><td>' + str(index + 1) + '. &nbsp;</td> <td>' + pub.html() + '</td></tr>'

                    if numeroDeItem % maxElementos == 0 or numeroDeItem == numeroTotalDeProducoes:
                        st = self.pagina_top(cabecalho=htmlCharts)
                        st += '\n<h3>' + tituloPagina + '</h3> <br> <center> <table> <tr> <td valign="top"><div id="barchart_div"></div> </td> <td valign="top"><div id="geochart_div"></div> </td> </tr> </table> </center>'
                        st += '<table>'
                        st += '<tr><td>Número total de publicações realizadas SEM parceria com estrangeiros:</td><td>' + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasSemParceirasComEstrangeiros()) + '</td><td><i>(publicações realizadas só por pesquisadores brasileiros)</i></td></tr>'                       
                        st += '<tr><td>Número total de publicações realizadas COM parceria com estrangeiros:</td><td>' + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasComParceirasComEstrangeiros()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com parcerias NÂO identificadas:</td><td>' + str(
                            gInternacionalizacao.numeroDePublicacoesComParceriasNaoIdentificadas()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com DOI cadastrado:</td><td><b>' + str(numeroTotalDeProducoes) + '</b></td><td></td></tr>'
                        st += '</table>'
                        st += '<br> <font color="red">(*) A estimativa de "coautoria e internacionalização" é baseada na análise automática dos DOIs das publicações cadastradas nos CVs Lattes. A identificação de países, para cada publicação, é feita através de buscas simples de nomes de países.</font><br><p>'
                        st += self.gerarIndiceDePaginas(numeroDePaginas, numeroDePaginaAtual, prefixo)
                        st += s  #
                        st += '</table>'
                        st += self.paginaBottom()

                        self.salvarPagina(prefixo + '-' + str(numeroDePaginaAtual) + self.extensaoPagina, st)
                        numeroDePaginaAtual += 1

                        if (index + 1) < len(elementos):
                            s = '<h3 class="year">' + anoRotulo + '</h3> <table>'
                        else:
                            s = ''
                    numeroDeItem += 1

                s += '</table>'
        return numeroTotalDeProducoes


    def gerarPaginaDeGrafosDeColaboracoes(self):
        lista = ''
        if self.grupo.obterParametro('grafo-incluir_artigo_em_periodico'):
            lista += 'Artigos completos publicados em periódicos, '
        if self.grupo.obterParametro('grafo-incluir_livro_publicado'):
            lista += 'Livros publicados/organizados ou edições, '
        if self.grupo.obterParametro('grafo-incluir_capitulo_de_livro_publicado'):
            lista += 'Capítulos de livros publicados, '
        if self.grupo.obterParametro('grafo-incluir_texto_em_jornal_de_noticia'):
            lista += 'Textos em jornais de notícias/revistas, '
        if self.grupo.obterParametro('grafo-incluir_trabalho_completo_em_congresso'):
            lista += 'Trabalhos completos publicados em anais de congressos, '
        if self.grupo.obterParametro('grafo-incluir_resumo_expandido_em_congresso'):
            lista += 'Resumos expandidos publicados em anais de congressos, '
        if self.grupo.obterParametro('grafo-incluir_resumo_em_congresso'):
            lista += 'Resumos publicados em anais de congressos, '
        if self.grupo.obterParametro('grafo-incluir_artigo_aceito_para_publicacao'):
            lista += 'Artigos aceitos para publicação, '
        if self.grupo.obterParametro('grafo-incluir_apresentacao_de_trabalho'):
            lista += 'Apresentações de trabalho, '
        if self.grupo.obterParametro('grafo-incluir_outro_tipo_de_producao_bibliografica'):
            lista += 'Demais tipos de produção bibliográfica, '

        lista = lista.strip().strip(",")

        s = self.pagina_top()
        s += '\n<h3>Grafo de colabora&ccedil;&otilde;es</h3> \
        <a href=membros' + self.extensaoPagina + '>' + str(self.grupo.numeroDeMembros()) + ' curriculos Lattes</a> foram considerados, \
        gerando os seguintes grafos de colabora&ccedil;&otilde;es encontradas com base nas produ&ccedil;&otilde;es: <i>' + lista + '</i>. <br><p>'

        prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro(
            'global-prefixo') == '' else ''
        # s+='Veja <a href="grafoDeColaboracoesInterativo'+self.extensaoPagina+'?entradaScriptLattes=./'+prefix+'matrizDeAdjacencia.xml">na seguinte página</a> uma versão interativa do grafo de colabora&ccedil;&otilde;es.<br><p><br><p>'

        s += '\nClique no nome dentro do vértice para visualizar o currículo Lattes. Para cada nó: o valor entre colchetes indica o número \
        de produ&ccedil;&otilde;es feitas em colabora&ccedil;&atilde;o apenas com os outros membros do próprio grupo. <br>'

        if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
            s += 'As cores representam os seguintes rótulos: '
            for i in range(0, len(self.grupo.listaDeRotulos)):
                rot = self.grupo.listaDeRotulos[i]
                cor = self.grupo.listaDeRotulosCores[i]
                if rot == '':
                    rot = '[Sem rótulo]'
                s += '<span style="background-color:' + cor + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>' + rot + ' '
        s += '\
        <ul> \
        <li><b>Grafo de colabora&ccedil;&otilde;es sem pesos</b><br> \
            <img src=grafoDeColaboracoesSemPesos.png border=1 ISMAP USEMAP="#grafo1"> <br><p> \
        <li><b>Grafo de colabora&ccedil;&otilde;es com pesos</b><br> \
            <img src=grafoDeColaboracoesComPesos.png border=1 ISMAP USEMAP="#grafo2"> <br><p> \
        </ul>'

        cmapx1 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaSemPesosCMAPX
        cmapx2 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaComPesosCMAPX
        s += '<map id="grafo1" name="grafo1">' + cmapx1.decode() + '\n</map>\n'
        s += '<map id="grafo2" name="grafo2">' + cmapx2.decode() + '\n</map>\n'

        if self.grupo.obterParametro('grafo-incluir_grau_de_colaboracao'):
            s += '<br><p><h3>Grau de colaboração</h3> \
                O grau de colaboração (<i>Collaboration Rank</i>) é um valor numérico que indica o impacto de um membro no grafo de colaborações.\
                <br>Esta medida é similar ao <i>PageRank</i> para grafos direcionais (com pesos).<br><p>'

            ranks, autores, rotulos = list(zip(
                *sorted(zip(self.grupo.vectorRank, self.grupo.nomes, self.grupo.rotulos), reverse=True)))

            s += '<table border=1><tr> <td><i><b>Collaboration Rank</b></i></td> <td><b>Membro</b></td> </tr>'
            for i in range(0, len(ranks)):
                s += '<tr><td>' + str(round(ranks[i], 2)) + '</td><td>' + autores[i] + '</td></tr>'
            s += '</table> <br><p>'

            if self.grupo.obterParametro('grafo-considerar_rotulos_dos_membros_do_grupo'):
                for i in range(0, len(self.grupo.listaDeRotulos)):
                    somaAuthorRank = 0

                    rot = self.grupo.listaDeRotulos[i]
                    cor = self.grupo.listaDeRotulosCores[i]
                    s += '<b><span style="background-color:' + cor + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>' + rot + '</b><br>'

                    s += '<table border=1><tr> <td><i><b>AuthorRank</b></i></td> <td><b>Membro</b></td> </tr>'
                    for i in range(0, len(ranks)):
                        if rotulos[i] == rot:
                            s += '<tr><td>' + str(round(ranks[i], 2)) + '</td><td>' + autores[i] + '</td></tr>'
                            somaAuthorRank += ranks[i]
                    s += '</table> <br> Total: ' + str(round(somaAuthorRank, 2)) + '<br><p>'

        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoes" + self.extensaoPagina, s)

        # grafo interativo
        s = self.pagina_top()
        s += '<applet code=MyGraph.class width=1280 height=800 archive="http://www.vision.ime.usp.br/creativision/graphview/graphview.jar,http://www.vision.ime.usp.br/creativision/graphview/prefuse.jar"></applet></body></html>'
        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoesInterativo" + self.extensaoPagina, s)

    @staticmethod
    def producao_qualis(elemento, membro):
        tabela_template = "<table style=\"width: 100%; display: block; overflow-x: auto;\"><tbody>" \
                          "<br><span style=\"font-size:14px;\"><b>Totais de publicações com Qualis:</b></span><br><br>" \
                          "<div style=\"width:100%; overflow-x:scroll;\">{body}</div>" \
                          "</tbody></table>"

        first_column_template = '<div style="float:left; width:200px; height: auto; border: 1px solid black; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                                ' background:#CCC; vertical-align: middle; padding: 4px 0; {extra_style}"><b>{header}</b></div>'
        header_template = '<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                          ' background:#CCC; text-align: center; vertical-align: middle; padding: 4px 0;"><b>{header}</b></div>'
        line_template = '<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                        ' background:#EAEAEA; text-align: center; vertical-align: middle; padding: 4px 0;">{value}</div>'  # padding:4px 6px;

        cell_size = 40
        num_estratos = len(membro.tabela_qualis['estrato'].unique())

        header_ano = first_column_template.format(header='Ano', extra_style='text-align: center;')
        header_estrato = first_column_template.format(header='Área \\ Estrato', extra_style='text-align: center;')

        for ano in sorted(membro.tabela_qualis['ano'].unique()):
            header_ano += header_template.format(header=ano, width=num_estratos * (cell_size + 1) - 1)
            for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                header_estrato += header_template.format(header=estrato, width=cell_size)

        if membro.tabela_qualis and not membro.tabela_qualis.empty():
            pt = membro.tabela_qualis.pivot_table(columns=['area', 'ano', 'estrato'], values='freq')
        lines = ''
        for area in sorted(membro.tabela_qualis['area'].unique()):
            lines += first_column_template.format(header=area, extra_style='')
            for ano in sorted(membro.tabela_qualis['ano'].unique()):
                for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                    try:
                        lines += line_template.format(value=pt.ix[area, ano, estrato], width=cell_size)
                    except IndexingError:
                        lines += line_template.format(value='&nbsp;', width=cell_size)
            lines += '<div style="clear:both"></div>'

        tabela_body = header_ano
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += header_estrato
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += lines

        tabela = tabela_template.format(body=tabela_body)

        # first = True
        # # FIXME: considerar as áreas
        # for ano in sorted(membro.tabela_qualis['ano'].unique()):
        #     if first:
        #         first = False
        #         display = "block"
        #     else:
        #         display = "none"
        #
        #     # esquerda = '<a class="ano_esquerda" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # direita = '<a class="ano_direita" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # tabela += '<div id="ano_{ano}_{elemento}" style="display: {display}">{esquerda}<b>{ano}</b>{direita}<br/><br/>'.format(
        #     #           ano=ano, elemento=elemento, display=display, esquerda=esquerda, direita=direita)
        #     chaves = ''
        #     valores = ''
        #
        #     for tipo, frequencia in membro.tabelaQualisDosAnos[ano].items():
        #         # FIXME: terminar de refatorar
        #         if tipo == "Qualis nao identificado":
        #             tipo = '<span title="Qualis nao identificado">QNI</span>'
        #
        #         chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #             tipo) + '</b></div>'
        #         valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #             frequencia) + '</div>'
        #
        #     tabela += '<div>' + chaves + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += '<div>' + valores + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += "<br><br></div>"
        # tabTipo += '<div>'
        # chaves = ''
        # valores = ''
        # for chave, valor in membro.tabelaQualisDosTipos.items():
        #
        #     if (chave == "Qualis nao identificado"):
        #         chave = "QNI"
        #
        #     chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #         chave) + '</b></div>'
        #     valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #         valor) + '</div>'
        # tabTipo += '<div>' + chaves + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += '<div>' + valores + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += "<br><br></div><br><br>"
        return tabela

    def gerar_pagina_de_membros(self):
        s = self.pagina_top()
        #s += u'\n<h3>Lista de membros</h3> <table id="membros" class="collapse-box" ><tr>\
        s += '\n<h3>Lista de membros</h3> <table id="membros" class="sortable" ><tr>\
                <th></th>\
                <th></th>\
                <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                <th><b><font size=-1>Grande área</font><b></th>\
                <th><b><font size=-1>Área</font><b></th>\
                <th><b><font size=-1>Instituição</font><b></th>\
                </tr>'
        
        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento    += 1
            bolsa        = membro.bolsaProdutividade  if membro.bolsaProdutividade else ''
            rotulo       = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
            rotulo       = rotulo
            nomeCompleto = membro.nomeCompleto #unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

            self.gerar_pagina_individual_de_membro(membro)

            #print " "
            #nomeCompleto = membro.nomeCompleto
            #print nomeCompleto
            #print type(nomeCompleto)
            #print " --------------------------------------------"
            #nomeCompleto = membro.nomeCompleto

            # html_qualis = self.producao_qualis(elemento, membro)
            ##         <td valign="center" height="40px">' + str(elemento) + '.</td> \
            ##        <td valign="top" height="40px"><img src="' + membro.foto + '" width="40px"></td> \

            s += '\n<tr class="testetabela"> \
                     <td valign="center">{0}.</td> \
                     <td><a href="membro-{1}.html"> {2}</a></td> \
                     <td><font size=-2>{3}</font></td> \
                     <td><font size=-2>{4}</font></td> \
                     <td><font size=-2>{5}</font></td> \
                     <td><font size=-2>{6}</font></td> \
                     <td><font size=-2>{7}</font></td> \
                     <td><font size=-2>{8}</font></td> \
                     <td><font size=-2>{9}</font></td> \
                 </tr>'.format(str(elemento),
                         membro.idLattes,
                         nomeCompleto,
                         rotulo,
                         bolsa,
                         membro.periodo,
                         membro.atualizacaoCV,
                         membro.nomePrimeiraGrandeArea,
                         membro.nomePrimeiraArea,
                         membro.instituicao)

            # <td class="centered"><font size=-1>' + u'Produção com Qualis' + '</font></td> \

            # s += '<tr><td colspan="9"> \
            #      ' + html_qualis + ' \
            #      </td></tr>'

        s += '\n</table>'

        #add jquery and plugins
        # s += '<script src="../../js/jexpand/jExpand.js"></script>' \
        #      '<script>' \
        #      '  $(document).ready(function(){' \
        #      '    $(".collapse-box").jExpand();' \
        #      '  });' \
        #      '</script>'

        s += '<script>' \
             '  $(document).ready( function () {' \
             '    $(\'#membros\').DataTable();' \
             '  });' \
             '</script>'


        # $(".ano_esquerda").live("click", function(e){\
        #     var anoAtual = parseInt($(this).attr("rel"));\
        #     var contador = $(this).attr("rev");\
        #     if(anoAtual > ' + str(anoInicio) + '){\
        #         $("#ano_"+anoAtual+"_"+contador).css("display", "none");\
        #         $("#ano_"+(anoAtual-1)+"_"+contador).css("display", "block");\
        #     }\
        # });\
        # $(".ano_direita").live("click", function(e){\
        #     var anoAtual = parseInt($(this).attr("rel"));\
        #     var contador = $(this).attr("rev");\
        #     if(anoAtual < ' + str(anoFim) + '){\
        #         $("#ano_"+anoAtual+"_"+contador).css("display", "none");\
        #         $("#ano_"+(anoAtual+1)+"_"+contador).css("display", "block");\
        #     }\
        # });\

        s += self.paginaBottom()

        self.salvarPagina("membros" + self.extensaoPagina, s)

    def gerar_pagina_de_metricas(self):
        s = self.pagina_top()

        s += '\n<h3>Métricas: Produções bibliográficas, técnicas e artísticas</h3> <table id="metricas" class="sortable" border=1><tr>\
                <th></th>\
                <th></th>\
                <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                <th><b><font size=-1>Grande área</font><b></th>\
                <th><b><font size=-1>Área</font><b></th>\
                <th><b><font size=-1>lat</font><b></th>\
                <th><b><font size=-1>lon</font><b></th>\
        <th><b><font size=-1>Produção<br>bibliográfica</font><b></th>\
        <th><b><font size=-1>Periódicos</font><b></th>\
        <th><b><font size=-1>Livros</font><b></th>\
        <th><b><font size=-1>Capítulos</font><b></th>\
        <th><b><font size=-1>Congressos</font><b></th>\
        <th><b><font size=-1>Resumos</font><b></th>\
        <th><b><font size=-1>Aceitos</font><b></th>\
        <th><b><font size=-1>Produção<br>técnica</font><b></th>\
        <th><b><font size=-1>Produção<br>artística</font><b></th>\
        </tr>'

        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento += 1
            bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
            rotulo = rotulo
            nomeCompleto = membro.nomeCompleto  #nicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

            quantitativo_publicacoes = [len(membro.listaArtigoEmPeriodico),
                                        len(membro.listaLivroPublicado),
                                        len(membro.listaCapituloDeLivroPublicado),
                                        len(membro.listaTrabalhoCompletoEmCongresso),
                                        len(membro.listaResumoEmCongresso) + len(membro.listaResumoExpandidoEmCongresso),
                                        len(membro.listaArtigoAceito) ]

            quantitativo_tecnica     = [len(membro.listaSoftwareComPatente),
                                        len(membro.listaSoftwareSemPatente),
                                        len(membro.listaProdutoTecnologico),
                                        len(membro.listaProcessoOuTecnica),
                                        len(membro.listaTrabalhoTecnico),
                                        len(membro.listaOutroTipoDeProducaoTecnica) ]

            quantitativo_artistica   = [len(membro.listaProducaoArtistica)]


            s += '\n<tr class="testetabela"> \
                     <td valign="center">{0}.</td> \
                     <td><a href="membro-{1}.html"> {2}</a></td> \
                     <td><font size=-2>{3}</font></td> \
                     <td><font size=-2>{4}</font></td> \
                     <td><font size=-2>{5}</font></td> \
                     <td><font size=-2>{6}</font></td> \
                     <td><font size=-2>{7}</font></td> \
                     <td><font size=-2>{8}</font></td> \
                     <td><font size=-2>{9}</font></td> \
                     <td><font size=-2>{10}</font></td> \
                     <td align="right"><font size=-2>{11}</font></td> \
                     <td align="right"><font size=-2>{12}</font></td> \
                     <td align="right"><font size=-2>{13}</font></td> \
                     <td align="right"><font size=-2>{14}</font></td> \
                     <td align="right"><font size=-2>{15}</font></td> \
                     <td align="right"><font size=-2>{16}</font></td> \
                     <td align="right"><font size=-2>{17}</font></td> \
                     <td align="right"><font size=-2>{18}</font></td> \
                     <td align="right"><font size=-2>{19}</font></td> \
                     </tr>'.format(str(elemento),
                               membro.idLattes,
                               nomeCompleto,
                                 rotulo,
                                 bolsa,
                                 membro.periodo,
                                 membro.atualizacaoCV,
                                 membro.nomePrimeiraGrandeArea,
                                 membro.nomePrimeiraArea,
                                 membro.enderecoProfissionalLat,
                                 membro.enderecoProfissionalLon,
                               sum(quantitativo_publicacoes),
                               quantitativo_publicacoes[0],
                               quantitativo_publicacoes[1],
                               quantitativo_publicacoes[2],
                               quantitativo_publicacoes[3],
                               quantitativo_publicacoes[4],
                               quantitativo_publicacoes[5],
                               sum(quantitativo_tecnica),
                               sum(quantitativo_artistica)  )

        s += '\n</table>'

        s += '\n<h3>Métricas: Orientações concluídas e em andamento</h3> <table id="metricas" class="sortable" border=1><tr>\
                        <th></th>\
                        <th></th>\
                        <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                        <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                        <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                        <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                        <th><b><font size=-1>Grande área</font><b></th>\
                        <th><b><font size=-1>Área</font><b></th>\
        <th><b><font size=-1>Orientações<br>concluídas</font><b></th>\
        <th><b><font size=-1>Posdoc</font><b></th>\
        <th><b><font size=-1>Doutorado</font><b></th>\
        <th><b><font size=-1>Mestrado</font><b></th>\
        <th><b><font size=-1>Especialização</font><b></th>\
        <th><b><font size=-1>TCC</font><b></th>\
        <th><b><font size=-1>IC</font><b></th>\
        <th><b><font size=-1>Orientações<br>em andamento</font><b></th>\
        <th><b><font size=-1>Posdoc</font><b></th>\
        <th><b><font size=-1>Doutorado</font><b></th>\
        <th><b><font size=-1>Mestrado</font><b></th>\
        <th><b><font size=-1>Especialização</font><b></th>\
        <th><b><font size=-1>TCC</font><b></th>\
        <th><b><font size=-1>IC</font><b></th>\
        </tr>'

        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento += 1
            bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
            rotulo = rotulo
            nomeCompleto = membro.nomeCompleto  #unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

            quantitativo_orientacoes_concluidas = [len(membro.listaOCSupervisaoDePosDoutorado),
                                                   len(membro.listaOCTeseDeDoutorado),
                                                   len(membro.listaOCDissertacaoDeMestrado),
                                                   len(membro.listaOCMonografiaDeEspecializacao),
                                                   len(membro.listaOCTCC),
                                                   len(membro.listaOCIniciacaoCientifica)]

            quantitativo_orientacoes_andamento = [len(membro.listaOASupervisaoDePosDoutorado),
                                                  len(membro.listaOATeseDeDoutorado),
                                                  len(membro.listaOADissertacaoDeMestrado),
                                                  len(membro.listaOAMonografiaDeEspecializacao),
                                                  len(membro.listaOATCC),
                                                  len(membro.listaOAIniciacaoCientifica)]

            s += '\n<tr class="testetabela"> \
                      <td valign="center">{0}.</td> \
                      <td><a href="membro-{1}.html"> {2}</a></td> \
                      <td><font size=-2>{3}</font></td> \
                      <td><font size=-2>{4}</font></td> \
                      <td><font size=-2>{5}</font></td> \
                      <td><font size=-2>{6}</font></td> \
                      <td><font size=-2>{7}</font></td> \
                      <td><font size=-2>{8}</font></td> \
                      <td><font size=-2>{9}</font></td> \
                      <td><font size=-2>{10}</font></td> \
                      <td align="right"><font size=-2>{11}</font></td> \
                      <td align="right"><font size=-2>{12}</font></td> \
                      <td align="right"><font size=-2>{13}</font></td> \
                      <td align="right"><font size=-2>{14}</font></td> \
                      <td align="right"><font size=-2>{15}</font></td> \
                      <td align="right"><font size=-2>{16}</font></td> \
                      <td align="right"><font size=-2>{17}</font></td> \
                      <td align="right"><font size=-2>{18}</font></td> \
                      <td align="right"><font size=-2>{19}</font></td> \
                      <td align="right"><font size=-2>{20}</font></td> \
                      <td align="right"><font size=-2>{21}</font></td> \
                      <td align="right"><font size=-2>{22}</font></td> \
                      </tr>'.format(str(elemento),
                                    membro.idLattes,
                                    nomeCompleto,
                                    rotulo,
                                    bolsa,
                                    membro.periodo,
                                    membro.atualizacaoCV,
                                    membro.nomePrimeiraGrandeArea,
                                    membro.nomePrimeiraArea,
                                    sum(quantitativo_orientacoes_concluidas),
                                    quantitativo_orientacoes_concluidas[0],
                                    quantitativo_orientacoes_concluidas[1],
                                    quantitativo_orientacoes_concluidas[2],
                                    quantitativo_orientacoes_concluidas[3],
                                    quantitativo_orientacoes_concluidas[4],
                                    quantitativo_orientacoes_concluidas[5],
                                    sum(quantitativo_orientacoes_andamento),
                                    quantitativo_orientacoes_andamento[0],
                                    quantitativo_orientacoes_andamento[1],
                                    quantitativo_orientacoes_andamento[2],
                                    quantitativo_orientacoes_andamento[3],
                                    quantitativo_orientacoes_andamento[4],
                                    quantitativo_orientacoes_andamento[5],
                                    )

        s += '\n</table>'


        s += '\n<h3>Métricas: Projetos, prêmios e eventos</h3> <table id="metricas" class="sortable" border=1><tr>\
                        <th></th>\
                        <th></th>\
                        <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                        <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                        <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                        <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                        <th><b><font size=-1>Grande área</font><b></th>\
                        <th><b><font size=-1>Área</font><b></th>\
        <th><b><font size=-1>Projetos</font><b></th>\
        <th><b><font size=-1>Prêmios</font><b></th>\
        <th><b><font size=-1>Participação em eventos</font><b></th>\
        <th><b><font size=-1>Organização de eventos</font><b></th>\
        </tr>'

        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento += 1
            bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
            rotulo = rotulo
            nomeCompleto = membro.nomeCompleto #unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

            s += '\n<tr class="testetabela"> \
                      <td valign="center">{0}.</td> \
                      <td><a href="membro-{1}.html"> {2}</a></td> \
                      <td><font size=-2>{3}</font></td> \
                      <td><font size=-2>{4}</font></td> \
                      <td><font size=-2>{5}</font></td> \
                      <td><font size=-2>{6}</font></td> \
                      <td><font size=-2>{7}</font></td> \
                      <td><font size=-2>{8}</font></td> \
                      <td><font size=-2>{9}</font></td> \
                      <td><font size=-2>{10}</font></td> \
                      <td align="right"><font size=-2>{11}</font></td> \
                      <td align="right"><font size=-2>{12}</font></td> \
                      </tr>'.format(str(elemento),
                                    membro.idLattes,
                                    nomeCompleto,
                                    rotulo,
                                    bolsa,
                                    membro.periodo,
                                    membro.atualizacaoCV,
                                    membro.nomePrimeiraGrandeArea,
                                    membro.nomePrimeiraArea,
                                    len(membro.listaProjetoDePesquisa),
                                    len(membro.listaPremioOuTitulo),
                                    len(membro.listaParticipacaoEmEvento),
                                    len(membro.listaOrganizacaoDeEvento)
                                    )

        s += '\n</table>'

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '\n<h3>Métricas: Coautoria</h3> <table id="metricas" class="sortable" border=1><tr>\
                            <th></th>\
                            <th></th>\
                            <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                            <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                            <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                            <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                            <th><b><font size=-1>Grande área</font><b></th>\
                            <th><b><font size=-1>Área</font><b></th>\
            <th><b><font size=-1>IDs Lattes identificados</font><b></th>\
            <th><b><font size=-1>Número de coautores - endôgeno</font><b></th>\
            <th><b><font size=-1>Número de coautores - Publicações bibliográficas</font><b></th>\
            </tr>'

            elemento = 0
            for membro in self.grupo.listaDeMembros:
                elemento += 1
                bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
                rotulo = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
                rotulo = rotulo
                nomeCompleto = membro.nomeCompleto #unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

                coautores_do_membro = list([])
                alias_do_membro = membro.nomeEmCitacoesBibliograficas.upper().replace(".","").split(";")
                for i in range(0,len(alias_do_membro)):
                    alias_do_membro[i] = alias_do_membro[i].strip()

                for tipo_de_publicacao in [membro.listaArtigoEmPeriodico,
                                           membro.listaLivroPublicado,
                                           membro.listaCapituloDeLivroPublicado,
                                           membro.listaTrabalhoCompletoEmCongresso,
                                           membro.listaResumoEmCongresso,
                                           membro.listaResumoExpandidoEmCongresso,
                                           membro.listaArtigoAceito]:
                    for pub in tipo_de_publicacao:

                        for coautor in pub.autores.upper().replace(".","").split(";"):
                            coautor = coautor.strip()
                            if not coautor in alias_do_membro:
                                coautores_do_membro.append(coautor)

                    '''quantitativo_tecnica = [len(membro.listaSoftwareComPatente),
                                            len(membro.listaSoftwareSemPatente),
                                            len(membro.listaProdutoTecnologico),
                                            len(membro.listaProcessoOuTecnica),
                                            len(membro.listaTrabalhoTecnico),
                                            len(membro.listaOutroTipoDeProducaoTecnica)]

                    quantitativo_artistica = [len(membro.listaProducaoArtistica)]
                    '''


                s += '\n<tr class="testetabela"> \
                          <td valign="center">{0}.</td> \
                          <td><a href="membro-{1}.html"> {2}</a></td> \
                          <td><font size=-2>{3}</font></td> \
                          <td><font size=-2>{4}</font></td> \
                          <td><font size=-2>{5}</font></td> \
                          <td><font size=-2>{6}</font></td> \
                          <td><font size=-2>{7}</font></td> \
                          <td><font size=-2>{8}</font></td> \
                          <td><font size=-2>{9}</font></td> \
                          <td><font size=-2>{10}</font></td> \
                          <td align="right"><font size=-2>{11}</font></td> \
                          </tr>'.format(str(elemento),
                                        membro.idLattes,
                                        nomeCompleto,
                                        rotulo,
                                        bolsa,
                                        membro.periodo,
                                        membro.atualizacaoCV,
                                        membro.nomePrimeiraGrandeArea,
                                        membro.nomePrimeiraArea,
                                        len(membro.listaIDLattesColaboradoresUnica),
                                        len(self.grupo.colaboradores_endogenos[membro.idMembro]),
                                        len(set(coautores_do_membro))
                                        )

            s += '\n</table>'


        # add jquery and plugins
        # s += '<script src="../../js/jexpand/jExpand.js"></script>' \
        #      '<script>' \
        #      '  $(document).ready(function(){' \
        #      '    $(".collapse-box").jExpand();' \
        #      '  });' \
        #      '</script>'

        s += '<script>' \
             '  $(document).ready( function () {' \
             '    $(\'#membros\').DataTable();' \
             '  });' \
             '</script>'

        # $(".ano_esquerda").live("click", function(e){\
        #     var anoAtual = parseInt($(this).attr("rel"));\
        #     var contador = $(this).attr("rev");\
        #     if(anoAtual > ' + str(anoInicio) + '){\
        #         $("#ano_"+anoAtual+"_"+contador).css("display", "none");\
        #         $("#ano_"+(anoAtual-1)+"_"+contador).css("display", "block");\
        #     }\
        # });\
        # $(".ano_direita").live("click", function(e){\
        #     var anoAtual = parseInt($(this).attr("rel"));\
        #     var contador = $(this).attr("rev");\
        #     if(anoAtual < ' + str(anoFim) + '){\
        #         $("#ano_"+anoAtual+"_"+contador).css("display", "none");\
        #         $("#ano_"+(anoAtual+1)+"_"+contador).css("display", "block");\
        #     }\
        # });\

        s += self.paginaBottom()

        self.salvarPagina("metricas" + self.extensaoPagina, s)


    def gerar_pagina_individual_de_membro(self, membro):
        bolsa        = membro.bolsaProdutividade  if membro.bolsaProdutividade else ''
        rotulo       = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
        rotulo       = rotulo
        nomeCompleto = membro.nomeCompleto #unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

        s = self.pagina_top()
        s += '\n<h3>{0}</h3>\
                {7}<br><p>\
                <table border=0>\
                <tr><td>\
                    <img height=130px src={2}>\
                </td><td>\
                    <ul>\
                    <li> <a href="{1}">{1}</a> ({3}) </li>\
                    <li> <b>Rótulo/Grupo:</b> {4}</li>\
                    <li> <b>Bolsa CNPq:</b> {5}</li>\
                    <li> <b>Período de análise:</b> {6}</li>\
                    <li> <b>Endereço:</b> {8}</li>\
                    <li> <b>Grande área:</b> {9}</li>\
                    <li> <b>Área:</b> {10}</li>\
                    <li> <b>Citações:</b> <a href="http://scholar.google.com.br/citations?view_op=search_authors&mauthors={0}">Google Acadêmico</a> </li>\
                    </ul>\
                </td><tr>\
                </table><br>'.format(nomeCompleto,
                        membro.url,
                        membro.foto,
                        membro.atualizacaoCV,
                        rotulo,
                        bolsa,
                        membro.periodo,
                        membro.textoResumo,
                        membro.enderecoProfissional,
                        membro.nomePrimeiraGrandeArea,
                        membro.nomePrimeiraArea)

        (nPB0, lista_PB0, titulo_PB0) = self.gerar_lista_de_producoes_de_membro( membro.listaArtigoEmPeriodico, "Artigos completos publicados em periódicos" )
        (nPB1, lista_PB1, titulo_PB1) = self.gerar_lista_de_producoes_de_membro( membro.listaLivroPublicado, "Livros publicados/organizados ou edições" )
        (nPB2, lista_PB2, titulo_PB2) = self.gerar_lista_de_producoes_de_membro( membro.listaCapituloDeLivroPublicado, "Capítulos de livros publicados" )
        (nPB3, lista_PB3, titulo_PB3) = self.gerar_lista_de_producoes_de_membro( membro.listaTextoEmJornalDeNoticia, "Textos em jornais de notícias/revistas" )
        (nPB4, lista_PB4, titulo_PB4) = self.gerar_lista_de_producoes_de_membro( membro.listaTrabalhoCompletoEmCongresso, "Trabalhos completos publicados em anais de congressos" )
        (nPB5, lista_PB5, titulo_PB5) = self.gerar_lista_de_producoes_de_membro( membro.listaResumoExpandidoEmCongresso, "Resumos expandidos publicados em anais de congressos" )
        (nPB6, lista_PB6, titulo_PB6) = self.gerar_lista_de_producoes_de_membro( membro.listaResumoEmCongresso, "Resumos publicados em anais de congressos" )
        (nPB7, lista_PB7, titulo_PB7) = self.gerar_lista_de_producoes_de_membro( membro.listaArtigoAceito, "Artigos aceitos para publicação" )
        (nPB8, lista_PB8, titulo_PB8) = self.gerar_lista_de_producoes_de_membro( membro.listaApresentacaoDeTrabalho, "Apresentações de trabalho" )
        (nPB9, lista_PB9, titulo_PB9) = self.gerar_lista_de_producoes_de_membro( membro.listaOutroTipoDeProducaoBibliografica, "Demais tipos de produção bibliográfica" )

        (nPT0, lista_PT0, titulo_PT0) = self.gerar_lista_de_producoes_de_membro( membro.listaSoftwareComPatente, "Programas de computador com registro" )
        (nPT1, lista_PT1, titulo_PT1) = self.gerar_lista_de_producoes_de_membro( membro.listaSoftwareSemPatente, "Programas de computador sem registro" )
        (nPT2, lista_PT2, titulo_PT2) = self.gerar_lista_de_producoes_de_membro( membro.listaProdutoTecnologico, "Produtos tecnológicos" )
        (nPT3, lista_PT3, titulo_PT3) = self.gerar_lista_de_producoes_de_membro( membro.listaProcessoOuTecnica, "Processos ou técnicas" )
        (nPT4, lista_PT4, titulo_PT4) = self.gerar_lista_de_producoes_de_membro( membro.listaTrabalhoTecnico, "Trabalhos técnicos" )
        (nPT5, lista_PT5, titulo_PT5) = self.gerar_lista_de_producoes_de_membro( membro.listaOutroTipoDeProducaoTecnica, "Demais tipos de produção técnica" )

        (nPA0, lista_PA0, titulo_PA0) = self.gerar_lista_de_producoes_de_membro( membro.listaProducaoArtistica, "Total de produção artística" )

        (nOA0, lista_OA0, titulo_OA0) = self.gerar_lista_de_producoes_de_membro( membro.listaOASupervisaoDePosDoutorado, "Supervisão de pós-doutorado" )
        (nOA1, lista_OA1, titulo_OA1) = self.gerar_lista_de_producoes_de_membro( membro.listaOATeseDeDoutorado, "Tese de doutorado" )
        (nOA2, lista_OA2, titulo_OA2) = self.gerar_lista_de_producoes_de_membro( membro.listaOADissertacaoDeMestrado, "Dissertação de mestrado" )
        (nOA3, lista_OA3, titulo_OA3) = self.gerar_lista_de_producoes_de_membro( membro.listaOAMonografiaDeEspecializacao, "Monografia de conclusão de curso de aperfeiçoamento/especialização" )
        (nOA4, lista_OA4, titulo_OA4) = self.gerar_lista_de_producoes_de_membro( membro.listaOATCC, "Trabalho de conclusão de curso de graduação" )
        (nOA5, lista_OA5, titulo_OA5) = self.gerar_lista_de_producoes_de_membro( membro.listaOAIniciacaoCientifica, "Iniciação científica" )
        (nOA6, lista_OA6, titulo_OA6) = self.gerar_lista_de_producoes_de_membro( membro.listaOAOutroTipoDeOrientacao, "Orientações de outra natureza" )

        (nOC0, lista_OC0, titulo_OC0) = self.gerar_lista_de_producoes_de_membro( membro.listaOCSupervisaoDePosDoutorado, "Supervisão de pós-doutorado" )
        (nOC1, lista_OC1, titulo_OC1) = self.gerar_lista_de_producoes_de_membro( membro.listaOCTeseDeDoutorado, "Tese de doutorado" )
        (nOC2, lista_OC2, titulo_OC2) = self.gerar_lista_de_producoes_de_membro( membro.listaOCDissertacaoDeMestrado, "Dissertação de mestrado" )
        (nOC3, lista_OC3, titulo_OC3) = self.gerar_lista_de_producoes_de_membro( membro.listaOCMonografiaDeEspecializacao, "Monografia de conclusão de curso de aperfeiçoamento/especialização" )
        (nOC4, lista_OC4, titulo_OC4) = self.gerar_lista_de_producoes_de_membro( membro.listaOCTCC, "Trabalho de conclusão de curso de graduação" )
        (nOC5, lista_OC5, titulo_OC5) = self.gerar_lista_de_producoes_de_membro( membro.listaOCIniciacaoCientifica, "Iniciação científica" )
        (nOC6, lista_OC6, titulo_OC6) = self.gerar_lista_de_producoes_de_membro( membro.listaOCOutroTipoDeOrientacao, "Orientações de outra natureza" )

        (nPj0, lista_Pj0, titulo_Pj0) = self.gerar_lista_de_producoes_de_membro( membro.listaProjetoDePesquisa, "Total de projetos de pesquisa" )
        (nPm0, lista_Pm0, titulo_Pm0) = self.gerar_lista_de_producoes_de_membro( membro.listaPremioOuTitulo, "Total de prêmios e títulos" )
        (nEp0, lista_Ep0, titulo_Ep0) = self.gerar_lista_de_producoes_de_membro( membro.listaParticipacaoEmEvento, "Total de participação em eventos" )
        (nEo0, lista_Eo0, titulo_Eo0) = self.gerar_lista_de_producoes_de_membro( membro.listaOrganizacaoDeEvento, "Total de organização de eventos" )

        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            (nCE, lista_CE, titulo_CE, lista_CE_detalhe)    = self.gerar_lista_de_colaboracoes (membro, 'Colaborações endôgenas')

        s += '<h3>Produção bibliográfica</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB0', titulo_PB0, nPB0 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB1', titulo_PB1, nPB1 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB2', titulo_PB2, nPB2 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB3', titulo_PB3, nPB3 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB4', titulo_PB4, nPB4 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB5', titulo_PB5, nPB5 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB6', titulo_PB6, nPB6 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB7', titulo_PB7, nPB7 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB8', titulo_PB8, nPB8 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB9', titulo_PB9, nPB9 )
        s += '</ul>'
        s += '<h3>Produção técnica</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT0', titulo_PT0, nPT0 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT1', titulo_PT1, nPT1 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT2', titulo_PT2, nPT2 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT3', titulo_PT3, nPT3 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT4', titulo_PT4, nPT4 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT5', titulo_PT5, nPT5 )
        s += '</ul>'
        s += '<h3>Produção artística</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PA0', titulo_PA0, nPA0 )
        s += '</ul>'
        s += '<h3>Orientações em andamento</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA0', titulo_OA0, nOA0 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA1', titulo_OA1, nOA1 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA2', titulo_OA2, nOA2 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA3', titulo_OA3, nOA3 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA4', titulo_OA4, nOA4 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA5', titulo_OA5, nOA5 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OA6', titulo_OA6, nOA6 )
        s += '</ul>'
        s += '<h3>Supervisões e orientações concluídas</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC0', titulo_OC0, nOC0 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC1', titulo_OC1, nOC1 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC2', titulo_OC2, nOC2 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC3', titulo_OC3, nOC3 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC4', titulo_OC4, nOC4 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC5', titulo_OC5, nOC5 )
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'OC6', titulo_OC6, nOC6 )
        s += '</ul>'
        s += '<h3>Projetos de pesquisa</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'Pj0', titulo_Pj0, nPj0 )
        s += '</ul>'
        s += '<h3>Prêmios e títulos</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'Pm0', titulo_Pm0, nPm0 )
        s += '</ul>'
        s += '<h3>Participação em eventos</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'Ep0', titulo_Ep0, nEp0 )
        s += '</ul>'
        s += '<h3>Organização de eventos</h3> <ul>'
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'Eo0', titulo_Eo0, nEo0 )
        s += '</ul>'
        #-------- 
        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '<h3>Lista de colaborações</h3> <ul>'
            s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'CE', titulo_CE, nCE ) 
            s += '    <ul> {} </ul>'.format( lista_CE ) 
            s += '</ul>'

        s += '<hr>'
        s += '<h3>Produção bibliográfica</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB0', titulo_PB0, nPB0, lista_PB0)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB1', titulo_PB1, nPB1, lista_PB1)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB2', titulo_PB2, nPB2, lista_PB2)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB3', titulo_PB3, nPB3, lista_PB3)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB4', titulo_PB4, nPB4, lista_PB4)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB5', titulo_PB5, nPB5, lista_PB5)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB6', titulo_PB6, nPB6, lista_PB6)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB7', titulo_PB7, nPB7, lista_PB7)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB8', titulo_PB8, nPB8, lista_PB8)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB9', titulo_PB9, nPB9, lista_PB9)
        s += '</ul>'
        s += '<h3>Produção técnica</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT0', titulo_PT0, nPT0, lista_PT0)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT1', titulo_PT1, nPT1, lista_PT1)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT2', titulo_PT2, nPT2, lista_PT2)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT3', titulo_PT3, nPT3, lista_PT3)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT4', titulo_PT4, nPT4, lista_PT4)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT5', titulo_PT5, nPT5, lista_PT5)
        s += '</ul>'
        s += '<h3>Produção artística</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PA0', titulo_PA0, nPA0, lista_PA0)
        s += '</ul>'
        s += '<h3>Orientações em andamento</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA0', titulo_OA0, nOA0, lista_OA0)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA1', titulo_OA1, nOA1, lista_OA1)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA2', titulo_OA2, nOA2, lista_OA2)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA3', titulo_OA3, nOA3, lista_OA3)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA4', titulo_OA4, nOA4, lista_OA4)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA5', titulo_OA5, nOA5, lista_OA5)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OA6', titulo_OA6, nOA6, lista_OA6)
        s += '</ul>'
        s += '<h3>Supervisões e orientações concluídas</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC0', titulo_OC0, nOC0, lista_OC0)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC1', titulo_OC1, nOC1, lista_OC1)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC2', titulo_OC2, nOC2, lista_OC2)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC3', titulo_OC3, nOC3, lista_OC3)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC4', titulo_OC4, nOC4, lista_OC4)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC5', titulo_OC5, nOC5, lista_OC5)
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'OC6', titulo_OC6, nOC6, lista_OC6)
        s += '</ul>'
        s += '<h3>Projetos de pesquisa</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'Pj0', titulo_Pj0, nPj0, lista_Pj0)
        s += '</ul>'
        s += '<h3>Prêmios e títulos</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'Pm0', titulo_Pm0, nPm0, lista_Pm0)
        s += '</ul>'
        s += '<h3>Participação em eventos</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'Ep0', titulo_Ep0, nEp0, lista_Ep0)
        s += '</ul>'
        s += '<h3>Organização de eventos</h3> <ul>'
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'Eo0', titulo_Eo0, nEo0, lista_Eo0)
        s += '</ul>'
        
        if self.grupo.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            s += '<h3>Lista de colaborações</h3> <ul>'
            s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'CE', titulo_CE, nCE, lista_CE_detalhe)
            s += '</ul>'

        s += self.paginaBottom()
        self.salvarPagina("membro-" + membro.idLattes + self.extensaoPagina, s)


    def gerar_lista_de_producoes_de_membro (self, lista, titulo):
        s = '<ol>'
        for publicacao in lista:
            s += '<li>' + publicacao.html(self.grupo.listaDeMembros)
        s += '</ol><br>'
        return (len(lista), s, titulo)


    def gerar_lista_de_colaboracoes (self, membro, titulo):
        s = '<ol>'
        detalhe = '<ul>'

        colaboradores = self.grupo.colaboradores_endogenos[membro.idMembro]

        for (idColaborador, quantidade) in sorted(colaboradores, key=lambda x:(-x[1],x[0])):
            colaborador = self.grupo.listaDeMembros[idColaborador] 
            s       += '<li><a href="#{0}">{1}</a> ({2})'.format(colaborador.idLattes, colaborador.nomeCompleto, quantidade)
            detalhe += '<li id="{0}"> <b>{3} &hArr; <a href="membro-{0}{4}">{1}</a></b> ({2}) <ol>'.format(colaborador.idLattes, colaborador.nomeCompleto, quantidade, membro.nomeCompleto, self.extensaoPagina)

            for publicacao in self.grupo.listaDeColaboracoes[membro.idMembro][idColaborador]:
                detalhe +=  '<li>' + publicacao.html(self.grupo.listaDeMembros)

            detalhe += '</ol><br>'
        s += '</ol><br>'

        detalhe += '</ul><br>'
        return ( len(colaboradores), s, titulo, detalhe)




    def pagina_top(self, cabecalho=''):
        nome_grupo = self.grupo.obterParametro('global-nome_do_grupo')

        s = self.html1
        template = '<head>' \
                   '<meta http-equiv="Content-Type" content="text/html; charset=utf8">' \
                   '<meta name="Generator" content="scriptLattes">' \
                   '<title>{nome_grupo}</title>' \
                   '<link rel="stylesheet" href="css/scriptLattes.css" type="text/css">' \
                   '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap">' \
                   '<link rel="stylesheet" type="text/css" href="css/jquery.dataTables.css">' \
                   '<link rel="stylesheet" type="text/css" href="css/dataTables.colVis.min.css">' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.dataTables.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/dataTables.colVis.min.js"></script>' \
				   '<script src="http://professor.ufabc.edu.br/~jesus.mena/sorttable.js"></script>'\
                   '{cabecalho}' \
                   '</head>' \
                   '<body><div id="header2"> <button onClick="history.go(-1)">Voltar</button>' \
                   '<h2>{nome_grupo}</h2></div>'
        # '<script type="text/javascript" charset="utf8" src="jquery.dataTables.rowGrouping.js"></script>' \
        s += template.format(nome_grupo=nome_grupo, cabecalho=cabecalho)
        return s

    def paginaBottom(self):
        agora = datetime.datetime.now()
        dia = '0' + str(agora.day)
        mes = '0' + str(agora.month)
        ano = str(agora.year)
        hora = '0' + str(agora.hour)
        minuto = '0' + str(agora.minute)
        segundo = '0' + str(agora.second)

        dia = dia[-2:]
        mes = mes[-2:]
        hora = hora[-2:]
        minuto = minuto[-2:]
        segundo = segundo[-2:]
        data = dia + "/" + mes + "/" + ano + " " + hora + ":" + minuto + ":" + segundo

        s = '<br><p>'
        if not self.grupo.obterParametro('global-itens_desde_o_ano') == '' and not self.grupo.obterParametro('global-itens_ate_o_ano') == '':
            s += '<br>(*) Relatório criado com produções desde ' + \
                 self.grupo.obterParametro('global-itens_desde_o_ano') + \
                 ' até ' + \
                 self.grupo.obterParametro('global-itens_ate_o_ano')

        s += '\n<br>Data de processamento: ' + data + '<br> \
        <div id="footer"> \
        Relatório gerado por <a href="http://scriptlattes.sourceforge.net/">scriptLattes ' + self.version + '</a>. \
        Os resultados podem ser afetados por possíveis falhas decorrentes de inconsistências no preenchimento dos Currículos Lattes. E-mail de contato: <a href="mailto:' + self.grupo.obterParametro('global-email_do_admin') + '">' + self.grupo.obterParametro('global-email_do_admin') + '</a> \
        </div> '

        if self.grupo.obterParametro('global-google_analytics_key'):
            s += '<script type="text/javascript">\
            var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");\
            document.write(unescape("%3Cscript src=\'" + gaJsHost + "google-analytics.com/ga.js\' type=\'text/javascript\'%3E%3C/script%3E"));\
            </script>\
            <script type="text/javascript">\
            try {\
              var pageTracker = _gat._getTracker("' + self.grupo.obterParametro('global-google_analytics_key') + '");\
              pageTracker._trackPageview();\
            } catch(err) {}\
            </script>'
        s += '</body>' + self.html2

        return s


    def salvarPagina(self, nome, conteudo):
        file = open(os.path.join(self.dir, nome), 'w', encoding='utf8')
        file.write(conteudo)
        file.close()


    def salvarPublicacaoEmFormatoRIS(self, pub):
        self.arquivoRis.write(pub.ris())


    def formatarTotaisQualis(self, qtd):
        st = '(<b>A1</b>: '+str(qtd['A1'])+', <b>A2</b>: '+str(qtd['A2'])+', <b>A3</b>: '+str(qtd['A3'])+', <b>A4</b>: '+str(qtd['A4'])+', <b>B1</b>: '+str(qtd['B1'])+', <b>B2</b>: '+str(qtd['B2'])
        st+= ', <b>B3</b>: '+str(qtd['B3'])+', <b>B4</b>: '+str(qtd['B4'])+', <b>B5</b>: '+str(qtd['B5'])+', <b>C</b>: '+str(qtd['C'])+', <b>NP</b>: '+str(qtd['NP'])
        st+= ', <b>Qualis n&atilde;o identificado</b>: '+str(qtd['Qualis nao identificado'])+')'
        st+= '<br><p><b>Legenda Qualis:</b><ul>'
        st+= '<li> Publica&ccedil;&atilde;o para a qual o nome exato do Qualis foi identificado: <font color="#254117"><b>Qualis &lt;estrato&gt;</b></font>'
        st+= '<li> Publica&ccedil;&atilde;o para a qual um nome similar (n&atilde;o exato) do Qualis foi identificado: <font color="#F88017"><b>Qualis &lt;estrato&gt;</b></font> (nome similar)'
        st+= '<li> Publica&ccedil;&atilde;o para a qual nenhum nome do Qualis foi identificado: <font color="#FDD7E4"><b>Qualis n&atilde;o identificado</b></font> (nome usado na busca)'
        st+= '</ul>'
        return st

        #return 'Sem totais qualis ainda...'


def menuHTMLdeBuscaPB(titulo):
    return ""
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://scholar.google.com/scholar?hl=en&lr=&q=' + titulo + '&btnG=Search">cita&ccedil;&otilde;es Google Scholar</a> | \
           <a href="http://academic.research.microsoft.com/Search?query=' + titulo + '">cita&ccedil;&otilde;es Microsoft Acad&ecirc;mico</a> | \
           <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> ] \
         </font><br>'
    return s


def menuHTMLdeBuscaPT(titulo):
    return ""
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s


def menuHTMLdeBuscaPA(titulo):
    return ""
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s


def formata_qualis(qualis, qualissimilar):
    s = ''
    if not qualis==None:
        if qualis=='':
            qualis = 'Qualis nao identificado'

        if qualis=='Qualis nao identificado':
            # Qualis nao identificado - imprime em vermelho
            s += '<font color="#FDD7E4"><b>Qualis: N&atilde;o identificado</b></font> ('+qualissimilar+')'
        else:
            if qualissimilar=='':
                # Casamento perfeito - imprime em verde
                s += '<font color="#254117"><b>Qualis: ' + qualis + '</b></font>'
            else:
                # Similar - imprime em laranja
                s += '<font color="#F88017"><b>Qualis: ' + qualis + '</b></font> ('+qualissimilar+')'
    return s


'''
def formata_qualis(qualis, qualissimilar):
    s = ''

    if not qualis:
        #s += '<font color="#FDD7E4"><b>Qualis: N&atilde;o identificado</b></font>'
        s += ''
    else:
        s += '<font color="#254117"><b>Qualis: </b></font> '
        if type(qualis) is str:
            s += '<font class="area"><b>SEM_AREA</b></font> - <b>' + qualis + '</b>&nbsp'
        else:
            l = ['<font class="area"><b>' + area + '</b></font> - <b>' + q + '</b>' for area, q in
                 sorted(qualis.items(), key=lambda x: x[0])]
            s += '&nbsp|&nbsp'.join(l)
    return s
'''
