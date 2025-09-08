#!/usr/bin/python
# encoding: utf-8

from collections import defaultdict
import datetime
import os
import re
import json
from . import membro
from networkx.readwrite import json_graph
import networkx as nx
import unicodedata

# SVG inline representando um mini-grafo de coautoria
grafo_svg = """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="13 18 114 64"
     width="120" height="73"
     role="img" aria-label="Ícone de grafo de coautoria">
  <!-- Arestas (todas em darkblue) -->
  <line x1="30"  y1="50" x2="75"  y2="25" stroke="#00008B" stroke-width="2"/>
  <line x1="30"  y1="50" x2="75"  y2="75" stroke="#00008B" stroke-width="2"/>
  <line x1="75"  y1="25" x2="120" y2="50" stroke="#00008B" stroke-width="2"/>
  <line x1="75"  y1="75" x2="120" y2="50" stroke="#00008B" stroke-width="2"/>

  <!-- Nós coloridos -->
  <circle cx="30"  cy="50" r="7" fill="#00008B"/>  <!-- darkblue -->
  <circle cx="75"  cy="25" r="7" fill="#006400"/>  <!-- darkgreen -->
  <circle cx="75"  cy="75" r="7" fill="#8B0000"/>  <!-- darkred -->
  <circle cx="120" cy="50" r="7" fill="#00008B"/>  <!-- darkblue -->
</svg>
"""

class GeradorDePaginasWeb:
    grupo = None
    dir = None
    version = None
    extensaoPagina = None
    arquivoRis = None

    def __init__(self, grupo):
        self.grupo = grupo
        self.version = 'V.2025.09'
        self.dir = self.grupo.obterParametro('global-diretorio_de_saida')

        self.extensaoPagina = '.html'
        self.html1 = '<html>'
        self.html2 = '</html>'

        # geracao de arquivo RIS com as publicacoes
        if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
            self.arquivoRis = open(self.dir + "/" + "publicacoes.ris", 'w', encoding='utf8')

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
            s += '<li> <a href="PT4-0' + self.extensaoPagina + '">Trabalhos técnicos</a> ' + '(' + str( self.nPT4) + ')'
        if self.nPT5 > 0:
            s += '<li> <a href="PT5-0' + self.extensaoPagina + '">Demais tipos de produção técnica</a> '+ '(' + str(self.nPT5) + ')'
        if self.nPT6 > 0:
            s += '<li> <a href="PT6-0' + self.extensaoPagina + '">Entrevistas, mesas redondas, programas e comentários na mídia</a> '+ '(' + str(self.nPT6) + ')'
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
            s += "</ul>\n"
            s += "<h3 id=\"grafo\">Grafo de colaborações</h3>\n"
            s += (
                f'<a href="grafoDeColaboracoes{self.extensaoPagina}" '
                'title="Clique para ver o grafo interativo de coautoria">\n'
                f'{grafo_svg}\n'
                '</a>\n'
            )

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
        self.nPT6 = 0
        self.nPT = 0

        if self.grupo.obterParametro('relatorio-incluir_software_com_registro'):
            self.nPT0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaSoftwareComPatente, "Programas de computador com registro", "PT0")
        if self.grupo.obterParametro('relatorio-incluir_software_sem_registro'):
            self.nPT1 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaSoftwareSemPatente, "Programas de computador sem registro", "PT1")
        if self.grupo.obterParametro('relatorio-incluir_produto_tecnologico'):
            self.nPT2 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProdutoTecnologico, "Produtos tecnológicos", "PT2")
        if self.grupo.obterParametro('relatorio-incluir_processo_ou_tecnica'):
            self.nPT3 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaProcessoOuTecnica, "Processos ou técnicas", "PT3")
        if self.grupo.obterParametro('relatorio-incluir_trabalho_tecnico'):
            self.nPT4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaTrabalhoTecnico, "Trabalhos técnicos", "PT4")
        if self.grupo.obterParametro('relatorio-incluir_outro_tipo_de_producao_tecnica'):
            self.nPT5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaOutroTipoDeProducaoTecnica, "Demais tipos de produção técnica", "PT5")
        if self.grupo.obterParametro('relatorio-incluir_entrevista_mesas_e_comentarios'):
            self.nPT6 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaEntrevista, "Entrevistas, mesas redondas, programas e comentários na mídia", "PT6")
        # Total de produções técnicas
        self.nPT = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPT, "Total de produção técnica", "PT")


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
                <h3>{titulo}</h3> <br>
                    {grafico}
                    Número total de itens: {numero_itens}<br>
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


    def gerar_grafico_de_producoes_html(self, lista_completa: dict, titulo: str, container_id: str = "grafico-producoes") -> str:
        """
        Gera o HTML+JS para um gráfico de barras Highcharts
        embutindo os dados e usando o CDN, sem arquivos .js locais.
        """
        # 1) Ordena os anos
        itens_ordenados = sorted(lista_completa.items())  # [(ano, lista_de_publicacoes), ...]
 
        # 2) Separa em duas listas: categorias (anos) e valores (contagens)
        categorias = []
        valores    = []
        for ano, publicacoes in itens_ordenados:
            categorias.append(str(ano))
            valores.append(len(publicacoes))
 
        # 3) Monta a configuração do Highcharts
        config = {
            "chart": {"type": "column", "height": 250},
            "title": {"text": ''},
            "xAxis": {"categories": categorias, "type": "category"},
            "yAxis": {"title": {"text": "Quantidade"}},
            "legend": {"enabled": False},
            "plotOptions": {
                "column": {
                    "color": "#4A4A4A",           # cor das barras
                    "borderRadius": 2,            # cantos levemente arredondados
                    "pointPadding": 0.1,
                    "groupPadding": 0.1
                }
            },
            "series": [
                {
                    "name": "Total",
                    "data": valores,
                    #"color": "#222233"          # opção alternativa: definir aqui
                }
            ],
            "credits": {"enabled": False}
        }

 
        # 4) Retorna o bloco HTML/JS completo
        return f"""
        <div id="{container_id}" style="width:100%; margin:1em auto;"></div>
        <!-- script src="https://code.highcharts.com/highcharts.js"></script -->
        <script src="./js/highcharts.js"></script>
        <script>
          document.addEventListener('DOMContentLoaded', function () {{
            Highcharts.chart('{container_id}', {json.dumps(config)});
          }});
        </script>
        """

  
    def gerar_pagina_de_producoes(self, lista_completa, titulo_pagina, prefixo, ris=False):    
        def _s(x): 
            return '' if x is None else str(x)
    
        def _int(x, default=0):
            try:
                return int(x)
            except Exception:
                return default
    
        def _slug(label):
            # rótulo → identificador seguro para Tabulator
            t = unicodedata.normalize('NFKD', _s(label)).encode('ascii', 'ignore').decode('ascii')
            t = re.sub(r'[^A-Za-z0-9]+', '_', t).strip('_').lower()
            return t or 'campo'
    
        def _eh_num(v):
            if v is None:
                return False
            try:
                float(str(v).replace('.', '').replace(',', '.'))
                return True
            except Exception:
                return False
    
        def _tipo_pub(pub):
            t = getattr(pub, 'tipo', None)
            if callable(t):
                try:
                    return _s(t())
                except Exception:
                    pass
            if isinstance(t, str) and t:
                return t
            return pub.__class__.__name__
    
        def _max_len(values):
            m = 0
            for v in values:
                if v is None:
                    continue
                s = str(v)
                if len(s) > m:
                    m = len(s)
            return m
    
        total_producoes = sum(len(v) for v in list(lista_completa.values()))
        keys = sorted(list(lista_completa.keys()), reverse=True)
        if not keys:
            return 0
    
        max_elementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
        total_paginas = total_producoes // max_elementos + (1 if total_producoes % max_elementos != 0 else 0)
    
        # Gráfico segue como já existia
        grafico = self.gerar_grafico_de_producoes_html(lista_completa, titulo_pagina)
    
        # [(ano, idx_no_ano, publicacao), ...]
        anos_indices_publicacoes = self.arranjar_publicacoes(lista_completa)
        itens_por_pagina = self.chunks(anos_indices_publicacoes, max_elementos)
    
        # Se houver mais de um tipo globalmente, página "Total" terá coluna Tipo
        todos_tipos = {_tipo_pub(pub) for (_, _, pub) in anos_indices_publicacoes}
        incluir_coluna_tipo_global = len(todos_tipos) > 1
    
        for numero_pagina, itens in enumerate(itens_por_pagina):
            linhas = []
            campos_dyn = {}         # {rotulo -> field_id}
            valores_por_campo = {}  # {field_id -> [valores]}
    
            # constrói linhas apenas com json() (sem HTML)
            for (ano, _, publicacao) in itens:
                ano_num = _int(ano, 0) if ano is not None else 0
                try:
                    meta = publicacao.json() or {}
                except Exception:
                    meta = {}
    
                flat = {}
                for rotulo, valor in meta.items():
                    field_id = campos_dyn.get(rotulo)
                    if not field_id:
                        field_id = _slug(rotulo)
                        # previne colisões improváveis de slug
                        while field_id in campos_dyn.values():
                            field_id += '_x'
                        campos_dyn[rotulo] = field_id
                    flat[field_id] = valor
                    valores_por_campo.setdefault(field_id, []).append(valor)
    
                row = {"ano": ano_num}
                if incluir_coluna_tipo_global:
                    row["tipo"] = _tipo_pub(publicacao)
                row.update(flat)
                linhas.append(row)
    
            # === Definição de colunas base ===
            colunas = [{
                "title": "Ano", "field": "ano", "hozAlign": "center",
                "sorter": "number", "headerFilter": "input",
                "headerFilterParams": {"values": True}, "width": 110,
                "formatter": "fmtAno", "tooltip": True, "resizable": True, "widthGrow": 0
            }]
            if incluir_coluna_tipo_global:
                colunas.append({
                    "title": "Tipo", "field": "tipo", "hozAlign": "left",
                    "sorter": "string", "headerFilter": "input",
                    "tooltip": True, "resizable": True, "minWidth": 140, "widthGrow": 1
                })
    
            # heurística de largura por campo
            NOMES_COMPACTOS = {"volume", "número", "numero", "páginas", "paginas", "issn", "ano"}
            NOMES_MEDIOS = {"doi"}  # DOI ganha ellipsis e link
    
            for rotulo, field_id in campos_dyn.items():
                valores = valores_por_campo.get(field_id, [])
                so_numeros = len(valores) > 0 and all(_eh_num(v) for v in valores if v not in (None, ""))
                maxlen = _max_len(valores)
                rlow = rotulo.strip().lower()
    
                # largura/elasticidade
                if rlow in NOMES_COMPACTOS or so_numeros or maxlen <= 8:
                    width = 90
                    minw = 70
                    grow = 0
                elif rlow in NOMES_MEDIOS or maxlen <= 16:
                    width = 120
                    minw = 100
                    grow = 0
                elif maxlen <= 32:
                    width = None
                    minw = 140
                    grow = 1
                else:
                    width = None
                    minw = 200
                    grow = 2
    
                col = {
                    "title": rotulo,
                    "field": field_id,
                    "hozAlign": "left",
                    "sorter": "number" if so_numeros else "string",
                    "headerFilter": "input",
                    "tooltip": True,
                    "resizable": True,
                    "minWidth": minw,
                    "widthGrow": grow
                }
                if width is not None:
                    col["width"] = width
    
                # DOI como link (formatter JS)
                if rlow == "doi":
                    col["formatter"] = "fmtDOI"
    
                colunas.append(col)
    
            # === HTML completo da página ===
            s = self.pagina_top()
            s += """
    <link href="css/tabulator_site.min.css" rel="stylesheet" />
    <link href="css/tabulator-scriplattes.css" rel="stylesheet" />
    <script src="js/tabulator.min.js"></script>
    <script src="js/xlsx.full.min.js"></script>
    
    <style>
    /* ellipsis em todas as células */
    #tabela-publicacoes .tabulator-cell {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    </style>
    """
            s += f"""
    <h3>{_s(titulo_pagina)}</h3><br>
    {grafico}
    Número total de itens: {str(total_producoes)}<br>
    {self.gerarIndiceDePaginas(total_paginas, numero_pagina, prefixo)}
    
    <div class="sl-controls" style="margin-top:.5rem">
      <button id="pubs-csv">⬇️ CSV</button>
      <button id="pubs-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-publicacoes" class="sl-tabela"></div>
    """
    
            js_data = json.dumps(linhas, ensure_ascii=False)
            js_cols = json.dumps(colunas, ensure_ascii=False)
    
            s += f"""
    <script>
    const DATA = {js_data};
    const COLUMNS = {js_cols};
    
    const LANG_PT = {{
      "pt-br": {{
        "pagination": {{
          "first":"«","first_title":"Primeira",
          "last":"»","last_title":"Última",
          "prev":"‹","prev_title":"Anterior",
          "next":"›","next_title":"Próxima"
        }},
        "headerFilters": {{ "default":"⎯ Filtrar ⎯" }}
      }}
    }};
    
    // Ano: mostra "—" quando 0
    function fmtAno(cell) {{
      const v = cell.getValue() || 0;
      return v === 0 ? "—" : v;
    }}
    
    // DOI → link clicável (aceita "10.xxxx/..." ou "doi:10...." ou já com http/https)
    function fmtDOI(cell) {{
      let v = cell.getValue();
      if (!v) return "";
      v = String(v).trim();
      let href = v;
      if (!/^https?:/i.test(v)) {{
        v = v.replace(/^doi:\\s*/i, "");
        href = "https://doi.org/" + v;
      }}
      const esc = (t) => String(t).replace(/[&<>"']/g, m => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}})[m]);
      return `<a href="${{esc(href)}}" target="_blank" rel="noopener">${{esc(v)}}</a>`;
    }}
    
    // aplica formatter customizado quando marcado como "fmtDOI" em Python
    COLUMNS.forEach(col => {{
      if (col.formatter === "fmtDOI") col.formatter = fmtDOI;
    }});
    
    document.addEventListener("DOMContentLoaded", function(){{
      const table = new Tabulator("#tabela-publicacoes", {{
        data: DATA,
        layout: "fitColumns",
        height: (DATA.length < 30 ? "45vh" : "70vh"),
        responsiveLayout: "collapse",
        pagination: "local",
        paginationSize: 100,
        paginationSizeSelector: [50, 100, 200, 500, 1000],
        movableColumns: true,
        headerFilterLiveFilter: true,
        columns: COLUMNS,
        locale: true, langs: LANG_PT, locale: "pt-br",
      }});
    
      document.getElementById("pubs-csv").onclick  = () => table.download("csv",  "publicacoes.csv",  {{ bom:true }});
      document.getElementById("pubs-xlsx").onclick = () => table.download("xlsx", "publicacoes.xlsx", {{ sheetName:"Publicações" }});
    }});
    </script>
    """
            s += self.paginaBottom()
            self.salvarPagina(prefixo + '-' + str(numero_pagina) + self.extensaoPagina, s)
    
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
        # 1) texto introdutório (monta lista de tipos incluídos)
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
        if self.grupo.obterParametro('grafo-incluir_software_com_registro'):
            lista += 'Programas de computador com registro, '
        if self.grupo.obterParametro('grafo-incluir_software_sem_registro'):
            lista += 'Programas de computador sem registro, '
        if self.grupo.obterParametro('grafo-incluir_produto_tecnologico'):
            lista += 'Produtos tecnológicos, '
        if self.grupo.obterParametro('grafo-incluir_processo_ou_tecnica'):
            lista += 'Processos ou técnicas, '
        if self.grupo.obterParametro('grafo-incluir_trabalho_tecnico'):
            lista += 'Trabalhos técnicos , '
        if self.grupo.obterParametro('grafo-incluir_outro_tipo_de_producao_tecnica'):
            lista += 'Demais tipos de produção técnica, '
        if self.grupo.obterParametro('grafo-incluir_entrevista_mesas_e_comentarios'):
            lista += 'Entrevistas, mesas redondas, programas e comentários na mídia, '
        if self.grupo.obterParametro('grafo-incluir_producao_artistica'):
            lista += 'Produções artísticas, '
        lista = lista.rstrip(', ')
    
        # 2) cabeçalho
        s = self.pagina_top()
        s += f"""
    <h3>Grafo de colaborações</h3>
    <p>
      <a href="membros{self.extensaoPagina}">
        {self.grupo.numeroDeMembros()} currículos Lattes
      </a> geraram este grafo baseado em <em>{lista}</em>.<br>
      O tamanho do vértice é proporcional ao número de colaboradores. A espessura da aresta é proporcional ao número de colaborações.
    </p>
    """
    
        # 3) grafo -> JSON (para injetar no JS)
        G = self.grupo.grafoDeColaboracoes
        from networkx.readwrite import json_graph
        import json
        data = json_graph.node_link_data(G)
        graph_js = json.dumps(data, ensure_ascii=False)
    
        # 4) estilos + estrutura + D3 (com tooltip/ellipsis nas tabelas ao final)
        s += r"""
    <style>
      .viz-wrap { display:flex; gap:1rem; }
      #info-pane {
        flex:1; max-height: 1200px; overflow:auto;
        border:1px solid #ddd; padding:0.75rem; background:#fafafa;
      }
      .toolbar {
        display:flex; gap:0.5rem; align-items:center; margin-bottom:0.5rem; flex-wrap: wrap;
      }
      .toolbar input[type="text"] {
        flex:1; min-width: 220px; padding:0.5rem; border:1px solid #ccc; border-radius:8px;
      }
      .toolbar button {
        padding:0.5rem 0.75rem; border:1px solid #ccc; border-radius:8px; background:#fff; cursor:pointer;
      }
      .legend { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap;
        font: 14px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, sans-serif; }
      .legend .title { margin-right:.25rem; }
      .legend .item { display:inline-flex; align-items:center; gap:.35rem; margin-right:.75rem; }
      .legend .swatch { width:14px; height:14px; display:inline-block; border-radius:2px; border:1px solid rgba(0,0,0,.2); }
    
      #viz-container { flex:3; height: 70vh; min-height: 620px; border:1px solid #ccc; position:relative; }
      @media (min-width: 1200px) { #viz-container { height: 1200px; } }
      @media (max-height: 600px) { #viz-container { height: 60vh; } }
    
      .node { cursor:grab; }
      .node:active { cursor:grabbing; }
      .node.selected circle { stroke:#111; stroke-width:1px; }
      .dimmed { opacity:0.15; }
    
      .label { font: 5px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, sans-serif; pointer-events:none; }
      .edge-label { font-size: 3px; line-height: 1; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, sans-serif; fill:#555; }
      .edge { stroke:#aaa; stroke-opacity:0.85; }
      .edge.highlight { stroke:#333; }
      .hidden { display:none !important; }
    
      /* Ellipsis + tooltip nas tabelas (aplicado quando Tabulator monta) */
      #tabela-vertices .tabulator-cell,
      #tabela-arestas  .tabulator-cell {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }
    </style>
    
    <div class="viz-wrap">
      <div style="flex:3; display:flex; flex-direction:column;">
        <div class="toolbar">
          <div id="legend" class="legend">
            <span class="title">As cores representam os seguintes rótulos:</span>
          </div>
          <button id="btnToggleLabels" title="Mostrar/ocultar rótulos (vértices e arestas)">Ocultar rótulos</button>
          <input id="searchBox" type="text" placeholder="Buscar pesquisador (nome ou ID)..." />
          <button id="btnSearch">Buscar</button>
          <button id="btnClear">Limpar seleção</button>
        </div>
    
        <div id="viz-container">
          <svg id="viz" width="100%" height="100%"></svg>
        </div>
      </div>
    
      <div id="info-pane">
        <h4>Informação do Pesquisador</h4>
        <p>Clique em um nó (ou use a busca) para ver detalhes aqui.</p>
      </div>
    </div>
    
    <p>Você pode baixar o grafo em formato GEXF:
      <a href="grafo_de_colaboracoes.gexf" download="grafo_de_colaboracoes.gexf">grafo_de_colaboracoes.gexf</a>
    </p>
    
    <!-- D3 global (sem módulos) -->
    <script src="js/d3.min.js"></script>
    
    <script>
      // ======= dados =======
      var graphData = __GRAPH_JS__;
      var nodes = graphData.nodes.map(function(n,i){
        return {
          id: (n.id != null ? n.id : String(i)),
          label: (n.label != null ? n.label : (n.id != null ? n.id : String(i))),
          size: (n.size != null ? n.size : (4 + (n.degree || 0) * 0.6)),
          color: (n.color != null ? n.color : "#1f77b4"),
          instituicao: n.instituicao,
          url: n.url,
          atualizacaoCV: n.atualizacaoCV,
          periodo: n.periodo,
          rotulo: n.rotulo,
          nomePrimeiraGrandeArea: n.nomePrimeiraGrandeArea,
          nomePrimeiraArea: n.nomePrimeiraArea,
          publicacoesEmCoautoria: n.publicacoesEmCoautoria,
          degree: n.degree,
          artigosPeriodicos: n.artigosPeriodicos,
          artigosEventos: n.artigosEventos,
          capitulosDeLivros: n.capitulosDeLivros,
          livros: n.livros,
          enderecoProfissional: n.enderecoProfissional
        };
      });
      var links = graphData.links.map(function(e){
        return { source:e.source, target:e.target, weight:(e.weight||1), color:(e.color||"#aaa") };
      });
    
      // ======= dados para a TABELA (vértices) =======
      window.__VERTEX_TABLE_DATA__ = nodes.map(function(n){
        var m = (n.atualizacaoCV||"").toString().match(/(\d{2})\/(\d{2})\/(\d{4})/);
        var ymd = m ? (parseInt(m[3])*10000 + parseInt(m[2]) * 100 + parseInt(m[1])) : 0;
        return {
          id: n.id,
          nome: n.label,
          instituicao: n.instituicao || "",
          url: n.url || "",
          atualizacao: n.atualizacaoCV || "",
          atualizacao_num: ymd,
          periodo: n.periodo || "",
          rotulo: n.rotulo || "",
          grande_area: n.nomePrimeiraGrandeArea || "",
          area: n.nomePrimeiraArea || "",
          publicacoesEmCoautoria: +n.publicacoesEmCoautoria || 0,
          degree: +n.degree || 0,
          artigosPeriodicos: +n.artigosPeriodicos || 0,
          artigosEventos: +n.artigosEventos || 0,
          capitulosDeLivros: +n.capitulosDeLivros || 0,
          livros: +n.livros || 0,
          enderecoProfissional: n.enderecoProfissional || ""
        };
      });
    
      // ======= TABELA (arestas) – pares de membros (únicos, peso >= 1) =======
      (function buildEdgeTableData(){
        var byId = new Map(nodes.map(function(n){ return [String(n.id), n]; }));
        function normId(x){ return (typeof x === "object" && x !== null) ? String(x.id) : String(x); }
    
        // vizinhanças
        var neigh = new Map();
        nodes.forEach(function(n){ neigh.set(String(n.id), new Set()); });
        links.forEach(function(e){
          var s = normId(e.source), t = normId(e.target);
          if (!neigh.has(s)) neigh.set(s, new Set());
          if (!neigh.has(t)) neigh.set(t, new Set());
          neigh.get(s).add(t); neigh.get(t).add(s);
        });
    
        var seen = new Set();
        var rows = [];
        links.forEach(function(e){
          var s = normId(e.source), t = normId(e.target);
          var w = +e.weight || 0;
          if (w < 1) return;
          var a = s < t ? s : t, b = s < t ? t : s; // par único
          var key = a + "||" + b;
          if (seen.has(key)) return;
          seen.add(key);
    
          var nA = byId.get(a), nB = byId.get(b);
          if (!nA || !nB) return;
    
          // colaboradores em comum (interseção, excluindo o próprio par)
          var neighA = new Set(neigh.get(a) || []);
          var neighB = new Set(neigh.get(b) || []);
          var comuns = 0;
          neighA.forEach(function(x){
            if (x === a || x === b) return;
            if (neighB.has(x)) comuns += 1;
          });
    
          rows.push({
            aresta: [nA.label, nB.label].sort(function(x,y){ return String(x).localeCompare(String(y)); }).join(", "),
            colabs:  w,
            comuns:  comuns
          });
        });
    
        // ordena: colabs desc, comuns desc, aresta asc
        rows.sort(function(r1, r2){
          if (r2.colabs !== r1.colabs) return r2.colabs - r1.colabs;
          if (r2.comuns !== r1.comuns) return r2.comuns - r1.comuns;
          return r1.aresta.localeCompare(r2.aresta);
        });
    
        window.__EDGE_TABLE_DATA__ = rows;
      })();
    
      // ======= D3: simulação/zoom/legenda =======
      var svg = d3.select("#viz"),
          g = svg.append("g"),
          zoom = d3.zoom().scaleExtent([0.2, 5]).on("zoom", function(ev){ g.attr("transform", ev.transform); });
      svg.call(zoom);
    
      function getBox() { return document.getElementById("viz-container").getBoundingClientRect(); }
      var box = getBox();
      var width = box.width, height = box.height;
    
      var weights = links.map(function(d){ return +d.weight || 0; });
      var minW = d3.min(weights), maxW = d3.max(weights);
      var edgeWidth = d3.scaleLinear().domain([minW, maxW]).range([1.2, 10]).clamp(true);
      var edgeOpacity = d3.scaleLinear().domain([minW, maxW]).range([0.56,0.79]).clamp(true);
    
      var degrees = nodes.map(function(d){ return +d.degree || 0; });
      var minD = d3.min(degrees) || 0;
      var maxD = d3.max(degrees) || 1;
      var nodeRadius = d3.scaleSqrt().domain([minD, maxD]).range([6, 11]).clamp(true);
      function R(d){ return nodeRadius(+d.degree || 0); }
    
      var edgeLayer = g.append("g").attr("class","edges");
      var nodeLayer = g.append("g").attr("class","nodes");
      var labelLayer = g.append("g").attr("class","labels");
      var edgeLabelLayer = g.append("g").attr("class","edge-labels");
    
      var edge = edgeLayer.selectAll("path")
        .data(links).join("path")
        .attr("class","edge")
        .attr("id", function(_,i){ return "e"+i; })
        .attr("stroke", function(d){ return d.color; })
        .attr("stroke-width", function(d){ return edgeWidth(+d.weight || 0); })
        .attr("fill","none")
        .attr("stroke-opacity", function(d){ return edgeOpacity(+d.weight || 0); });
    
      var edgeLabels = edgeLabelLayer.selectAll("text")
        .data(links).join("text")
        .attr("class","edge-label")
        .append("textPath")
        .attr("href", function(_,i){ return "#e"+i; })
        .attr("startOffset","50%")
        .attr("text-anchor","middle")
        .text(function(d){ return d.weight ? String(d.weight) : ""; });
    
      var node = nodeLayer.selectAll("g.node")
        .data(nodes, function(d){ return d.id; })
        .join(function(enter){
          var g = enter.append("g").attr("class","node");
          g.append("circle")
            .attr("r", function(d){ return R(d); })
            .attr("fill", function(d){ return d.color; })
            .attr("stroke", "#333")
            .attr("stroke-width", 0.17);
          return g;
        });
    
      var labels = labelLayer.selectAll("text")
        .data(nodes, function(d){ return d.id; })
        .join("text")
        .attr("class","label")
        .attr("text-anchor","middle")
        .attr("dy","-0.05em")
        .text(function(d){ return d.label; });
    
      var centerForce = d3.forceCenter(width/2, height/2);
      var sim = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(function(d){return d.id;}).distance(40).strength(0.6))
        .force("charge", d3.forceManyBody().strength(-60))
        .force("collide", d3.forceCollide().radius(function(d){ return R(d)+6; }).iterations(2))
        .force("center", centerForce)
        .on("tick", ticked)
        .on("end", maybeFit);
    
      var fitted = false, fitTimeout = setTimeout(function(){ maybeFit(); }, 1000);
    
      function ticked(){
        edge.attr("d", function(d){ return "M"+d.source.x+","+d.source.y+" L"+d.target.x+","+d.target.y; });
        node.attr("transform", function(d){ return "translate("+d.x+", "+d.y+")"; });
        labels.attr("x", function(d){ return d.x; }).attr("y", function(d){ return d.y; });
      }
    
      function maybeFit(){
        if (fitted) return;
        fitted = true; clearTimeout(fitTimeout);
        var xs = nodes.map(function(d){ return d.x; }), ys = nodes.map(function(d){ return d.y; });
        var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
        var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
        var w = Math.max(1, maxX - minX), h = Math.max(1, maxY - minY);
        var margin = 40;
        var kx = (width  - margin*2) / w;
        var ky = (height - margin*2) / h;
        var scale = Math.max(0.2, Math.min(3, Math.min(kx, ky)));
        var tx = (width  - scale*(minX + maxX)) / 2;
        var ty = (height - scale*(minY + maxY)) / 2;
        svg.transition().duration(600)
          .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
      }
    
      node.call(d3.drag()
        .on("start", function(ev, d){ if (!ev.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag",  function(ev, d){ d.fx = ev.x; d.fy = ev.y; })
        .on("end",   function(ev, d){ if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
      );
    
      var selectedId = null;
      function neighborSet(id){
        var nei = new Set([id]);
        links.forEach(function(e){
          var s = (typeof e.source === 'object') ? e.source.id : e.source;
          var t = (typeof e.target === 'object') ? e.target.id : e.target;
          if (s === id) nei.add(t);
          if (t === id) nei.add(s);
        });
        return nei;
      }
    
      function renderSelection(){
        if (!selectedId){
          node.classed("selected", false);
          node.classed("dimmed", false);
          labels.classed("dimmed", false);
          edge.classed("highlight", false).classed("dimmed", false);
          edgeLabels.classed("dimmed", false);
          return;
        }
        var keep = neighborSet(selectedId);
        node.classed("selected", function(d){ return d.id === selectedId; })
            .classed("dimmed", function(d){ return !keep.has(d.id); });
        labels.classed("dimmed", function(d){ return !keep.has(d.id); });
        edge.classed("highlight", function(d){
              var s = (typeof d.source === 'object') ? d.source.id : d.source;
              var t = (typeof d.target === 'object') ? d.target.id : d.target;
              return s === selectedId || t === selectedId;
            })
            .classed("dimmed", function(d){
              var s = (typeof d.source === 'object') ? d.source.id : d.source;
              var t = (typeof d.target === 'object') ? d.target.id : d.target;
              return !(s === selectedId || t === selectedId);
            });
        edgeLabels.classed("dimmed", function(d){
          var s = (typeof d.source === 'object') ? d.source.id : d.source;
          var t = (typeof d.target === 'object') ? d.target.id : d.target;
          return !(s === selectedId || t === selectedId);
        });
      }
    
      function fillInfo(d){
        var pane = document.getElementById("info-pane");
        var campos = {
          "Nome": d.label,
          "Instituição": d.instituicao,
          "CV": d.url,
          "Atualização do CV": d.atualizacaoCV,
          "Período": d.periodo,
          "Rótulo": d.rotulo,
          "Primeira Grande Área": d.nomePrimeiraGrandeArea,
          "Primeira Área": d.nomePrimeiraArea,
          "Publicações em coautoria": d.publicacoesEmCoautoria,
          "Número de colaboradores": d.degree,
          "Artigos em periódicos": d.artigosPeriodicos,
          "Artigos em eventos": d.artigosEventos,
          "Capítulos de livro": d.capitulosDeLivros,
          "Livros": d.livros,
          "Endereço": d.enderecoProfissional
        };
        var html = "<h4>"+(d.label || d.id)+"</h4><ul>";
        Object.keys(campos).forEach(function(k){
          var v = campos[k];
          if (v === undefined || v === null || v === "") return;
          if (k === "CV"){
            html += "<li><strong>"+k+":</strong> <a href=\""+v+"\" target=\"_blank\" rel=\"noopener\">"+v+"</a></li>";
          } else {
            html += "<li><strong>"+k+":</strong> "+v+"</li>";
          }
        });
        html += "</ul>";
        pane.innerHTML = html;
      }
    
      function selectNodeById(id){
        var d = nodes.find(function(n){ return n.id === id; });
        if (!d) return;
        selectedId = d.id; fillInfo(d); renderSelection();
        var t = d3.zoomTransform(svg.node());
        var scale = Math.max(1.2, t.k);
        var x = width/2 - d.x * scale;
        var y = height/2 - d.y * scale;
        svg.transition().duration(600).call(zoom.transform, d3.zoomIdentity.translate(x, y).scale(scale));
      }
      node.on("click", function(_, d){ selectNodeById(d.id); });
    
      function norm(s){ return (s||"").toString().normalize("NFD").replace(/\p{Diacritic}/gu,"").toLowerCase().trim(); }
      function searchAndSelect(q){
        var nq = norm(q); if (!nq) return;
        var hit = nodes.find(function(n){ return norm(n.label) === nq || norm(n.id) === nq; });
        if (!hit) hit = nodes.find(function(n){ return norm(n.label).indexOf(nq) >= 0; });
        if (hit) selectNodeById(hit.id);
      }
      document.getElementById("btnSearch").addEventListener("click", function(){
        searchAndSelect(document.getElementById("searchBox").value);
      });
      document.getElementById("searchBox").addEventListener("keydown", function(ev){
        if (ev.key === "Enter") searchAndSelect(ev.target.value);
      });
      document.getElementById("btnClear").addEventListener("click", function(){
        selectedId = null; renderSelection();
        document.getElementById("info-pane").innerHTML =
          "<h4>Informação do Pesquisador</h4><p>Clique em um nó (ou use a busca) para ver detalhes aqui.</p>";
      });
    
      var labelsVisible = true;
      var btnToggle = document.getElementById("btnToggleLabels");
      function applyLabelsVisibility(){
        labelLayer.classed("hidden", !labelsVisible);
        d3.select(".edge-labels").classed("hidden", !labelsVisible);
      }
      btnToggle.addEventListener("click", function(){
        labelsVisible = !labelsVisible;
        btnToggle.textContent = labelsVisible ? "Ocultar rótulos" : "Mostrar rótulos";
        applyLabelsVisibility();
      });
      applyLabelsVisibility();
    
      // legenda (cores por rótulo)
      var byRotulo = d3.rollup(nodes, function(v){ return v[0].color; }, function(d){ return d.rotulo || "Sem rótulo"; });
      var legendData = Array.from(byRotulo, function(entry){ return {rotulo: entry[0], color: entry[1]}; });
      var legend = d3.select("#legend");
      legend.selectAll("span.item")
        .data(legendData)
        .join("span")
        .attr("class","item")
        .html(function(d){ return '<span class="swatch" style="background:'+d.color+'"></span>'+d.rotulo; });
    
      // refit ao redimensionar
      var ro = new ResizeObserver(function(){
        var b = getBox();
        width = b.width; height = b.height;
        centerForce = d3.forceCenter(width/2, height/2);
        sim.force("center", centerForce).alpha(0.05).restart();
        fitted = false; maybeFit();
      });
      ro.observe(document.getElementById("viz-container"));
    </script>
    """
    
        # 5) TABELAS: VÉRTICES + ARESTAS (com tooltip + ellipsis) — Tabulator
        s += """
    <hr style="margin:1.25rem 0">
    
    <h3>Vértices</h3>
    <p>Esta tabela lista todos os atributos usados para compor os vértices do grafo acima.</p>
    <div class="sl-controls">
      <button id="vert-csv">⬇️ CSV</button>
      <button id="vert-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-vertices" class="sl-tabela"></div>
    
    <h3 style="margin-top:1.5rem;">Arestas (pares de membros)</h3>
    <p>Veja quais pares de membros mais colaboram e quantos colaboradores em comum possuem.</p>
    <div class="sl-controls">
      <button id="edge-csv">⬇️ CSV</button>
      <button id="edge-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-arestas" class="sl-tabela"></div>
    
    <!-- Tabulator -->
    <link href="css/tabulator_site.min.css" rel="stylesheet" />
    <link href="css/tabulator-scriplattes.css" rel="stylesheet" />
    <script src="js/tabulator.min.js"></script>
    <script src="js/xlsx.full.min.js"></script>
    
    <script>
      // Dados vindos dos blocos anteriores
      var DATA_VERT  = (window.__VERTEX_TABLE_DATA__ || []);
      var DATA_EDGES = (window.__EDGE_TABLE_DATA__  || []);
    
      // Heurística de altura (evita rolagem infinita)
      function heightFor(n){
        if (n <= 12) return "auto";
        if (n <= 60) return "40vh";
        return "60vh";
      }
      var HEIGHT_VERT = heightFor(DATA_VERT.length);
      var HEIGHT_EDG  = heightFor(DATA_EDGES.length);
    
      const LANG_PT = {
        "pt-br": {
          "pagination": {
            "first":"«","first_title":"Primeira",
            "last":"»","last_title":"Última",
            "prev":"‹","prev_title":"Anterior",
            "next":"›","next_title":"Próxima"
          },
          "headerFilters": { "default":"⎯ Filtrar ⎯" }
        }
      };
    
      // Ordenação por data BR via campo auxiliar yyyymmdd
      function sortDateBR(a, b, aRow, bRow) {
        var av = (aRow && aRow.getData && aRow.getData().atualizacao_num) || 0;
        var bv = (bRow && bRow.getData && bRow.getData().atualizacao_num) || 0;
        return av - bv;
      }
    
      // Formatter de link com title (tooltip no <a>) — usado na coluna "Nome" dos vértices
      function linkWithTitle(cell) {
        const data = cell.getData();
        const url = String(data.url || "#");
        const label = String(cell.getValue() ?? "");
        const a = document.createElement("a");
        a.href = url; a.textContent = label; a.target = "_blank"; a.rel = "noopener"; a.title = label;
        return a;
      }
    
      // Helper para criar Tabulator com tooltips + ellipsis
      function createTable(el, data, columns, initialSort, height){
        const base = {
          data,
          layout: "fitColumns",
          responsiveLayout: "collapse",
          pagination: "local",
          paginationSize: 50,
          paginationSizeSelector: [10, 25, 50, 100, 200, 500],
          movableColumns: true,
          initialSort,
          headerFilterLiveFilter: true,
          columns,
          locale: true, langs: LANG_PT, locale: "pt-br",
          tooltips: true
        };
        if (height !== "auto") base.height = height;
        return new Tabulator(el, base);
      }
    
      // === VÉRTICES ===
      (function(){
        const columns = [
          { title:"ID", field:"id", headerFilter:"input", tooltip:true },
          { title:"Nome", field:"nome", formatter: linkWithTitle,
            headerFilter:"input", widthGrow:2, tooltip:true },
          { title:"Instituição", field:"instituicao", headerFilter:"input", tooltip:true },
          { title:"Atualização CV", field:"atualizacao", headerFilter:"input", sorter: sortDateBR, tooltip:true },
          { title:"Período", field:"periodo", headerFilter:"input", tooltip:true },
          { title:"Rótulo", field:"rotulo", headerFilter:"input", tooltip:true },
          { title:"Grande área", field:"grande_area", headerFilter:"input", tooltip:true },
          { title:"Área", field:"area", headerFilter:"input", tooltip:true },
          { title:"Publicações em coautoria", field:"publicacoesEmCoautoria", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Nº colaboradores (grau)", field:"degree", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Artigos em periódicos", field:"artigosPeriodicos", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Artigos em eventos", field:"artigosEventos", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Capítulos de livro", field:"capitulosDeLivros", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Livros", field:"livros", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Endereço", field:"enderecoProfissional", headerFilter:"input", widthGrow:2, tooltip:true }
        ];
        const sort = [{ column:"degree", dir:"desc" }];
        const t = createTable("#tabela-vertices", DATA_VERT, columns, sort, HEIGHT_VERT);
        document.getElementById("vert-csv").onclick  = () => t.download("csv",  "vertices_campos.csv", { bom:true });
        document.getElementById("vert-xlsx").onclick = () => t.download("xlsx", "vertices_campos.xlsx", { sheetName:"Vértices" });
      })();
    
      // === ARESTAS (coluna única "Aresta") ===
      (function(){
        const columns = [
          { title:"Aresta", field:"aresta", headerFilter:"input", widthGrow:3, tooltip:true },
          { title:"Número de colaborações", field:"colabs", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true },
          { title:"Nº de colaboradores em comum", field:"comuns", hozAlign:"right", sorter:"number", headerFilter:"input", tooltip:true }
        ];
        const sort = [{ column:"colabs", dir:"desc" }, { column:"comuns", dir:"desc" }];
        const t = createTable("#tabela-arestas", DATA_EDGES, columns, sort, HEIGHT_EDG);
        document.getElementById("edge-csv").onclick  = () => t.download("csv",  "arestas_colaboracoes.csv", { bom:true });
        document.getElementById("edge-xlsx").onclick = () => t.download("xlsx", "arestas_colaboracoes.xlsx", { sheetName:"Arestas" });
      })();
    </script>
    """
    
        # injeta o JSON do grafo no placeholder
        s = s.replace('__GRAPH_JS__', graph_js)
    
        # 6) fim
        s += self.paginaBottom()
        self.salvarPagina(f"grafoDeColaboracoes{self.extensaoPagina}", s)
    

      
    def gerar_pagina_de_membros(self):   
        import json, re
    
        def _s(val):
            return '' if val is None else str(val)
    
        def _len(x):
            try:
                return int(len(x))
            except Exception:
                return 0
    
        def _date_ddmmyyyy_only(texto):
            """
            Extrai 'dd/mm/yyyy' de uma string (ex.: '23/09/2024 12:30:00')
            e devolve (dd/mm/yyyy, yyyymmdd_int). Em falha, ('', 0).
            """
            s = _s(texto)
            m = re.search(r'(\d{2})/(\d{2})/(\d{4})', s)
            if not m:
                return '', 0
            d, mth, y = m.group(1), m.group(2), m.group(3)
            try:
                ymd = int(y) * 10000 + int(mth) * 100 + int(d)
            except Exception:
                ymd = 0
            return f"{d}/{mth}/{y}", ymd
    
        n_membros = _len(getattr(self.grupo, "listaDeMembros", []))
        # Altura adaptativa
        if n_membros <= 20:
            table_height = "auto"
        elif n_membros <= 70:
            table_height = "70vh"
        else:
            table_height = "90vh"
    
        s = self.pagina_top()
    
        # CSS/JS do Tabulator + tema local
        s += """
    <link href="css/tabulator_site.min.css" rel="stylesheet" />
    <link href="css/tabulator-scriplattes.css" rel="stylesheet" />
    <script src="js/tabulator.min.js"></script>
    <script src="js/xlsx.full.min.js"></script>
    
    <style>
    /* Ellipsis nas células: mostra "..." e deixa o tooltip trabalhar */
    #tabela-membros .tabulator-cell {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    </style>
    """
    
        # -------------------------
        # Dados para a tabela
        # -------------------------
        membros_data = []
        for membro in self.grupo.listaDeMembros:
            # mantém a geração da página individual
            self.gerar_pagina_individual_de_membro(membro)
    
            nome   = _s(getattr(membro, "nomeCompleto", ""))
            rotulo = _s(getattr(membro, "rotulo", ""))
            bolsa  = _s(getattr(membro, "bolsaProdutividade", ""))
            periodo = _s(getattr(membro, "periodo", ""))
    
            atual_str, atual_num = _date_ddmmyyyy_only(getattr(membro, "atualizacaoCV", ""))
    
            membros_data.append({
                "nome": nome,
                "url": f"membro-{_s(getattr(membro, 'idLattes', ''))}.html",
                "id_lattes": _s(getattr(membro, 'idLattes', '')),
                "rotulo_grupo": rotulo,  
                "bolsa": bolsa,
                "periodo": periodo,
                "atualizacao": atual_str,
                "atualizacao_num": atual_num,  # usado para ordenar
                "grande_area": _s(getattr(membro, "nomePrimeiraGrandeArea", "")),
                "area": _s(getattr(membro, "nomePrimeiraArea", "")),
                "instituicao": _s(getattr(membro, "instituicao", "")),
            })
    
        s += """
    <h3>Lista de membros</h3>
    <div class="sl-controls">
      <button id="membros-csv">⬇️ CSV</button>
      <button id="membros-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-membros" class="sl-tabela" id="tabela-membros"></div>
    """
    
        # -------------------------
        # Script Tabulator
        # -------------------------
        s += f"""
    <script>
    const DATA_MEMBROS = {json.dumps(membros_data, ensure_ascii=False)};
    const TABLE_HEIGHT = "{table_height}"; // "auto" | "70vh" | "90vh"
    
    const LANG_PT = {{
      "pt-br": {{
        "pagination": {{
          "first":"«","first_title":"Primeira",
          "last":"»","last_title":"Última",
          "prev":"‹","prev_title":"Anterior",
          "next":"›","next_title":"Próxima"
        }},
        "headerFilters": {{ "default":"⎯ Filtrar ⎯" }}
      }}
    }};
    
    // Ordenador para data BR usando campo auxiliar yyyymmdd (numérico)
    function sortDateBR(a, b, aRow, bRow, column, dir, sorterParams) {{
      const av = aRow?.getData()?.atualizacao_num ?? 0;
      const bv = bRow?.getData()?.atualizacao_num ?? 0;
      return av - bv;
    }}
    
    // Formatter de link com title (tooltip no próprio <a>)
    function linkWithTitle(cell, formatterParams, onRendered) {{
      const data = cell.getData();
      const url = data && data.url ? String(data.url) : "#";
      const label = String(cell.getValue() ?? "");
      const a = document.createElement("a");
      a.href = url;
      a.textContent = label;
      a.target = "_blank";
      a.rel = "noopener";
      a.title = label; // <-- tooltip no link
      return a;
    }}
    
    function createTable(el, data, columns, initialSort) {{
      const base = {{
        data,
        layout: "fitColumns",
        responsiveLayout: "collapse",
        pagination: "local",
        paginationSize: 50,
        paginationSizeSelector: [10, 25, 50, 100, 200, 500],
        movableColumns: true,
        initialSort,
        headerFilterLiveFilter: true,
        columns,
        locale: true, langs: LANG_PT, locale: "pt-br",
        tooltips: true    // <-- tooltip global (para colunas sem link)
      }};
      if (TABLE_HEIGHT !== "auto") {{
        base.height = TABLE_HEIGHT;
      }}
      return new Tabulator(el, base);
    }}
    
    document.addEventListener("DOMContentLoaded", function(){{
      const columns = [
        // Nome com link + title no próprio <a>
        {{ title:"Nome", field:"nome", formatter: linkWithTitle,
           headerFilter:"input", widthGrow:3, tooltip:true }},
    
        // Demais colunas (tooltip global já cobre)
        {{ title:"ID Lattes", field:"id_lattes", headerFilter:"input", tooltip:true }},
        {{ title:"Rótulo/Grupo", field:"rotulo_grupo", headerFilter:"input", tooltip:true }},
        {{ title:"Bolsa CNPq", field:"bolsa", headerFilter:"input", tooltip:true }},
        {{ title:"Período de análise individual", field:"periodo", headerFilter:"input", tooltip:true }},
        {{ title:"Data de atualização do CV", field:"atualizacao", headerFilter:"input", sorter: sortDateBR, tooltip:true }},
        {{ title:"Grande área", field:"grande_area", headerFilter:"input", tooltip:true }},
        {{ title:"Área", field:"area", headerFilter:"input", tooltip:true }},
        {{ title:"Instituição", field:"instituicao", headerFilter:"input", tooltip:true }},
      ];
    
      const t = createTable("#tabela-membros", DATA_MEMBROS, columns, [{{ column: "nome", dir: "asc" }}]);
    
      document.getElementById("membros-csv").onclick  = () => t.download("csv",  "lista_membros.csv", {{ bom:true }});
      document.getElementById("membros-xlsx").onclick = () => t.download("xlsx", "lista_membros.xlsx", {{ sheetName:"Membros" }});
    }});
    </script>
    """
        s += self.paginaBottom()
        self.salvarPagina("membros" + self.extensaoPagina, s)
             
 
    def gerar_pagina_de_metricas(self):   
        def _s(val):
            return '' if val is None else str(val)
    
        def _int(n):
            try:
                return int(n)
            except Exception:
                return 0
    
        def _len(x):
            try:
                return int(len(x))
            except Exception:
                return 0
    
        def _date_ddmmyyyy_only(texto):
            """
            Extrai 'dd/mm/yyyy' de uma string (ex.: '23/09/2024 12:30:00')
            e devolve (dd/mm/yyyy, yyyymmdd_int). Em falha, ('', 0).
            """
            s = _s(texto)
            m = re.search(r'(\d{2})/(\d{2})/(\d{4})', s)
            if not m:
                return '', 0
            d, mth, y = m.group(1), m.group(2), m.group(3)
            try:
                ymd = int(y) * 10000 + int(mth) * 100 + int(d)
            except Exception:
                ymd = 0
            return f"{d}/{mth}/{y}", ymd
    
        n_membros = _len(getattr(self.grupo, "listaDeMembros", []))
        # altura: auto | 40vh | 60vh
        if n_membros <= 12:
            table_height = "auto"
        elif n_membros <= 60:
            table_height = "40vh"
        else:
            table_height = "60vh"
    
        s = self.pagina_top()
    
        # Includes + ellipsis CSS
        s += """
    <link href="css/tabulator_site.min.css" rel="stylesheet" />
    <link href="css/tabulator-scriplattes.css" rel="stylesheet" />
    <script src="js/tabulator.min.js"></script>
    <script src="js/xlsx.full.min.js"></script>
    
    <style>
    /* Ellipsis nas três tabelas */
    #tabela-producao .tabulator-cell,
    #tabela-orientacoes .tabulator-cell,
    #tabela-projetos .tabulator-cell {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    </style>
    """
    
        # ======== DADOS ========
        producao, orientacoes, projetos = [], [], []
    
        for membro in self.grupo.listaDeMembros:
            bolsa  = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = _s(membro.rotulo)
            nome   = _s(membro.nomeCompleto)
            atual_str, atual_num = _date_ddmmyyyy_only(getattr(membro, "atualizacaoCV", ""))
    
            qtd_pub_periodicos = _len(getattr(membro, "listaArtigoEmPeriodico", []))
            qtd_pub_livros     = _len(getattr(membro, "listaLivroPublicado", []))
            qtd_pub_capit      = _len(getattr(membro, "listaCapituloDeLivroPublicado", []))
            qtd_pub_congr      = _len(getattr(membro, "listaTrabalhoCompletoEmCongresso", []))
            qtd_pub_resumos    = _len(getattr(membro, "listaResumoEmCongresso", [])) + _len(getattr(membro, "listaResumoExpandidoEmCongresso", []))
            qtd_pub_aceitos    = _len(getattr(membro, "listaArtigoAceito", []))
    
            qtd_tec_soft_pat   = _len(getattr(membro, "listaSoftwareComPatente", []))
            qtd_tec_soft_sem   = _len(getattr(membro, "listaSoftwareSemPatente", []))
            qtd_tec_prod       = _len(getattr(membro, "listaProdutoTecnologico", []))
            qtd_tec_proc       = _len(getattr(membro, "listaProcessoOuTecnica", []))
            qtd_tec_trab       = _len(getattr(membro, "listaTrabalhoTecnico", []))
            qtd_tec_outros     = _len(getattr(membro, "listaOutroTipoDeProducaoTecnica", []))
    
            qtd_artistica      = _len(getattr(membro, "listaProducaoArtistica", []))
    
            pb_total  = (qtd_pub_periodicos + qtd_pub_livros + qtd_pub_capit +
                         qtd_pub_congr + qtd_pub_resumos + qtd_pub_aceitos)
            tec_total = (qtd_tec_soft_pat + qtd_tec_soft_sem + qtd_tec_prod +
                         qtd_tec_proc + qtd_tec_trab + qtd_tec_outros)
            art_total = qtd_artistica
    
            producao.append({
                "nome": nome,
                "url": f"membro-{_s(getattr(membro, 'idLattes', ''))}.html",
                "rotulo": rotulo,
                "bolsa": _s(bolsa),
                "periodo": _s(getattr(membro, "periodo", "")),
                "atualizacao": atual_str,
                "atualizacao_num": _int(atual_num),
                "grande_area": _s(getattr(membro, "nomePrimeiraGrandeArea", "")),
                "area": _s(getattr(membro, "nomePrimeiraArea", "")),
    
                "pb_total": _int(pb_total),
                "periodicos": _int(qtd_pub_periodicos),
                "livros": _int(qtd_pub_livros),
                "capitulos": _int(qtd_pub_capit),
                "congressos": _int(qtd_pub_congr),
                "resumos": _int(qtd_pub_resumos),
                "aceitos": _int(qtd_pub_aceitos),
    
                "tec_total": _int(tec_total),
                "art_total": _int(art_total),
            })
    
        for membro in self.grupo.listaDeMembros:
            bolsa  = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = _s(membro.rotulo)
            nome   = _s(membro.nomeCompleto)
            atual_str, atual_num = _date_ddmmyyyy_only(getattr(membro, "atualizacaoCV", ""))
    
            concl_posdoc = _len(getattr(membro, "listaOCSupervisaoDePosDoutorado", []))
            concl_dout   = _len(getattr(membro, "listaOCTeseDeDoutorado", []))
            concl_mest   = _len(getattr(membro, "listaOCDissertacaoDeMestrado", []))
            concl_espec  = _len(getattr(membro, "listaOCMonografiaDeEspecializacao", []))
            concl_tcc    = _len(getattr(membro, "listaOCTCC", []))
            concl_ic     = _len(getattr(membro, "listaOCIniciacaoCientifica", []))
            concl_total  = concl_posdoc + concl_dout + concl_mest + concl_espec + concl_tcc + concl_ic
    
            and_posdoc   = _len(getattr(membro, "listaOASupervisaoDePosDoutorado", []))
            and_dout     = _len(getattr(membro, "listaOATeseDeDoutorado", []))
            and_mest     = _len(getattr(membro, "listaOADissertacaoDeMestrado", []))
            and_espec    = _len(getattr(membro, "listaOAMonografiaDeEspecializacao", []))
            and_tcc      = _len(getattr(membro, "listaOATCC", []))
            and_ic       = _len(getattr(membro, "listaOAIniciacaoCientifica", []))
            and_total    = and_posdoc + and_dout + and_mest + and_espec + and_tcc + and_ic
    
            orientacoes.append({
                "nome": nome,
                "url": f"membro-{_s(getattr(membro, 'idLattes', ''))}.html",
                "rotulo": rotulo,
                "bolsa": _s(bolsa),
                "periodo": _s(getattr(membro, "periodo", "")),
                "atualizacao": atual_str,
                "atualizacao_num": _int(atual_num),
                "grande_area": _s(getattr(membro, "nomePrimeiraGrandeArea", "")),
                "area": _s(getattr(membro, "nomePrimeiraArea", "")),
    
                "concl_total": _int(concl_total),
                "concl_posdoc": _int(concl_posdoc),
                "concl_dout": _int(concl_dout),
                "concl_mest": _int(concl_mest),
                "concl_espec": _int(concl_espec),
                "concl_tcc": _int(concl_tcc),
                "concl_ic": _int(concl_ic),
    
                "and_total": _int(and_total),
                "and_posdoc": _int(and_posdoc),
                "and_dout": _int(and_dout),
                "and_mest": _int(and_mest),
                "and_espec": _int(and_espec),
                "and_tcc": _int(and_tcc),
                "and_ic": _int(and_ic),
            })
    
        for membro in self.grupo.listaDeMembros:
            bolsa  = membro.bolsaProdutividade if membro.bolsaProdutividade else ''
            rotulo = _s(membro.rotulo)
            nome   = _s(membro.nomeCompleto)
            atual_str, atual_num = _date_ddmmyyyy_only(getattr(membro, "atualizacaoCV", ""))
    
            projetos.append({
                "nome": nome,
                "url": f"membro-{_s(getattr(membro, 'idLattes', ''))}.html",
                "rotulo": rotulo,
                "bolsa": _s(bolsa),
                "periodo": _s(getattr(membro, "periodo", "")),
                "atualizacao": atual_str,
                "atualizacao_num": _int(atual_num),
                "grande_area": _s(getattr(membro, "nomePrimeiraGrandeArea", "")),
                "area": _s(getattr(membro, "nomePrimeiraArea", "")),
    
                "projetos":   _len(getattr(membro, "listaProjetoDePesquisa", [])),
                "premios":    _len(getattr(membro, "listaPremioOuTitulo", [])),
                "part_event": _len(getattr(membro, "listaParticipacaoEmEvento", [])),
                "org_event":  _len(getattr(membro, "listaOrganizacaoDeEvento", [])),
            })
    
        dados_js = {
            "producao":    producao,
            "orientacoes": orientacoes,
            "projetos":    projetos,
        }
    
        # ======== HTML + botões ========
        s += """
    <h3>Métricas: Produções bibliográficas, técnicas e artísticas</h3>
    <div class="sl-controls">
      <button id="prod-csv">⬇️ CSV</button>
      <button id="prod-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-producao" class="sl-tabela"></div>
    
    <h3>Métricas: Orientações concluídas e em andamento</h3>
    <div class="sl-controls">
      <button id="ori-csv">⬇️ CSV</button>
      <button id="ori-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-orientacoes" class="sl-tabela"></div>
    
    <h3>Métricas: Projetos, prêmios e eventos</h3>
    <div class="sl-controls">
      <button id="proj-csv">⬇️ CSV</button>
      <button id="proj-xlsx">⬇️ XLSX</button>
    </div>
    <div id="tabela-projetos" class="sl-tabela"></div>
    """
    
        # ======== SCRIPT (sem f-string para evitar { } escapados) ========
        script = (
            "<script>\n"
            "const DATA = " + json.dumps(dados_js, ensure_ascii=False) + ";\n"
            "const TABLE_HEIGHT = \"" + table_height + "\";\n"
            "const LANG_PT = {\n"
            "  \"pt-br\": {\n"
            "    \"pagination\": {\n"
            "      \"first\":\"«\",\"first_title\":\"Primeira\",\n"
            "      \"last\":\"»\",\"last_title\":\"Última\",\n"
            "      \"prev\":\"‹\",\"prev_title\":\"Anterior\",\n"
            "      \"next\":\"›\",\"next_title\":\"Próxima\"\n"
            "    },\n"
            "    \"headerFilters\": { \"default\":\"⎯ Filtrar ⎯\" }\n"
            "  }\n"
            "};\n"
            "\n"
            "// Ordenação por data BR via campo auxiliar yyyymmdd\n"
            "function sortDateBR(a, b, aRow, bRow, column, dir, sorterParams) {\n"
            "  const av = aRow?.getData()?.atualizacao_num ?? 0;\n"
            "  const bv = bRow?.getData()?.atualizacao_num ?? 0;\n"
            "  return av - bv;\n"
            "}\n"
            "\n"
            "// Link com title (tooltip no <a>)\n"
            "function linkWithTitle(cell) {\n"
            "  const data = cell.getData();\n"
            "  const url = data && data.url ? String(data.url) : '#';\n"
            "  const label = String(cell.getValue() ?? '');\n"
            "  const a = document.createElement('a');\n"
            "  a.href = url; a.textContent = label; a.target = '_blank'; a.rel = 'noopener'; a.title = label;\n"
            "  return a;\n"
            "}\n"
            "\n"
            "function createTable(el, data, columns, initialSort) {\n"
            "  const base = {\n"
            "    data,\n"
            "    layout: 'fitColumns',\n"
            "    responsiveLayout: 'collapse',\n"
            "    pagination: 'local',\n"
            "    paginationSize: 50,\n"
            "    paginationSizeSelector: [10, 25, 50, 100, 200, 500],\n"
            "    movableColumns: true,\n"
            "    initialSort,\n"
            "    headerFilterLiveFilter: true,\n"
            "    columns,\n"
            "    locale: true, langs: LANG_PT, locale: 'pt-br',\n"
            "    tooltips: true\n"
            "  };\n"
            "  if (TABLE_HEIGHT !== 'auto') base.height = TABLE_HEIGHT;\n"
            "  return new Tabulator(el, base);\n"
            "}\n"
            "\n"
            "function mkTabelaProducao() {\n"
            "  const columns = [\n"
            "    { title:'Nome', field:'nome', formatter: linkWithTitle, headerFilter:'input', widthGrow:3, tooltip:true },\n"
            "    { title:'Rótulo', field:'rotulo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Bolsa CNPq', field:'bolsa', headerFilter:'input', tooltip:true },\n"
            "    { title:'Período', field:'periodo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Atualização CV', field:'atualizacao', headerFilter:'input', sorter: sortDateBR, tooltip:true },\n"
            "    { title:'Grande área', field:'grande_area', headerFilter:'input', tooltip:true },\n"
            "    { title:'Área', field:'area', headerFilter:'input', tooltip:true },\n"
            "    { title:'PB (total)', field:'pb_total', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Periódicos', field:'periodicos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Livros', field:'livros', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Capítulos', field:'capitulos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Congressos', field:'congressos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Resumos', field:'resumos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Aceitos', field:'aceitos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Técnica (total)', field:'tec_total', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Artística (total)', field:'art_total', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true }\n"
            "  ];\n"
            "  const t = createTable('#tabela-producao', DATA.producao, columns, [{ column: 'pb_total', dir: 'desc' }]);\n"
            "  document.getElementById('prod-csv').onclick  = () => t.download('csv',  'metricas_producao.csv', { bom:true });\n"
            "  document.getElementById('prod-xlsx').onclick = () => t.download('xlsx', 'metricas_producao.xlsx', { sheetName:'Produção' });\n"
            "  return t;\n"
            "}\n"
            "\n"
            "function mkTabelaOrientacoes() {\n"
            "  const columns = [\n"
            "    { title:'Nome', field:'nome', formatter: linkWithTitle, headerFilter:'input', widthGrow:3, tooltip:true },\n"
            "    { title:'Rótulo', field:'rotulo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Bolsa CNPq', field:'bolsa', headerFilter:'input', tooltip:true },\n"
            "    { title:'Período', field:'periodo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Atualização CV', field:'atualizacao', headerFilter:'input', sorter: sortDateBR, tooltip:true },\n"
            "    { title:'Grande área', field:'grande_area', headerFilter:'input', tooltip:true },\n"
            "    { title:'Área', field:'area', headerFilter:'input', tooltip:true },\n"
            "    { title:'Concluídas (total)', field:'concl_total', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Pós-doc', field:'concl_posdoc', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Doutorado', field:'concl_dout', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Mestrado', field:'concl_mest', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Especialização', field:'concl_espec', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'TCC', field:'concl_tcc', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'IC', field:'concl_ic', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Em andamento (total)', field:'and_total', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Pós-doc', field:'and_posdoc', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Doutorado', field:'and_dout', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Mestrado', field:'and_mest', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Especialização', field:'and_espec', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'TCC', field:'and_tcc', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'IC', field:'and_ic', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true }\n"
            "  ];\n"
            "  const t = createTable('#tabela-orientacoes', DATA.orientacoes, columns, [{ column: 'concl_total', dir: 'desc' }]);\n"
            "  document.getElementById('ori-csv').onclick  = () => t.download('csv',  'metricas_orientacoes.csv', { bom:true });\n"
            "  document.getElementById('ori-xlsx').onclick = () => t.download('xlsx', 'metricas_orientacoes.xlsx', { sheetName:'Orientações' });\n"
            "  return t;\n"
            "}\n"
            "\n"
            "function mkTabelaProjetos() {\n"
            "  const columns = [\n"
            "    { title:'Nome', field:'nome', formatter: linkWithTitle, headerFilter:'input', widthGrow:3, tooltip:true },\n"
            "    { title:'Rótulo', field:'rotulo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Bolsa CNPq', field:'bolsa', headerFilter:'input', tooltip:true },\n"
            "    { title:'Período', field:'periodo', headerFilter:'input', tooltip:true },\n"
            "    { title:'Atualização CV', field:'atualizacao', headerFilter:'input', sorter: sortDateBR, tooltip:true },\n"
            "    { title:'Grande área', field:'grande_area', headerFilter:'input', tooltip:true },\n"
            "    { title:'Área', field:'area', headerFilter:'input', tooltip:true },\n"
            "    { title:'Projetos', field:'projetos', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Prêmios', field:'premios', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Participação em eventos', field:'part_event', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true },\n"
            "    { title:'Organização de eventos', field:'org_event', hozAlign:'right', headerFilter:'input', sorter:'number', tooltip:true }\n"
            "  ];\n"
            "  const t = createTable('#tabela-projetos', DATA.projetos, columns, [{ column: 'projetos', dir: 'desc' }]);\n"
            "  document.getElementById('proj-csv').onclick  = () => t.download('csv',  'metricas_projetos.csv', { bom:true });\n"
            "  document.getElementById('proj-xlsx').onclick = () => t.download('xlsx', 'metricas_projetos.xlsx', { sheetName:'Projetos' });\n"
            "  return t;\n"
            "}\n"
            "\n"
            "document.addEventListener('DOMContentLoaded', function(){\n"
            "  mkTabelaProducao();\n"
            "  mkTabelaOrientacoes();\n"
            "  mkTabelaProjetos();\n"
            "});\n"
            "</script>\n"
        )
    
        s += script
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
        (nPT6, lista_PT6, titulo_PT6) = self.gerar_lista_de_producoes_de_membro( membro.listaEntrevista , "Entrevistas, mesas redondas, programas e comentários na mídia" )

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

        #
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
        s += '<li><a href="#{}">{}</a> ({}) </li>'.format( 'PT6', titulo_PT6, nPT6 )
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
        s += '<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PT6', titulo_PT6, nPT6, lista_PT6)
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
