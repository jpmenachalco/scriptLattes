#!/usr/bin/python
# encoding: utf-8
# filename: parserLattes.py
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
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

import sys
from html.entities import name2codepoint
#from tidylib import tidy_document


# ---------------------------------------------------------------------------- #
from html.parser import HTMLParser
from .producoesUnitarias.formacaoAcademica import *
from .producoesUnitarias.areaDeAtuacao import *
from .producoesUnitarias.idioma import *
from .producoesUnitarias.premioOuTitulo import *
from .producoesUnitarias.projetoDePesquisa import *

from .producoesBibliograficas.artigoEmPeriodico import *
from .producoesBibliograficas.livroPublicado import *
from .producoesBibliograficas.capituloDeLivroPublicado import *
from .producoesBibliograficas.textoEmJornalDeNoticia import *
from .producoesBibliograficas.trabalhoCompletoEmCongresso import *
from .producoesBibliograficas.resumoExpandidoEmCongresso import *
from .producoesBibliograficas.resumoEmCongresso import *
from .producoesBibliograficas.artigoAceito import *
from .producoesBibliograficas.apresentacaoDeTrabalho import *
from .producoesBibliograficas.outroTipoDeProducaoBibliografica import *

from .producoesTecnicas.softwareComPatente import *
from .producoesTecnicas.softwareSemPatente import *
from .producoesTecnicas.produtoTecnologico import *
from .producoesTecnicas.processoOuTecnica import *
from .producoesTecnicas.trabalhoTecnico import *
from .producoesTecnicas.outroTipoDeProducaoTecnica import *

from .producoesArtisticas.producaoArtistica import *

from .orientacoes.orientacaoEmAndamento import *
from .orientacoes.orientacaoConcluida import *

from .eventos.organizacaoDeEvento import *
from .eventos.participacaoEmEvento import *

sys.tracebacklimit = 0

class ParserLattes(HTMLParser):

    identificador16 = ''
    item = None
    nomeCompleto = ''
    bolsaProdutividade = ''
    enderecoProfissional = ''
    sexo = ''
    nomeEmCitacoesBibliograficas = ''
    atualizacaoCV = ''
    foto = ''
    textoResumo = ''


    salvarIdentificador16 = None
    salvarNome = None
    salvarBolsaProdutividade = None
    salvarEnderecoProfissional = None
    salvarSexo = None
    salvarNomeEmCitacoes = None
    salvarAtualizacaoCV = None
    salvarTextoResumo = None
    salvarFormacaoAcademica = None
    salvarProjetoDePesquisa = None
    salvarAreaDeAtuacao = None
    salvarIdioma = None
    salvarPremioOuTitulo = None
    salvarItem = None
    salvarParticipacaoEmEvento = None
    salvarOrganizacaoDeEvento = None

    # novos atributos
    achouIdentificacao = None
    achouEndereco = None
    salvarParte1 = None
    salvarParte2 = None
    salvarParte3 = None
    achouProducoes = None
    achouProducaoEmCTA = None
    achouProducaoTecnica = None
    achouProducaoArtisticaCultural = None
    achouOutraProducaoArtisticaCultural = None
    achouBancas = None
    achouEventos = None
    achouOrientacoes = None
    achouOutrasInformacoesRelevantes = None
    spanInformacaoArtigo = None

    recuperarIdentificador16 = None


    achouGrupo = None
    achouEnderecoProfissional = None
    achouSexo = None
    achouNomeEmCitacoes = None
    achouFormacaoAcademica = None
    achouProjetoDePesquisa = None
    achouAreaDeAtuacao = None
    achouIdioma = None
    achouPremioOuTitulo = None

    achouArtigoEmPeriodico = None
    achouLivroPublicado = None
    achouCapituloDeLivroPublicado = None
    achouTextoEmJornalDeNoticia = None
    achouTrabalhoCompletoEmCongresso = None
    achouResumoExpandidoEmCongresso = None
    achouResumoEmCongresso = None
    achouArtigoAceito = None
    achouApresentacaoDeTrabalho = None
    achouOutroTipoDeProducaoBibliografica = None

    achouSoftwareComPatente = None
    achouSoftwareSemPatente = None
    achouProdutoTecnologico = None
    achouProcessoOuTecnica = None
    achouTrabalhoTecnico = None
    achouOutroTipoDeProducaoTecnica = None

    achouPatente = None
    achouProgramaComputador = None
    achouDesenhoIndustrial = None
    achouPatenteRegistro = None


    achouProducaoArtistica = None

    achouOrientacoesEmAndamento	= None
    achouOrientacoesConcluidas = None
    achouSupervisaoDePosDoutorado = None
    achouTeseDeDoutorado = None
    achouDissertacaoDeMestrado = None
    achouMonografiaDeEspecializacao = None
    achouTCC = None
    achouIniciacaoCientifica = None
    achouOutroTipoDeOrientacao = None

    achouParticipacaoEmEvento = None
    achouOrganizacaoDeEvento = None

    procurarCabecalho = None
    partesDoItem = []

    listaIDLattesColaboradores = []
    listaFormacaoAcademica = []
    listaProjetoDePesquisa = []
    listaAreaDeAtuacao = []
    listaIdioma = []
    listaPremioOuTitulo = []

    listaArtigoEmPeriodico = []
    listaLivroPublicado = []
    listaCapituloDeLivroPublicado = []
    listaTextoEmJornalDeNoticia = []
    listaTrabalhoCompletoEmCongresso = []
    listaResumoExpandidoEmCongresso = []
    listaResumoEmCongresso = []
    listaArtigoAceito = []
    listaApresentacaoDeTrabalho = []
    listaOutroTipoDeProducaoBibliografica = []

    listaSoftwareComPatente = []
    listaSoftwareSemPatente = []
    listaProdutoTecnologico = []
    listaProcessoOuTecnica = []
    listaTrabalhoTecnico = []
    listaOutroTipoDeProducaoTecnica = []

    listaPatente = []
    listaProgramaComputador = []
    listaDesenhoIndustrial = []

    listaProducaoArtistica = []

    # Orientaççoes em andamento (OA)
    listaOASupervisaoDePosDoutorado = []
    listaOATeseDeDoutorado = []
    listaOADissertacaoDeMestrado = []
    listaOAMonografiaDeEspecializacao = []
    listaOATCC = []
    listaOAIniciacaoCientifica = []
    listaOAOutroTipoDeOrientacao = []

    # Orientações concluídas (OC)
    listaOCSupervisaoDePosDoutorado = []
    listaOCTeseDeDoutorado = []
    listaOCDissertacaoDeMestrado = []
    listaOCMonografiaDeEspecializacao = []
    listaOCTCC = []
    listaOCIniciacaoCientifica = []
    listaOCOutroTipoDeOrientacao = []

    # Eventos
    listaParticipacaoEmEvento = []
    listaOrganizacaoDeEvento = []

    # auxiliares
    doi = ''
    relevante = 0
    umaUnidade = 0
    idOrientando = None
    citado = 0
    complemento = ''


    # ------------------------------------------------------------------------ #
    def __init__(self, idMembro, cvLattesHTML):
        HTMLParser.__init__(self)

        # inicializacao obrigatoria
        self.idMembro = idMembro
        self.sexo = 'Masculino'
        self.nomeCompleto = '[Nome-nao-identificado]'

        self.item = ''
        self.issn = ''
        self.listaIDLattesColaboradores = []
        self.listaFormacaoAcademica = []
        self.listaProjetoDePesquisa = []
        self.listaAreaDeAtuacao = []
        self.listaIdioma = []
        self.listaPremioOuTitulo = []

        self.listaArtigoEmPeriodico = []
        self.listaLivroPublicado = []
        self.listaCapituloDeLivroPublicado = []
        self.listaTextoEmJornalDeNoticia = []
        self.listaTrabalhoCompletoEmCongresso = []
        self.listaResumoExpandidoEmCongresso = []
        self.listaResumoEmCongresso = []
        self.listaArtigoAceito = []
        self.listaApresentacaoDeTrabalho = []
        self.listaOutroTipoDeProducaoBibliografica = []

        self.listaSoftwareComPatente = []
        self.listaSoftwareSemPatente = []
        self.listaProdutoTecnologico = []
        self.listaProcessoOuTecnica = []
        self.listaTrabalhoTecnico = []
        self.listaOutroTipoDeProducaoTecnica = []

        self.listaPatente = []
        self.listaProgramaComputador = []
        self.listaDesenhoIndustrial = []

        self.listaProducaoArtistica = []

        self.listaOASupervisaoDePosDoutorado = []
        self.listaOATeseDeDoutorado = []
        self.listaOADissertacaoDeMestrado = []
        self.listaOAMonografiaDeEspecializacao = []
        self.listaOATCC = []
        self.listaOAIniciacaoCientifica = []
        self.listaOAOutroTipoDeOrientacao = []

        self.listaOCSupervisaoDePosDoutorado = []
        self.listaOCTeseDeDoutorado = []
        self.listaOCDissertacaoDeMestrado = []
        self.listaOCMonografiaDeEspecializacao = []
        self.listaOCTCC = []
        self.listaOCIniciacaoCientifica = []
        self.listaOCOutroTipoDeOrientacao = []

        self.listaParticipacaoEmEvento = []
        self.listaOrganizacaoDeEvento = []


        # inicializacao para evitar a busca exaustiva de algumas palavras-chave
        self.salvarAtualizacaoCV = 1
        self.salvarFoto = 1
        self.procurarCabecalho = 0
        self.achouGrupo = 0
        self.doi = ''
        self.relevante = 0
        self.idOrientando = ''
        self.complemento = ''

        # contornamos alguns erros do HTML da Plataforma Lattes
        cvLattesHTML = cvLattesHTML.replace("<![CDATA[","")
        cvLattesHTML = cvLattesHTML.replace("]]>","")
        cvLattesHTML = cvLattesHTML.replace("<x<","&lt;x&lt;")
        cvLattesHTML = cvLattesHTML.replace("<X<","&lt;X&lt;")

        # feed it! O tidy nao é mais necessario pois estamos em python3
        #cvLattesHTML = cvLattesHTML.encode('utf-8').decode('utf-8', 'replace')
        #cvLattesHTML, errors = tidy_document(cvLattesHTML, options={'numeric-entities':0, 'char-encoding': 'utf8', 'input-encoding': 'utf8'})
        #cvLattesHTML, errors = tidy_document(cvLattesHTML, options={'numeric-entities':1})
        #print(cvLattesHTML)

        ## tentativa errada (não previsível)
        # options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0)
        # cvLattesHTML = str(tidy.parseString(cvLattesHTML, **options)).decode("utf8")

        self.feed(cvLattesHTML)

    # ------------------------------------------------------------------------ #

    def parse_issn(self,url):
        s = url.find('issn=')
        if s == -1:
            return None
        e = url.find('&',s)
        if e == -1:
            return None

        issnvalue = url[s:e].split('=')
        issn = issnvalue[1]
        if len(issn) < 8: return
        issn = issn[:8]
        self.issn = issn[0:4]+'-'+issn[4:8]

    def handle_starttag(self, tag, attributes):

        if tag=='h2':
            for name, value in attributes:
                if name=='class' and value=='nome':
                    self.salvarNome = 1
                    self.item = ''
                    break

        if tag=='li':
            self.recuperarIdentificador16 = 1

        if tag=='p':
            for name, value in attributes:
                if name=='class' and value=='resumo':
                    self.salvarTextoResumo = 1
                    self.item = ''
                    break

        if tag=='span' and self.salvarNome:
            self.item = ''
            self.salvarBolsaProdutividade = 1
            self.salvarNome = 0

        if tag=='div':
            self.citado = 0

            for name, value in attributes:
                if name == 'cvuri':
                    self.parse_issn(value)


            for name, value in attributes:
                if name=='class' and value=='title-wrapper':
                    self.umaUnidade = 1
                    break

            for name, value in attributes:
                if name=='class' and (value=='transform' or value=='layout-cell-pad-5' or value=='layout-cell-pad-6' or value=='layout-cell layout-cell-11'): #update on Lattes HTML format 19/04/2024
                    if self.achouNomeEmCitacoes:
                        self.salvarNomeEmCitacoes = 1
                        self.item = ''

                    if self.achouSexo:
                        self.salvarSexo = 1
                        self.item = ''

                    if self.achouEnderecoProfissional:
                        self.salvarEnderecoProfissional = 1
                        self.item = ''

                    if self.salvarParte1:
                        self.salvarParte1 = 0
                        self.salvarParte2 = 1

                if name=='class' and (value=='layout-cell-pad-5 text-align-right' or value=='layout-cell-pad-6 text-align-right'): #update on Lattes HTML format 20/03/2024
                    self.item = ''
                    if self.achouFormacaoAcademica or self.achouAtuacaoProfissional or self.achouProjetoDePesquisa or self.achouMembroDeCorpoEditorial or self.achouRevisorDePeriodico or self.achouAreaDeAtuacao or self.achouIdioma or self.achouPremioOuTitulo or self.salvarItem:
                        self.salvarParte1 = 1
                        self.salvarParte2 = 0
                        if not self.salvarParte3:
                            self.partesDoItem = []

                if name == 'class' and (value == 'citacoes' or value == 'citado'):
                    self.citado = 1

                if name == 'cvuri' and self.citado:
                    self.citado = 0
                    self.complemento = value.replace("/buscatextual/servletcitacoes?", "")


        if tag=='h1' and self.umaUnidade:
            self.procurarCabecalho = 1

            self.achouIdentificacao = 0
            self.achouEndereco = 0
            self.achouFormacaoAcademica = 0
            self.achouAtuacaoProfissional = 0
            self.achouProjetoDePesquisa = 0
            self.achouMembroDeCorpoEditorial = 0
            self.achouRevisorDePeriodico = 0
            self.achouAreaDeAtuacao = 0
            self.achouIdioma = 0
            self.achouPremioOuTitulo = 0
            self.achouProducoes = 0
            #self.achouProducaoEmCTA = 0
            #self.achouProducaoTecnica = 0
            #self.achouProducaoArtisticaCultural = 0
            self.achouBancas = 0
            self.achouEventos = 0
            self.achouOrientacoes = 0
            self.achouOutrasInformacoesRelevantes = 0
            self.salvarItem = 0
            self.achouPatenteRegistro = 0

        if tag=='img':
            if self.salvarFoto:
                for name, value in attributes:
                    if name=='src' and 'servletrecuperafoto' in value:
                        self.foto = value
                        self.salvarFoto = 0
                        break

            if self.salvarItem:
                for name, value in attributes:
                    if name=='src' and 'ico_relevante' in value:
                        self.relevante = 1
                        break

                """for name,value in attributes:
                    if name=='data-issn':
                        if len(value) == 8:
                            self.issn = value[0:4]+'-'+value[4:8]
                        break
                """




        if tag=='br':
            self.item = self.item + ' '

        if tag=='span':
            if self.achouProducaoEmCTA:
                for name, value in attributes:
                    if name=='class' and value=='informacao-artigo':
                        self.spanInformacaoArtigo = 1

        if tag=='a':
            if self.salvarItem: # and self.achouArtigoEmPeriodico:
                for name, value in attributes:
                    if name=='href' and 'doi' in value:
                        self.doi = value
                        break

                    id = re.findall('http://lattes.cnpq.br/(\d{16})', value)
                    if name=='href' and len(id)>0:
                        self.listaIDLattesColaboradores.append(id[0])
                        if self.achouOrientacoesEmAndamento or self.achouOrientacoesConcluidas:
                            self.idOrientando = id[0]
                        break


    # ------------------------------------------------------------------------ #
    def handle_endtag(self, tag):
        # Informações do pesquisador (pre-cabecalho)
        if tag=='h2' and self.salvarNome:
            self.nomeCompleto = str(stripBlanks(self.item))
            self.salvarNome = 0
            self.item = ''

        if tag=='p':
            if self.salvarTextoResumo:
                self.textoResumo = stripBlanks(self.item)
                self.salvarTextoResumo = 0

        if tag=='span' and self.salvarBolsaProdutividade:
            self.bolsaProdutividade = stripBlanks(self.item)
            self.bolsaProdutividade = re.sub('Bolsista de Produtividade em Pesquisa do CNPq - ','', self.bolsaProdutividade)
            self.bolsaProdutividade = self.bolsaProdutividade.strip('()')
            self.salvarBolsaProdutividade = 0
            self.item = ''

        if tag=='span' and self.salvarIdentificador16 == 1:
            self.identificador16 = re.findall('http://lattes.cnpq.br/(\d{16})', value)
            self.salvarIdentificador16 = 0

        # Cabeçalhos
        if tag=='h1' and self.procurarCabecalho:
            self.procurarCabecalho = 0


        if tag=='div':
            if self.salvarNomeEmCitacoes:
                self.nomeEmCitacoesBibliograficas = stripBlanks(self.item)
                self.salvarNomeEmCitacoes = 0
                self.achouNomeEmCitacoes = 0
            if self.salvarSexo:
                self.sexo = stripBlanks(self.item)
                self.salvarSexo = 0
                self.achouSexo = 0
            if self.salvarEnderecoProfissional:
                self.enderecoProfissional = stripBlanks(self.item)
                self.enderecoProfissional = re.sub("\'", '', self.enderecoProfissional)
                self.enderecoProfissional = re.sub("\"", '', self.enderecoProfissional)
                self.salvarEnderecoProfissional = 0
                self.achouEnderecoProfissional = 0

            if (self.salvarParte1 and not self.salvarParte2) or (self.salvarParte2 and not self.salvarParte1) :
                if len(stripBlanks(self.item))>0:
                    self.partesDoItem.append(stripBlanks(self.item)) # acrescentamos cada celula da linha em uma lista!
                    self.item = ''

                if self.salvarParte2:
                    self.salvarParte1 = 0
                    self.salvarParte2 = 0

                    if self.achouFormacaoAcademica and len(self.partesDoItem)>=2:
                        iessimaFormacaoAcademica = FormacaoAcademica(self.partesDoItem) # criamos um objeto com a lista correspondentes às celulas da linha
                        self.listaFormacaoAcademica.append(iessimaFormacaoAcademica) # acrescentamos o objeto de FormacaoAcademica

                    #if self.achouAtuacaoProfissional:
                    #	print self.partesDoItem

                    if self.achouProjetoDePesquisa:
                        if not self.salvarParte3:
                            self.salvarParte3 = 1
                        else:
                            self.salvarParte3 = 0
                            if len(self.partesDoItem)>=3:
                                iessimoProjetoDePesquisa = ProjetoDePesquisa(self.idMembro, self.partesDoItem) # criamos um objeto com a lista correspondentes às celulas da linha
                                self.listaProjetoDePesquisa.append(iessimoProjetoDePesquisa) # acrescentamos o objeto de ProjetoDePesquisa

                    #if self.achouMembroDeCorpoEditorial:
                    #	print self.partesDoItem

                    #if self.achouRevisorDePeriodico:
                    #	print self.partesDoItem

                    if self.achouAreaDeAtuacao and len(self.partesDoItem)>=2:
                        iessimaAreaDeAtucao = AreaDeAtuacao(self.partesDoItem) # criamos um objeto com a lista correspondentes às celulas da linha
                        self.listaAreaDeAtuacao.append(iessimaAreaDeAtucao) # acrescentamos o objeto de AreaDeAtuacao

                    if self.achouIdioma and len(self.partesDoItem)>=2:
                        iessimoIdioma = Idioma(self.partesDoItem) # criamos um objeto com a lista correspondentes às celulas da linha
                        self.listaIdioma.append(iessimoIdioma) # acrescentamos o objeto de Idioma

                    if self.achouPremioOuTitulo and len(self.partesDoItem)>=2:
                        iessimoPremio = PremioOuTitulo(self.idMembro, self.partesDoItem) # criamos um objeto com a lista correspondentes às celulas da linha
                        self.listaPremioOuTitulo.append(iessimoPremio) # acrescentamos o objeto de PremioOuTitulo


                        # if self.achouPatenteRegistro:
                    #	#print "===>>>> PROCESSANDO PATENTE e REGISTRO"
                    #	if self.achouPatente:
                    #		iessimoItem = Patente(self.idMembro, self.partesDoItem, self.relevante)
                    #		self.listaPatente.append(iessimoItem)
                    #	if self.achouProgramaComputador:
                    #		iessimoItem = ProgramaComputador(self.idMembro, self.partesDoItem, self.relevante)
                    #		self.listaProgramaComputador.append(iessimoItem)
                    #	if self.achouDesenhoIndustrial:
                    #		iessimoItem = DesenhoIndustrial(self.idMembro, self.partesDoItem, self.relevante)
                    #		self.listaDesenhoIndustrial.append(iessimoItem)

                    if self.achouProducoes:
                        if self.achouProducaoEmCTA:
                            if self.achouArtigoEmPeriodico:
                                iessimoItem = ArtigoEmPeriodico(self.idMembro, self.partesDoItem, self.doi,
                                                                self.relevante, self.complemento)
                                self.listaArtigoEmPeriodico.append(iessimoItem)
                                self.doi = ''
                                self.issn = ''
                                self.relevante = 0
                                self.complemento = ''
    
                            if self.achouLivroPublicado:
                                iessimoItem = LivroPublicado(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaLivroPublicado.append(iessimoItem)
                                self.relevante = 0
    
                            if self.achouCapituloDeLivroPublicado:
                                iessimoItem = CapituloDeLivroPublicado(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaCapituloDeLivroPublicado.append(iessimoItem)
                                self.relevante = 0

                            if self.achouTextoEmJornalDeNoticia:
                                iessimoItem = TextoEmJornalDeNoticia(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaTextoEmJornalDeNoticia.append(iessimoItem)
                                self.relevante = 0

                            if self.achouTrabalhoCompletoEmCongresso:
                                iessimoItem = TrabalhoCompletoEmCongresso(self.idMembro, self.partesDoItem, self.doi,
                                                                          self.relevante)
                                self.listaTrabalhoCompletoEmCongresso.append(iessimoItem)
                                self.doi = ''
                                self.relevante = 0

                            if self.achouResumoExpandidoEmCongresso:
                                iessimoItem = ResumoExpandidoEmCongresso(self.idMembro, self.partesDoItem, self.doi,
                                                                         self.relevante)
                                self.listaResumoExpandidoEmCongresso.append(iessimoItem)
                                self.doi = ''
                                self.relevante = 0

                            if self.achouResumoEmCongresso:
                                iessimoItem = ResumoEmCongresso(self.idMembro, self.partesDoItem, self.doi,
                                                                self.relevante)
                                self.listaResumoEmCongresso.append(iessimoItem)
                                self.doi = ''
                                self.relevante = 0
    
                            if self.achouArtigoAceito:
                                iessimoItem = ArtigoAceito(self.idMembro, self.partesDoItem, self.doi, self.relevante)
                                self.listaArtigoAceito.append(iessimoItem)
                                self.doi = ''
                                self.relevante = 0

                            if self.achouApresentacaoDeTrabalho:
                                iessimoItem = ApresentacaoDeTrabalho(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaApresentacaoDeTrabalho.append(iessimoItem)
    
                            if self.achouOutroTipoDeProducaoBibliografica:
                                iessimoItem = OutroTipoDeProducaoBibliografica(self.idMembro, self.partesDoItem,
                                                                               self.relevante)
                                self.listaOutroTipoDeProducaoBibliografica.append(iessimoItem)


                        if self.achouProducaoTecnica:
                            if self.achouSoftwareComPatente:
                                iessimoItem = SoftwareComPatente(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaSoftwareComPatente.append(iessimoItem)
    
                            if self.achouSoftwareSemPatente:
                                iessimoItem = SoftwareSemPatente(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaSoftwareSemPatente.append(iessimoItem)

                            if self.achouProdutoTecnologico:
                                iessimoItem = ProdutoTecnologico(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaProdutoTecnologico.append(iessimoItem)
    
                            if self.achouProcessoOuTecnica:
                                iessimoItem = ProcessoOuTecnica(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaProcessoOuTecnica.append(iessimoItem)
    
                            if self.achouTrabalhoTecnico:
                                iessimoItem = TrabalhoTecnico(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaTrabalhoTecnico.append(iessimoItem)
    
                            if self.achouOutroTipoDeProducaoTecnica:
                                iessimoItem = OutroTipoDeProducaoTecnica(self.idMembro, self.partesDoItem,
                                                                         self.relevante)
                                self.listaOutroTipoDeProducaoTecnica.append(iessimoItem)

                        if self.achouProducaoArtisticaCultural:
                            if self.achouOutraProducaoArtisticaCultural:
                                iessimoItem = ProducaoArtistica(self.idMembro, self.partesDoItem, self.relevante)
                                self.listaProducaoArtistica.append(iessimoItem)


                    #if self.achouBancas:

                    if self.achouEventos:
                        if self.achouParticipacaoEmEvento:
                            self.listaParticipacaoEmEvento.append(ParticipacaoEmEvento(self.idMembro, self.partesDoItem))

                        if self.achouOrganizacaoDeEvento:
                            self.listaOrganizacaoDeEvento.append(OrganizacaoDeEvento(self.idMembro, self.partesDoItem))


                    if self.achouOrientacoes:
                        if self.achouOrientacoesEmAndamento:
                            if self.achouSupervisaoDePosDoutorado:
                                self.listaOASupervisaoDePosDoutorado.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouTeseDeDoutorado:
                                self.listaOATeseDeDoutorado.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouDissertacaoDeMestrado:
                                self.listaOADissertacaoDeMestrado.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouMonografiaDeEspecializacao:
                                self.listaOAMonografiaDeEspecializacao.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouTCC:
                                self.listaOATCC.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouIniciacaoCientifica:
                                self.listaOAIniciacaoCientifica.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouOutroTipoDeOrientacao:
                                self.listaOAOutroTipoDeOrientacao.append( OrientacaoEmAndamento(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''

                        if self.achouOrientacoesConcluidas :
                            if self.achouSupervisaoDePosDoutorado:
                                self.listaOCSupervisaoDePosDoutorado.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouTeseDeDoutorado:
                                self.listaOCTeseDeDoutorado.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouDissertacaoDeMestrado:
                                self.listaOCDissertacaoDeMestrado.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouMonografiaDeEspecializacao:
                                self.listaOCMonografiaDeEspecializacao.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouTCC:
                                self.listaOCTCC.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouIniciacaoCientifica:
                                self.listaOCIniciacaoCientifica.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''
                            if self.achouOutroTipoDeOrientacao:
                                self.listaOCOutroTipoDeOrientacao.append( OrientacaoConcluida(self.idMembro, self.partesDoItem, self.idOrientando) )
                                self.idOrientando = ''


        if tag=='span':
            if self.spanInformacaoArtigo:
                self.spanInformacaoArtigo = 0


    # ------------------------------------------------------------------------ #
    def handle_data(self, dado):
        if not self.spanInformacaoArtigo:
            self.item = self.item + htmlentitydecode(dado)

        dado = stripBlanks(dado)

        if self.salvarAtualizacaoCV:
            data = re.findall('Última atualização do currículo em (\d{2}/\d{2}/\d{4})', dado)
            if len(data)>0: # se a data de atualizacao do CV for identificada
                self.atualizacaoCV = stripBlanks(data[0])
                self.salvarAtualizacaoCV = 0

        if self.procurarCabecalho:
            if 'Identificação'==dado:
                self.achouIdentificacao = 1
            if 'Endereço'==dado:
                self.achouEndereco = 1
            if 'Formação acadêmica/titulação'==dado:
                self.achouFormacaoAcademica = 1
            if 'Atuação Profissional'==dado:
                self.achouAtuacaoProfissional = 1
            if 'Projetos de pesquisa'==dado:
                self.achouProjetoDePesquisa = 1
            if 'Membro de corpo editorial'==dado:
                self.achouMembroDeCorpoEditorial = 1
            if 'Revisor de periódico'==dado:
                self.achouRevisorDePeriodico = 1
            if 'Áreas de atuação'==dado:
                self.achouAreaDeAtuacao = 1
            if 'Idiomas'==dado:
                self.achouIdioma = 1
            if 'Prêmios e títulos'==dado:
                self.achouPremioOuTitulo = 1
            if 'Produções'==dado:  # !---
                self.achouProducoes = 1
                #self.achouProducaoEmCTA = 1
            #if u'Produção técnica'==dado:
            #	self.achouProducaoTecnica = 1
            #if u'Produção artística/cultural'==dado:
            #	self.achouProducaoArtisticaCultural = 1
            if 'Bancas'==dado:
                self.achouBancas = 1
            if 'Eventos'==dado:
                self.achouEventos = 1
            if 'Orientações'==dado:
                self.achouOrientacoes = 1
            if 'Patentes e registros'== dado:
                self.achouPatenteRegistro = 1
                #print "0==>>>>ACHOU PATENTE e REGISTRO"
            if 'Outras informações relevantes'==dado:
                self.achouOutrasInformacoesRelevantes = 1
            self.umaUnidade = 0
        if self.achouIdentificacao:
            if 'Nome em citações bibliográficas'==dado:
                self.achouNomeEmCitacoes = 1
            if 'Sexo'==dado:
                self.achouSexo = 1

        if self.achouEndereco:
            if 'Endereço Profissional'==dado:
                self.achouEnderecoProfissional = 1

        if self.achouPatenteRegistro:
            if 'Patente'==dado:
                self.salvarItem = 1
                self.achouPatente = 1
                self.achouProgramaComputador = 0
                self.achouDesenhoIndustrial = 0
                #print "1==>>>>ACHOU PATENTE e REGISTRO"
            if 'Programa de computador'==dado:
                self.salvarItem = 1
                self.achouPatente = 0
                self.achouProgramaComputador = 1
                self.achouDesenhoIndustrial = 0
                #print "2==>>>>ACHOU PATENTE e REGISTRO"
            if 'Desenho industrial'==dado:
                self.salvarItem = 1
                self.achouPatente = 0
                self.achouProgramaComputador = 0
                self.achouDesenhoIndustrial = 1

        if self.achouProducoes:
            if 'Produção bibliográfica'==dado:
                self.achouProducaoEmCTA = 1
                self.achouProducaoTecnica = 0
                self.achouProducaoArtisticaCultural= 0
            if 'Produção técnica'==dado:
                self.achouProducaoEmCTA = 0
                self.achouProducaoTecnica = 1
                self.achouProducaoArtisticaCultural= 0
            if 'Produção artística/cultural'==dado:
                self.achouProducaoEmCTA = 0
                self.achouProducaoTecnica = 0
                self.achouProducaoArtisticaCultural= 1

            if 'Demais trabalhos'==dado:
                self.salvarItem = 0
                self.achouProducaoEmCTA = 0
                self.achouProducaoTecnica = 0
                self.achouProducaoArtisticaCultural= 0


            if self.achouProducaoEmCTA:
                if 'Artigos completos publicados em periódicos'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 1
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Livros publicados/organizados ou edições'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 1
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Capítulos de livros publicados'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 1
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Textos em jornais de notícias/revistas'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 1
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Trabalhos completos publicados em anais de congressos'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 1
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Resumos expandidos publicados em anais de congressos'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 1
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Resumos publicados em anais de congressos' in dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 1
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Artigos aceitos para publicação'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 1
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Apresentações de Trabalho'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 1
                    self.achouOutroTipoDeProducaoBibliografica = 0
                if 'Outras produções bibliográficas'==dado:
                #if u'Demais tipos de produção bibliográfica'==dado:
                    self.salvarItem = 1
                    self.achouArtigoEmPeriodico = 0
                    self.achouLivroPublicado = 0
                    self.achouCapituloDeLivroPublicado = 0
                    self.achouTextoEmJornalDeNoticia = 0
                    self.achouTrabalhoCompletoEmCongresso = 0
                    self.achouResumoExpandidoEmCongresso = 0
                    self.achouResumoEmCongresso = 0
                    self.achouArtigoAceito = 0
                    self.achouApresentacaoDeTrabalho = 0
                    self.achouOutroTipoDeProducaoBibliografica = 1


            if self.achouProducaoTecnica:
                #if u'Softwares com registro de patente'==dado:
                if 'Programas de computador com registro'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 1
                    self.achouSoftwareSemPatente = 0
                    self.achouProdutoTecnologico = 0
                    self.achouProcessoOuTecnica = 0
                    self.achouTrabalhoTecnico = 0
                    self.achouOutroTipoDeProducaoTecnica = 0
                if 'Programas de computador sem registro'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 0
                    self.achouSoftwareSemPatente = 1
                    self.achouProdutoTecnologico = 0
                    self.achouProcessoOuTecnica = 0
                    self.achouTrabalhoTecnico = 0
                    self.achouOutroTipoDeProducaoTecnica = 0
                if 'Produtos tecnológicos'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 0
                    self.achouSoftwareSemPatente = 0
                    self.achouProdutoTecnologico = 1
                    self.achouProcessoOuTecnica = 0
                    self.achouTrabalhoTecnico = 0
                    self.achouOutroTipoDeProducaoTecnica = 0
                if 'Processos ou técnicas'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 0
                    self.achouSoftwareSemPatente = 0
                    self.achouProdutoTecnologico = 0
                    self.achouProcessoOuTecnica = 1
                    self.achouTrabalhoTecnico = 0
                    self.achouOutroTipoDeProducaoTecnica = 0
                if 'Trabalhos técnicos'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 0
                    self.achouSoftwareSemPatente = 0
                    self.achouProdutoTecnologico = 0
                    self.achouProcessoOuTecnica = 0
                    self.achouTrabalhoTecnico = 1
                    self.achouOutroTipoDeProducaoTecnica = 0
                if 'Demais tipos de produção técnica'==dado:
                    self.salvarItem = 1
                    self.achouSoftwareComPatente = 0
                    self.achouSoftwareSemPatente = 0
                    self.achouProdutoTecnologico = 0
                    self.achouProcessoOuTecnica = 0
                    self.achouTrabalhoTecnico = 0
                    self.achouOutroTipoDeProducaoTecnica = 1
                #if u'Demais trabalhos'==dado:
                #	self.salvarItem = 0
                #	self.achouSoftwareComPatente = 0
                #	self.achouSoftwareSemPatente = 0
                #	self.achouProdutoTecnologico = 0
                #	self.achouProcessoOuTecnica = 0
                #	self.achouTrabalhoTecnico = 0
                #	self.achouOutroTipoDeProducaoTecnica = 0
    
            if self.achouProducaoArtisticaCultural:
                #if u'Produção artística/cultural'==dado:
                if 'Outras produções artísticas/culturais'==dado or 'Artes Cênicas'==dado or 'Música'==dado:
                    # separar as listas de producoes artisticas por tipos
                    self.salvarItem = 1
                    self.achouOutraProducaoArtisticaCultural = 1

        if self.achouBancas:
            if 'Participação em bancas de trabalhos de conclusão'==dado:
                self.salvarItem = 0

        if self.achouEventos:
            if 'Participação em eventos, congressos, exposições e feiras'==dado:
                self.salvarItem = 1
                self.achouParticipacaoEmEvento  = 1
                self.achouOrganizacaoDeEvento = 0
            if 'Organização de eventos, congressos, exposições e feiras'==dado:
                self.salvarItem = 1
                self.achouParticipacaoEmEvento  = 0
                self.achouOrganizacaoDeEvento = 1

        if self.achouOrientacoes:
            if 'Orientações e supervisões em andamento'==dado:
                self.achouOrientacoesEmAndamento  = 1
                self.achouOrientacoesConcluidas = 0
            if 'Orientações e supervisões concluídas'==dado:
                self.achouOrientacoesEmAndamento  = 0
                self.achouOrientacoesConcluidas = 1

            # Tipos de orientações (em andamento ou concluídas)
            if 'Supervisão de pós-doutorado'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 1
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 0
            if 'Tese de doutorado'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 1
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 0
            if 'Dissertação de mestrado'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 1
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 0
            if 'Monografia de conclusão de curso de aperfeiçoamento/especialização'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 1
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 0
            if 'Trabalho de conclusão de curso de graduação'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 1
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 0
            if 'Iniciação científica' in dado or 'Iniciação Científica'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 1
                self.achouOutroTipoDeOrientacao = 0
            if 'Orientações de outra natureza'==dado:
                self.salvarItem = 1
                self.achouSupervisaoDePosDoutorado = 0
                self.achouTeseDeDoutorado = 0
                self.achouDissertacaoDeMestrado = 0
                self.achouMonografiaDeEspecializacao = 0
                self.achouTCC = 0
                self.achouIniciacaoCientifica = 0
                self.achouOutroTipoDeOrientacao = 1


        if self.achouOutrasInformacoesRelevantes:
            self.salvarItem = 0

        if self.recuperarIdentificador16 and self.identificador16 == '':
          id = re.findall('http://lattes.cnpq.br/(\d{16})', dado)
          if len(id) > 0:
            self.identificador16 = id[0]

        if self.achouProjetoDePesquisa:
            if dado.startswith('Projeto certificado pelo(a) coordenador(a)') or dado.startswith('Projeto certificado pela empresa'):
            #if u'Projeto certificado pelo(a) coordenador(a)' in dado or u'Projeto certificado pela empresa' in dado:
                self.item = ''
                self.salvarParte3 = 0



# ---------------------------------------------------------------------------- #
def stripBlanks(s):
    return re.sub('\s+', ' ', s).strip()

def htmlentitydecode(s):                                                                               
    return re.sub('&(%s);' % '|'.join(name2codepoint),
        lambda m: chr(name2codepoint[m.group(1)]), s)

