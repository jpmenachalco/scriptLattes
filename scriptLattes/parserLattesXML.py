#!/usr/bin/python
# encoding: utf-8
# filename: parserLattesXML.py
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


# ---------------------------------------------------------------------------- #
# Classe para leitura de CVs Lattes em formato XML. Sim, nosso scriptLattes
# também pode ler CVs em formato XML e HTML. 
# Por enquanto esta característica fica sem documentação.
# ---------------------------------------------------------------------------- #

from html.entities import name2codepoint
from html.parser import HTMLParser

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
from .orientacoes.orientacaoConcluida import *


class ParserLattesXML(HTMLParser):
	item = None
	nomeCompleto = ''
	bolsaProdutividade = ''
	enderecoProfissional = ''
	sexo = ''
	nomeEmCitacoesBibliograficas = ''
	atualizacaoCV = ''
	foto = ''
	textoResumo = ''
	idLattes = ''
	url = ''

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

	# variáveis auxiliares
	achouArtigoEmPeriodico = None #
	achouCapituloDeLivroPublicado = None #
	achouLivroPublicado = None #
	achouTextoEmJornalDeNoticia = None #
	achouTrabalhoCompletoEmCongresso = None #
	achouResumoExpandidoEmCongresso = None #
	achouResumoEmCongresso = None #
	achouArtigoAceito = None #
	achouApresentacaoDeTrabalho = None # 
	achouOutroTipoDeProducaoBibliografica = None #

	achouSoftwareComPatente = None
	achouSoftwareSemPatente = None
	achouProdutoTecnologico = None
	achouProcessoOuTecnica = None
	achouTrabalhoTecnico = None
	achouOutroTipoDeProducaoTecnica = None

	achouProducaoArtistica = None
	achouTrabalhoEmEvento = None

	achouOCDissertacaoDeMestrado = None
	achouOCSupervisaoDePosDoutorado = None
	achouOCTeseDeDoutorado = None


	# ------------------------------------------------------------------------ #
	def __init__(self, idMembro, cvLattesXML):
		HTMLParser.__init__(self)

		# inicializacao obrigatoria
		self.idMembro = idMembro

		self.item = ''
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

		# inicializacao 
		self.idLattes = ''
		self.url      = ''
		self.foto     = ''

		# feed it!
		# print cvLattesXML #.encode("utf8")
		self.feed(cvLattesXML)

	# ------------------------------------------------------------------------ #
	def handle_starttag(self, tag, attributes):

		if tag=='curriculo-vitae':
			for name, value in attributes:
				if name=='data-atualizacao':
					self.atualizacaoCV = value
				if name=='numero-identificador':
					self.idLattes = value
					self.url = 'http://lattes.cnpq.br/'+value
					self.url = self.url.encode('utf-8')

		if tag=='dados-gerais':
			for name, value in attributes:
				if name=='nome-completo':
					self.nomeCompleto = value
				if name=='nome-em-citacoes-bibliograficas':
					self.nomeEmCitacoesBibliograficas = value
				if name=='sexo':
					self.sexo = value.capitalize()
					self.foto = 'usuaria.png' if self.sexo[0]=='F' else 'usuario.png' 
		
		if tag=='resumo-cv':
			for name, value in attributes:
				if name=='texto-resumo-cv-rh':
					self.textoResumo = value

		# por implementar

		#if tag=='FORMACAO-ACADEMICA-TITULACAO':
		#	for name, value in attributes:
		#		if name=='':
		#			= value

		#if tag=='AREAS-DE-ATUACAO':
		#	for name, value in attributes:
		#		if name=='':
		#			= value

		#if tag=='IDIOMAS
		#	for name, value in attributes:
		#		if name=='':
		#			= value

		if tag=='artigo-publicado':
			self.achouArtigoEmPeriodico = 1
			self.autoresLista = list(['']*150)
			self.autores  = ''
			self.titulo   = ''
			self.ano      = ''
			self.revista  = ''
			self.volume   = ''
			self.numero   = ''
			self.paginas  = ''
			self.doi      = ''

		if tag=='livro-publicado-ou-organizado':
			self.achouLivroPublicado = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.edicao   = '' 
			self.ano      = '' 
			self.volume   = '' 
			self.paginas  = ''

		if tag=='capitulo-de-livro-publicado':
			self.achouCapituloDeLivroPublicado = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.livro    = '' 
			self.edicao   = '' 
			self.editora  = '' 
			self.ano      = '' 
			self.volume   = '' 
			self.paginas  = ''

		if tag=='texto-em-jornal-ou-revista':
			self.achouTextoEmJornalDeNoticia = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.nomeJornal= '' 
			self.data     = '' 
			self.volume   = '' 
			self.paginas  = ''
			self.ano      = '' 

		if tag=='trabalho-em-eventos':
			self.achouTrabalhoEmEvento = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.nomeDoEvento= '' 
			self.ano      = '' 
			self.volume   = '' 
			self.numero   = '' 
			self.paginas  = ''
			self.doi      = ''

		if tag=='artigo-aceito-para-publicacao':
			self.achouArtigoAceito = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.revista  = '' 
			self.ano      = '' 
			self.volume   = '' 
			self.numero   = '' 
			self.paginas  = ''
			self.doi      = ''

		if tag=='apresentacao-de-trabalho':
			self.achouApresentacaoDeTrabalho = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.ano      = '' 
			self.natureza = '' 

		if tag=='outra-producao-bibliografica':
			self.achouOutroTipoDeProducaoBibliografica = 1
			self.autoresLista = list(['']*150)
			self.autores  = '' 
			self.titulo   = '' 
			self.ano      = '' 
			self.natureza = '' 


		# ----------------------------------------------------------------------
		# ----------------------------------------------------------------------
		if tag=='orientacoes-concluidas-para-pos-doutorado':
			self.achouOCSupervisaoDePosDoutorado = 1
			self.nome = ''
			self.tituloDoTrabalho = ''
			self.ano = ''
			self.instituicao = ''
			self.agenciaDeFomento = ''
			self.tipoDeOrientacao = ''

		if tag=='orientacoes-concluidas-para-doutorado':
			self.achouOCTeseDeDoutorado = 1
			self.nome = ''
			self.tituloDoTrabalho = ''
			self.ano = ''
			self.instituicao = ''
			self.agenciaDeFomento = ''
			self.tipoDeOrientacao = ''

		if tag=='orientacoes-concluidas-para-mestrado':
			self.achouOCDissertacaoDeMestrado = 1
			self.nome = ''
			self.tituloDoTrabalho = ''
			self.ano = ''
			self.instituicao = ''
			self.agenciaDeFomento = ''
			self.tipoDeOrientacao = ''


		# ----------------------------------------------------------------------
		if tag=='endereco-profissional':
			for name, value in attributes:
				if name=='nome-instituicao-empresa':
					nomeIntituicao = value
				if name=='nome-unidade':
					nomeUnidade = value
				if name=='nome-orgao':
					orgao = value
				if name=='logradouro-complemento':
					logradouro = value
				if name=='cidade':
					cidade = value
				if name=='pais':
					pais = value
				if name=='uf':
					uf = value
				if name=='cep':
					cep = value
			self.enderecoProfissional = nomeIntituicao+". "+nomeUnidade+". "+orgao+". "+logradouro+" CEP "+cep+" - "+cidade+", "+uf+" - "+pais


		# ----------------------------------------------------------------------
		if self.achouArtigoEmPeriodico:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-artigo':
				for name, value in attributes:
					if name=='titulo-do-artigo':
						self.titulo = value
					if name=='ano-do-artigo':
						self.ano = value
					if name=='doi':
						self.doi = value

			if tag=='detalhamento-do-artigo':
				for name, value in attributes:
					if name=='titulo-do-periodico-ou-revista':
						self.revista = value
					if name=='volume':
						self.volume = value
					if name=='fasciculo':
						self.numero = value
					if name=='pagina-inicial':
						pagina1 = value
					if name=='pagina-final':
						pagina2 = value
				self.paginas = pagina1+'-'+pagina2


		# ----------------------------------------------------------------------
		if self.achouLivroPublicado:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-livro':
				for name, value in attributes:
					if name=='titulo-do-livro':
						self.titulo = value
					if name=='ano':
						self.ano = value

			if tag=='detalhamento-do-livro':
				for name, value in attributes:
					if name=='numero-da-edicao-revisao':
						self.edicao = value
					if name=='numero-da-serie':
						self.volume = value
					if name=='numero-de-paginas':
						self.paginas = value

		# ----------------------------------------------------------------------
		if self.achouCapituloDeLivroPublicado:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-capitulo':
				for name, value in attributes:
					if name=='titulo-do-capitulo-do-livro':
						self.titulo = value
					if name=='ano':
						self.ano = value

			if tag=='detalhamento-do-capitulo':
				for name, value in attributes:
					if name=='titulo-do-livro':
						self.livro = value
					if name=='numero-da-edicao-revisao':
						self.edicao = value
					if name=='nome-da-editora':
						self.editora = value
					if name=='numero-da-serie':
						self.volume = value
					if name=='pagina-inicial':
						pagina1 = value
					if name=='pagina-final':
						pagina2 = value
				self.paginas = pagina1+'-'+pagina2

		# ----------------------------------------------------------------------
		if self.achouTextoEmJornalDeNoticia:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-texto':
				for name, value in attributes:
					if name=='titulo-do-texto':
						self.titulo = value
					if name=='ano-do-texto':
						self.ano = value

			if tag=='detalhamento-do-texto':
				for name, value in attributes:
					if name=='titulo-do-jornal-ou-revista':
						self.nomeJornal = value
					if name=='data-de-publicacao':
						self.data = value
					if name=='volume':
						self.volume = value
					if name=='pagina-inicial':
						pagina1 = value
					if name=='pagina-final':
						pagina2 = value
				self.paginas = pagina1+'-'+pagina2

		# ----------------------------------------------------------------------
		if self.achouTrabalhoEmEvento:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-trabalho':
				for name, value in attributes:
					if name=='natureza' and value.lower()=='completo':
						self.achouTrabalhoCompletoEmCongresso = 1
					if name=='natureza' and value.lower()=='resumo':
						self.achouResumoEmCongresso = 1
					if name=='natureza' and value.lower()=='resumo_expandido':
						self.achouResumoExpandidoEmCongresso = 1


					if name=='titulo-do-trabalho':
						self.titulo = value
					if name=='ano-do-trabalho':
						self.ano = value
					if name=='doi':
						self.doi = value
			if tag=='detalhamento-do-trabalho':
				for name, value in attributes:
					if name=='nome-do-evento':
						self.nomeDoEvento = value
					if name=='volume':
						self.volume = value
					if name=='fasciculo':
						self.numero = value
					if name=='pagina-inicial':
						pagina1 = value
					if name=='pagina-final':
						pagina2 = value
				self.paginas = pagina1+'-'+pagina2

		# ----------------------------------------------------------------------
		if self.achouArtigoAceito:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-do-artigo':
				for name, value in attributes:
					if name=='titulo-do-artigo':
						self.titulo = value
					if name=='ano-do-artigo':
						self.ano = value
					if name=='doi':
						self.doi = value

			if tag=='detalhamento-do-artigo':
				for name, value in attributes:
					if name=='titulo-do-periodico-ou-revista':
						self.revista = value
					if name=='volume':
						self.volume = value
					if name=='fasciculo':
						self.numero = value
					if name=='pagina-inicial':
						pagina1 = value
					if name=='pagina-final':
						pagina2 = value
				self.paginas = pagina1+'-'+pagina2

		# ----------------------------------------------------------------------
		if self.achouApresentacaoDeTrabalho:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-da-apresentacao-de-trabalho':
				for name, value in attributes:
					if name=='titulo':
						self.titulo = value
					if name=='ano':
						self.ano = value
					if name=='natureza':
						self.natureza = value.capitalize()

			if tag=='detalhamento-da-apresentacao-de-trabalho':
				for name, value in attributes:
					if name=='nome-do-evento':
						self.nomeEvento = value

		# ----------------------------------------------------------------------
		if self.achouOutroTipoDeProducaoBibliografica:
			if tag=='autores':
				for name, value in attributes:
					if name=='nome-para-citacao':
						autorNome = value.split(';')[0]
					if name=='ordem-de-autoria':
						autorOrdem = value
				self.autoresLista[int(autorOrdem)] = autorNome

			if tag=='dados-basicos-de-outra-producao':
				for name, value in attributes:
					if name=='titulo':
						self.titulo = value
					if name=='ano':
						self.ano = value
					if name=='natureza':
						self.natureza = value.capitalize()

			if tag=='detalhamento-de-outra-producao':
				for name, value in attributes:
					if name=='editora':
						self.editora = value


		# ----------------------------------------------------------------------
		# ----------------------------------------------------------------------
		# ----------------------------------------------------------------------
		if self.achouOCSupervisaoDePosDoutorado:
			if tag=='dados-basicos-de-orientacoes-concluidas-para-pos-doutorado':
				for name, value in attributes:
					if name=='titulo':
						self.tituloDoTrabalho = value
					if name=='ano':
						self.ano = value
					if name=='natureza':
						self.tipoDeOrientacao = value.capitalize()
			if tag=='detalhamento-de-orientacoes-concluidas-para-pos-doutorado':
				for name, value in attributes:
					if name=='nome-do-orientado':
						self.nome = value
					if name=='nome-da-instituicao':
						self.instituicao = value
					if name=='nome-da-agencia':
						self.agenciaDeFomento = value

		# ----------------------------------------------------------------------
		if self.achouOCTeseDeDoutorado:
			if tag=='dados-basicos-de-orientacoes-concluidas-para-doutorado':
				for name, value in attributes:
					if name=='titulo':
						self.tituloDoTrabalho = value
					if name=='ano':
						self.ano = value
					if name=='natureza':
						self.tipoDeOrientacao = value.capitalize()
			if tag=='detalhamento-de-orientacoes-concluidas-para-doutorado':
				for name, value in attributes:
					if name=='nome-do-orientado':
						self.nome = value
					if name=='nome-da-instituicao':
						self.instituicao = value
					if name=='nome-da-agencia':
						self.agenciaDeFomento = value

		# ----------------------------------------------------------------------
		if self.achouOCDissertacaoDeMestrado:
			if tag=='dados-basicos-de-orientacoes-concluidas-para-mestrado':
				for name, value in attributes:
					if name=='titulo':
						self.tituloDoTrabalho = value
					if name=='ano':
						self.ano = value
					if name=='natureza':
						self.tipoDeOrientacao = value.capitalize()
			if tag=='detalhamento-de-orientacoes-concluidas-para-mestrado':
				for name, value in attributes:
					if name=='nome-do-orientado':
						self.nome = value
					if name=='nome-da-instituicao':
						self.instituicao = value
					if name=='nome-da-agencia':
						self.agenciaDeFomento = value



	def handle_endtag(self, tag):
		# ----------------------------------------------------------------------
		if tag=='artigo-publicado':
			self.achouArtigoEmPeriodico = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = ArtigoEmPeriodico(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = stripBlanks(self.titulo)
			pub.revista = self.revista
			pub.volume  = self.volume
			pub.paginas = self.paginas
			pub.numero  = self.numero
			pub.ano     = self.ano
			pub.chave   = self.autores
			pub.doi     = 'http://dx.doi.org/'+self.doi if not self.doi==0 else ''
			self.listaArtigoEmPeriodico.append(pub)

		# ----------------------------------------------------------------------
		if tag=='livro-publicado-ou-organizado':
			self.achouLivroPublicado = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = LivroPublicado(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = self.titulo
			pub.edicao  = self.edicao
			pub.ano     = self.ano
			pub.volume  = self.volume
			pub.paginas = self.paginas
			pub.chave   = self.autores
			self.listaLivroPublicado.append(pub)

		# ----------------------------------------------------------------------
		if tag=='capitulo-de-livro-publicado':
			self.achouCapituloDeLivroPublicado = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = CapituloDeLivroPublicado(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = stripBlanks(self.titulo)
			pub.livro   = self.livro
			pub.edicao  = self.edicao
			pub.editora = self.editora
			pub.ano     = self.ano
			pub.volume  = self.volume
			pub.paginas = self.paginas
			pub.chave   = self.autores
			self.listaCapituloDeLivroPublicado.append(pub)

		# ----------------------------------------------------------------------
		if tag=='texto-em-jornal-ou-revista':
			self.achouTextoEmJornalDeNoticia = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = TextoEmJornalDeNoticia(self.idMembro)
			pub.autores  = self.autores
			pub.titulo   = self.titulo
			pub.nomeJornal=self.nomeJornal 
			pub.data     = self.data
			pub.volume   = self.volume
			pub.paginas  = self.paginas
			pub.ano      = self.ano
			pub.chave   = self.autores
			self.listaTextoEmJornalDeNoticia.append(pub)

		# ----------------------------------------------------------------------
		if tag=='trabalho-em-eventos':
			self.achouTrabalhoEmEvento = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")


			if self.achouResumoEmCongresso:
				self.achouResumoEmCongresso = 0
				pub = ResumoEmCongresso(self.idMembro)
				pub.autores  = self.autores
				pub.titulo   = self.titulo
				pub.nomeDoEvento=self.nomeDoEvento
				pub.ano      = self.ano
				pub.volume   = self.volume
				pub.numero   = self.numero
				pub.paginas  = self.paginas
				pub.chave   = self.autores
				pub.doi     = 'http://dx.doi.org/'+self.doi if not self.doi==0 else ''
				self.listaResumoEmCongresso.append(pub)
				return

			if self.achouResumoExpandidoEmCongresso:
				self.achouResumoExpandidoEmCongresso = 0
				pub = ResumoExpandidoEmCongresso(self.idMembro)
				pub.autores  = self.autores
				pub.titulo   = self.titulo
				pub.nomeDoEvento=self.nomeDoEvento
				pub.ano      = self.ano
				pub.volume   = self.volume
				pub.paginas  = self.paginas
				pub.chave   = self.autores
				pub.doi     = 'http://dx.doi.org/'+self.doi if not self.doi==0 else ''
				self.listaResumoExpandidoEmCongresso.append(pub)
				return

			if self.achouTrabalhoCompletoEmCongresso:
				self.achouTrabalhoCompletoEmCongresso = 0
				pub = TrabalhoCompletoEmCongresso(self.idMembro)
				pub.autores  = self.autores
				pub.titulo   = self.titulo
				pub.nomeDoEvento=self.nomeDoEvento
				pub.ano      = self.ano
				pub.volume   = self.volume
				pub.paginas  = self.paginas
				pub.chave   = self.autores
				self.listaTrabalhoCompletoEmCongresso.append(pub)
				return

		# ----------------------------------------------------------------------
		if tag=='artigo-aceito-para-publicacao':
			self.achouArtigoAceito = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = ArtigoAceito(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = stripBlanks(self.titulo)
			pub.revista = self.revista
			pub.volume  = self.volume
			pub.paginas = self.paginas
			pub.numero  = self.numero
			pub.ano     = self.ano
			pub.chave   = self.autores
			pub.doi     = 'http://dx.doi.org/'+self.doi if not self.doi==0 else ''
			self.listaArtigoAceito.append(pub)

		# ----------------------------------------------------------------------
		if tag=='apresentacao-de-trabalho':
			self.achouApresentacaoDeTrabalho = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = ApresentacaoDeTrabalho(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = stripBlanks(self.titulo)
			pub.ano     = self.ano
			pub.natureza= self.nomeEvento+'. ('+self.natureza+')'
			pub.chave   = self.autores
			self.listaApresentacaoDeTrabalho.append(pub)
		
		# ----------------------------------------------------------------------
		if tag=='outra-producao-bibliografica':
			self.achouOutroTipoDeProducaoBibliografica = 0

			for aut in self.autoresLista:
				if not aut=='':
					self.autores+= aut +"; "
			self.autores = self.autores.strip("; ")

			pub = OutroTipoDeProducaoBibliografica(self.idMembro)
			pub.autores = self.autores
			pub.titulo  = stripBlanks(self.titulo)
			pub.ano     = self.ano
			pub.natureza= self.editora+'. ('+self.natureza+')'
			pub.chave   = self.autores
			self.listaOutroTipoDeProducaoBibliografica.append(pub)

		# ----------------------------------------------------------------------
		if tag=='orientacoes-concluidas-para-pos-doutorado':
			self.achouOCSupervisaoDePosDoutorado = 0

			ori = OrientacaoConcluida(self.idMembro)
			ori.nome = self.nome
			ori.tituloDoTrabalho = self.tituloDoTrabalho
			ori.ano = self.ano
			ori.instituicao = self.instituicao
			ori.agenciaDeFomento = self.agenciaDeFomento
			ori.tipoDeOrientacao = self.tipoDeOrientacao
			ori.chave = self.nome
			self.listaOCSupervisaoDePosDoutorado.append(ori)

		if tag=='orientacoes-concluidas-para-doutorado':
			self.achouOCTeseDeDoutorado = 0

			ori = OrientacaoConcluida(self.idMembro)
			ori.nome = self.nome
			ori.tituloDoTrabalho = self.tituloDoTrabalho
			ori.ano = self.ano
			ori.instituicao = self.instituicao
			ori.agenciaDeFomento = self.agenciaDeFomento
			ori.tipoDeOrientacao = self.tipoDeOrientacao
			ori.chave = self.nome
			self.listaOCTeseDeDoutorado.append(ori)

		if tag=='orientacoes-concluidas-para-mestrado':
			self.achouOCDissertacaoDeMestrado = 0

			ori = OrientacaoConcluida(self.idMembro)
			ori.nome = self.nome
			ori.tituloDoTrabalho = self.tituloDoTrabalho
			ori.ano = self.ano
			ori.instituicao = self.instituicao
			ori.agenciaDeFomento = self.agenciaDeFomento
			ori.tipoDeOrientacao = self.tipoDeOrientacao
			ori.chave = self.nome
			self.listaOCDissertacaoDeMestrado.append(ori)



	# ------------------------------------------------------------------------ #
	# def handle_data(self, dado):

# ---------------------------------------------------------------------------- #
def stripBlanks(s):
	return re.sub('\s+', ' ', s).strip()

def htmlentitydecode(s):                                                                               
	return re.sub('&(%s);' % '|'.join(name2codepoint),                                                 
		lambda m: chr(name2codepoint[m.group(1)]), s)   

