#!/usr/bin/python
# encoding: utf-8


import fileinput
import tqdm
from scriptLattes.util import *
from . import util
from scriptLattes.membro import Membro
from scriptLattes.compiladorDeListas import CompiladorDeListas
from scriptLattes.geradorDePaginasWeb import GeradorDePaginasWeb
from scriptLattes.grafoDeColaboracoes import *


class Grupo:
    compilador = None
    listaDeParametros = []
    listaDeMembros = []
    listaDeRotulos = []
    listaDeRotulosCores = []
    listaDePublicacoesEinternacionalizacao = []

    arquivoConfiguracao = None
    itemsDesdeOAno = None
    itemsAteOAno = None
    diretorioCache = None
    diretorioDoi = None

    matrizArtigoEmPeriodico = None
    matrizLivroPublicado = None
    matrizCapituloDeLivroPublicado = None
    matrizTextoEmJornalDeNoticia = None
    matrizTrabalhoCompletoEmCongresso = None
    matrizResumoExpandidoEmCongresso = None
    matrizResumoEmCongresso = None
    matrizArtigoAceito = None
    matrizApresentacaoDeTrabalho = None
    matrizOutroTipoDeProducaoBibliografica = None
    matrizSoftwareComPatente = None
    matrizSoftwareSemPatente = None
    matrizProdutoTecnologico = None
    matrizProcessoOuTecnica = None
    matrizTrabalhoTecnico = None
    matrizOutroTipoDeProducaoTecnica = None
    matrizProducaoArtistica = None

    matrizPatente = None
    matrizProgramaComputador = None
    matrizDesenhoIndustrial = None

    matrizDeAdjacencia = None
    matrizDeFrequencia = None
    matrizDeFrequenciaNormalizada = None
    vetorDeCoAutoria = None
    grafoDeColaboracoes = None
    geradorDeXml = None

    vectorRank = None
    nomes = None
    rotulos = None

    colaboradores_endogenos = None
    listaDeColaboracoes = None

    
    listaDeTermos = list()
    dicionarioDeTermos = dict()


    def __init__(self, arquivo):
        self.arquivoConfiguracao = arquivo
        self.carregarParametrosPadrao()


        # atualizamos a lista de parametros
        for linha in fileinput.input(self.arquivoConfiguracao):
            linha = linha.replace("\r", "")
            linha = linha.replace("\n", "")

            linhaPart = linha.partition("#")  # eliminamos os comentários
            linhaDiv = linhaPart[0].split("=", 1)

            if len(linhaDiv) == 2:
                self.atualizarParametro(linhaDiv[0], linhaDiv[1])

        # carregamos o periodo global
        ano1 = self.obterParametro('global-itens_desde_o_ano')
        ano2 = self.obterParametro('global-itens_ate_o_ano')
        if ano1.lower() == 'hoje':
            ano1 = str(datetime.datetime.now().year)
        if ano2.lower() == 'hoje':
            ano2 = str(datetime.datetime.now().year)
        if ano1 == '':
            ano1 = '0'
        if ano2 == '':
            ano2 = '10000'
        self.itemsDesdeOAno = int(ano1)
        self.itemsAteOAno = int(ano2)

        self.diretorioCache = self.obterParametro('global-diretorio_de_armazenamento_de_cvs')
        if not self.diretorioCache == '':
            util.criarDiretorio(self.diretorioCache)


        if self.obterParametro('global-identificar_producoes_por_termos'):
            # carregamos a lista de termos
            entrada = buscarArquivo(self.obterParametro('global-arquivo_de_termos_de_busca'))
            for linha in fileinput.input(entrada):
                linha = linha.replace("\r", "")
                linha = linha.replace("\n", "")

                linhaPart = linha.partition("#")  # eliminamos os comentários
                t = linhaPart[0].strip()

                if len(t) > 0:
                    self.listaDeTermos.append(t)
                    nt = eliminar_acentuacao(t)
                    partes = nt.split(" AND ")
                    partes = [x.strip(' ').lower() for x in partes]  # tiramos os espacos
                    self.dicionarioDeTermos[t] = partes 


        # carregamos a lista de membros
        entrada = buscarArquivo(self.obterParametro('global-arquivo_de_entrada'))

        idSequencial = 0
        for linha in fileinput.input(entrada):
            linha = linha.replace("\r", "")
            linha = linha.replace("\n", "")

            linhaPart = linha.partition("#")  # eliminamos os comentários
            linhaDiv = linhaPart[0].split(",")
            if ';' in linhaPart[0] and len(linhaDiv) < 2:
                linhaDiv = linhaPart[0].split(";")
            if '\t' in linhaPart[0] and len(linhaDiv) < 2:
                linhaDiv = linhaPart[0].split("\t")

            if linhaDiv[0].strip():
                identificador = linhaDiv[0].strip() if len(linhaDiv) > 0 else ''
                nome = linhaDiv[1].strip() if len(linhaDiv) > 1 else ''
                periodo = linhaDiv[2].strip() if len(linhaDiv) > 2 else ''
                rotulo = linhaDiv[3].strip() if len(linhaDiv) > 3 and linhaDiv[3].strip() else '* Sem rótulo'

                self.listaDeMembros.append( Membro(idSequencial, identificador, nome, periodo, rotulo, self.itemsDesdeOAno, self.itemsAteOAno, self.diretorioCache, self.dicionarioDeTermos))
                self.listaDeRotulos.append(rotulo)
                idSequencial += 1

        self.listaDeRotulos = list(set(self.listaDeRotulos))  # lista unica de rotulos
        self.listaDeRotulos.sort()
        self.listaDeRotulosCores = [''] * len(self.listaDeRotulos)



    def gerarArquivosTemporarios(self):
        print ("\n[CRIANDO ARQUIVOS TEMPORARIOS: CSV, TXT, GDF]")


        # (4) lista unica de colaboradores (orientadores, ou qualquer outro tipo de parceiros...)
        rawIDsColaboradores = list([])
        rawIDsMembros       = list([])
        for membro in self.listaDeMembros:
            rawIDsMembros.append(membro.idLattes)
        for membro in self.listaDeMembros:
            for idColaborador in membro.listaIDLattesColaboradoresUnica:
                if not idColaborador in rawIDsMembros:
                    rawIDsColaboradores.append(idColaborador)
        rawIDsColaboradores = list(set(rawIDsColaboradores))
        self.salvarListaTXT(rawIDsColaboradores, "colaboradores.txt")

        # (6) arquivo GDF + JSON
        #self.gerarArquivoGDF("rede.gdf")
        #self.gerarArquivoJSON("rede.json")




    def gerarArquivoGDF(self, nomeArquivo):
        # Vêrtices
        N = len(self.listaDeMembros)
        string = "nodedef> name VARCHAR, idLattes VARCHAR, label VARCHAR, rotulo VARCHAR, lat DOUBLE, lon DOUBLE, collaborationRank DOUBLE, producaoBibliografica DOUBLE, artigoEmPeriodico DOUBLE, livro DOUBLE, capituloDeLivro DOUBLE, trabalhoEmCongresso DOUBLE, resumoExpandido DOUBLE, resumo DOUBLE"
        string+= ", posDoutorado DOUBLE"
        string+= ", dutorado DOUBLE"
        string+= ", mestrado DOUBLE"
        string+= ", ic DOUBLE"
        string+= ", color VARCHAR"
        i = 0
        for membro in self.listaDeMembros:
            #nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto)
            nomeCompleto = membro.nomeCompleto
            # print nomeCompleto
            string += "\n" + str(i) + "," + membro.idLattes + "," + nomeCompleto + "," + membro.rotulo + "," + membro.enderecoProfissionalLat + "," + membro.enderecoProfissionalLon + ","
            string += str(self.vectorRank[i]) + ","
            string += str(len(membro.listaArtigoEmPeriodico) + len(membro.listaLivroPublicado) + len(
                membro.listaCapituloDeLivroPublicado) + len(membro.listaTrabalhoCompletoEmCongresso) + len(
                membro.listaResumoExpandidoEmCongresso) + len(membro.listaResumoEmCongresso)) + ","
            string += str(len(membro.listaArtigoEmPeriodico)) + ","
            string += str(len(membro.listaLivroPublicado)) + ","
            string += str(len(membro.listaCapituloDeLivroPublicado)) + ","
            string += str(len(membro.listaTrabalhoCompletoEmCongresso)) + ","
            string += str(len(membro.listaResumoExpandidoEmCongresso)) + ","
            string += str(len(membro.listaResumoEmCongresso)) + ","

            string += str(len(membro.listaOCSupervisaoDePosDoutorado)) + ","
            string += str(len(membro.listaOCTeseDeDoutorado)) + ","
            string += str(len(membro.listaOCDissertacaoDeMestrado)) + ","
            string += str(len(membro.listaOCIniciacaoCientifica)) + ","

            string += "'" + self.HTMLColorToRGB(membro.rotuloCorBG) + "'"
            i += 1

        # Arestas
        matriz = self.matrizDeAdjacencia

        string += "\nedgedef> node1 VARCHAR, node2 VARCHAR, weight DOUBLE"
        for i in range(0, N):
            for j in range(i + 1, N):
                if (i != j) and (matriz[i, j] > 0):
                    string += '\n' + str(i) + ',' + str(j) + ',' + str(matriz[i, j])


        # gerando o arquivo GDF
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w', encoding='utf8')
        arquivo.write(string)  # .encode("utf8","ignore"))
        arquivo.close()  


    def gerarArquivoJSON(self, nomeArquivo):
        # Vêrtices
        N = len(self.listaDeMembros)
        string = '{\n"nodes":['
        i = 0
        for membro in self.listaDeMembros:
            #nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')
            nomeCompleto = membro.nomeCompleto
            string += '\n{{ "name":"{0}", "idlattes":"{1}", "rotulo":"{2}", "collaborationrank":{3} }},'.format(nomeCompleto, membro.idLattes, membro.rotulo, self.vectorRank[i] )
            i += 1
        string = string.strip(',')
        string += '\n],'
        
        # Arestas
        string += '\n"links":['
        matriz = self.matrizDeAdjacencia

        for i in range(0, N):
            for j in range(i + 1, N):
                if (i != j) and (matriz[i, j] > 0):
                    string += '\n{{ "source":{0}, "target":{1}, "value":{2} }},'.format( str(i), str(j), str(matriz[i, j]) )
        string = string.strip(',')
        string += '\n]\n}'

        # gerando o arquivo JSON
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w', encoding='utf8')
        arquivo.write(string)  # .encode("utf8","ignore"))
        arquivo.close()  


    def HTMLColorToRGB(self, colorstring):
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        #return (r, g, b)
        return str(r) + "," + str(g) + "," + str(b)


    def imprimeCSVListaIndividual(self, nomeCompleto, lista):
        s = ""
        for pub in lista:
            s += pub.csv(nomeCompleto) + "\n"
        return s


    def imprimeCSVListaGrupal(self, listaCompleta):
        s = ""
        keys = list(listaCompleta.keys())
        keys.sort(reverse=True)

        if len(keys) > 0:
            for ano in keys:
                elementos = listaCompleta[ano]
                elementos.sort(key=lambda x: x.chave.lower())
                for index in range(0, len(elementos)):
                    pub = elementos[index]
                    s += pub.csv(' ') + "\n"
        return s



    def salvarArquivoGenerico(self, conteudo, nomeArquivo):
        if type(conteudo) == bytes:
            conteudo = conteudo.decode() 
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w', encoding='utf8')
        arquivo.write(conteudo)
        arquivo.close()


    def carregarDadosCVLattes(self):
        indice = 1
        self.listaDeMembros: list[Membro]
        for membro in self.listaDeMembros:
            print(f'\n[LENDO REGISTRO LATTES: {indice}o. DA LISTA]')
            indice += 1
            membro.carregarDadosCVLattes()
            membro.filtrarItemsPorPeriodoOuTermos()
            print(membro)


    def gerarPaginasWeb(self):
        paginasWeb = GeradorDePaginasWeb(self)


    def compilarListasDeItems(self):
        self.compilador = CompiladorDeListas(self)  # compilamos todo e criamos 'listasCompletas'

        # Grafos de coautoria
        self.compilador.criarMatrizesDeColaboracao()

        [self.matrizDeAdjacencia, self.matrizDeFrequencia, self.listaDeColaboracoes] = self.compilador.uniaoDeMatrizesDeColaboracao()
        self.vetorDeCoAutoria = self.matrizDeFrequencia.sum(axis=1)  # soma das linhas = num. de items feitos em co-autoria (parceria) com outro membro do grupo
        self.matrizDeFrequenciaNormalizada = self.matrizDeFrequencia.copy()

        for i in range(0, self.numeroDeMembros()):
            if not self.vetorDeCoAutoria[i] == 0:
                self.matrizDeFrequenciaNormalizada[i, :] /= float(self.vetorDeCoAutoria[i])

        # listas de nomes, rotulos e IDs
        self.nomes = list([])
        self.rotulos = list([])
        self.ids = list([])
        for membro in self.listaDeMembros:
            self.nomes.append(membro.nomeCompleto)
            self.rotulos.append(membro.rotulo)
            self.ids.append(membro.idLattes)


    def salvarListaTXT(self, lista, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w', encoding='utf8')

        for i in range(0, len(lista)):
            elemento = lista[i]
            if not type(elemento) == type(str()):
                elemento = str(elemento)
            arquivo.write(elemento + '\n')
        arquivo.close()

    def salvarMatrizTXT(self, matriz, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w', encoding='utf8')
        N = matriz.shape[0]

        for i in range(0, N):
            for j in range(0, N):
                arquivo.write(str(matriz[i, j]) + ' ')
            arquivo.write('\n')
        arquivo.close()

    def salvarMatrizXML(self, matriz, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')

        s = '<?xml version="1.0" encoding="UTF-8"?> \
            \n<!--  An excerpt of an egocentric social network  --> \
            \n<graphml xmlns="http://graphml.graphdrawing.org/xmlns"> \
            \n<graph edgedefault="undirected"> \
            \n<!-- data schema --> \
            \n<key id="name" for="node" attr.name="name" attr.type="string"/> \
            \n<key id="nickname" for="node" attr.name="nickname" attr.type="string"/> \
            \n<key id="gender" for="node" attr.name="gender" attr.type="string"/> \
            \n<key id="image" for="node" attr.name="image" attr.type="string"/> \
            \n<key id="link" for="node" attr.name="link" attr.type="string"/> \
            \n<key id="amount" for="edge" attr.name="amount" attr.type="int"/> \
            \n<key id="pubs" for="node" attr.name="pubs" attr.type="int"/>'

        for i in range(0, self.numeroDeMembros()):
            membro = self.listaDeMembros[i]
            s += '\n<!-- nodes --> \
                \n<node id="' + str(membro.idMembro) + '"> \
                \n<data key="name">' + membro.nomeCompleto + '</data> \
                \n<data key="nickname">' + membro.nomeEmCitacoesBibliograficas + '</data> \
                \n<data key="gender">' + membro.sexo[0].upper() + '</data> \
                \n<data key="image">' + membro.foto + '</data> \
                \n<data key="link">' + membro.url + '</data> \
                \n<data key="pubs">' + str(int(self.vetorDeCoAutoria[i])) + '</data> \
                \n</node>'

        N = matriz.shape[0]
        for i in range(0, N):
            for j in range(0, N):
                if matriz[i, j] > 0:
                    s += '\n<!-- edges --> \
                        \n<edge source="' + str(i) + '" target="' + str(j) + '"> \
                        \n<data key="amount">' + str(matriz[i, j]) + '</data> \
                        \n</edge>'

        s += '\n</graph>\
            \n</graphml>'

        arquivo.write(s.encode('utf8'))
        arquivo.close()

    def salvarVetorDeProducoes(self, vetor, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        string = ''
        for i in range(0, len(vetor)):
            (prefixo, pAnos, pQuantidades) = vetor[i]
            string += "\n" + prefixo + ":"
            for j in range(0, len(pAnos)):
                string += str(pAnos[j]) + ',' + str(pQuantidades[j]) + ';'
        arquivo.write(string)
        arquivo.close()

    def salvarListaInternalizacaoTXT(self, listaDoiValido, nomeArquivo):
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        for i in range(0, len(listaDoiValido)):
            elemento = listaDoiValido[i]
            if type(elemento) == type(str()):
                elemento = elemento.encode("utf8")
            else:
                elemento = str(elemento)
            arquivo.write(elemento + '\n')
        arquivo.close()

    def gerarGraficosDeBarras(self):
        print ("\n[CRIANDO GRAFICOS DE BARRAS]")
        gBarra = GraficoDeBarras(self.obterParametro('global-diretorio_de_saida'))

        gBarra.criarGrafico(self.compilador.listaCompletaArtigoEmPeriodico, 'PB0', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaLivroPublicado, 'PB1', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaCapituloDeLivroPublicado, 'PB2', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaTextoEmJornalDeNoticia, 'PB3', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaTrabalhoCompletoEmCongresso, 'PB4', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaResumoExpandidoEmCongresso, 'PB5', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaResumoEmCongresso, 'PB6', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaArtigoAceito, 'PB7', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaApresentacaoDeTrabalho, 'PB8', 'Numero de publicacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOutroTipoDeProducaoBibliografica, 'PB9', 'Numero de publicacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaSoftwareComPatente, 'PT0', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaSoftwareSemPatente, 'PT1', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaProdutoTecnologico, 'PT2', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaProcessoOuTecnica, 'PT3', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaTrabalhoTecnico, 'PT4', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaOutroTipoDeProducaoTecnica, 'PT5', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaEntrevista, 'PT6', 'Numero de producoes tecnicas')

        gBarra.criarGrafico(self.compilador.listaCompletaPatente, 'PR0', 'Numero de patentes')
        gBarra.criarGrafico(self.compilador.listaCompletaProgramaComputador, 'PR1', 'Numero de programa de computador')
        gBarra.criarGrafico(self.compilador.listaCompletaDesenhoIndustrial, 'PR2', 'Numero de desenho industrial')

        gBarra.criarGrafico(self.compilador.listaCompletaProducaoArtistica, 'PA0', 'Numero de producoes artisticas')

        gBarra.criarGrafico(self.compilador.listaCompletaOASupervisaoDePosDoutorado, 'OA0', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOATeseDeDoutorado, 'OA1', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOADissertacaoDeMestrado, 'OA2', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAMonografiaDeEspecializacao, 'OA3', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOATCC, 'OA4', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAIniciacaoCientifica, 'OA5', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOAOutroTipoDeOrientacao, 'OA6', 'Numero de orientacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaOCSupervisaoDePosDoutorado, 'OC0', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCTeseDeDoutorado, 'OC1', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCDissertacaoDeMestrado, 'OC2', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCMonografiaDeEspecializacao, 'OC3', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCTCC, 'OC4', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCIniciacaoCientifica, 'OC5', 'Numero de orientacoes')
        gBarra.criarGrafico(self.compilador.listaCompletaOCOutroTipoDeOrientacao, 'OC6', 'Numero de orientacoes')

        gBarra.criarGrafico(self.compilador.listaCompletaPremioOuTitulo, 'Pm', 'Numero de premios')
        gBarra.criarGrafico(self.compilador.listaCompletaProjetoDePesquisa, 'Pj', 'Numero de projetos')

        gBarra.criarGrafico(self.compilador.listaCompletaPB, 'PB', 'Numero de producoes bibliograficas')
        gBarra.criarGrafico(self.compilador.listaCompletaPT, 'PT', 'Numero de producoes tecnicas')
        gBarra.criarGrafico(self.compilador.listaCompletaPA, 'PA', 'Numero de producoes artisticas')
        gBarra.criarGrafico(self.compilador.listaCompletaOA, 'OA', 'Numero de orientacoes em andamento')
        gBarra.criarGrafico(self.compilador.listaCompletaOC, 'OC', 'Numero de orientacoes concluidas')

        gBarra.criarGrafico(self.compilador.listaCompletaParticipacaoEmEvento, 'Ep', 'Numero de Eventos')
        gBarra.criarGrafico(self.compilador.listaCompletaOrganizacaoDeEvento, 'Eo', 'Numero de Eventos')

        #prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''
        #self.salvarVetorDeProducoes(gBarra.obterVetorDeProducoes(), prefix + 'vetorDeProducoes.txt')

    def gerarGrafosDeColaboracoes(self):
        if self.obterParametro('grafo-mostrar_grafo_de_colaboracoes'):
            grafoDeColaboracoes = GrafoDeColaboracoes(self)
            self.grafoDeColaboracoes = grafoDeColaboracoes.criar_grafo_com_pesos()
            self.identificar_lista_de_colaboradores_endogenos()

        #print("\n[ROTULOS]")
        #for rot in range(0, len(self.listaDeRotulos)):
        #    print(('- {} : {}'.format( self.listaDeRotulos[rot], self.listaDeRotulosCores[rot] )))


    def gerarGraficoDeProporcoes(self):
        if self.obterParametro('relatorio-incluir_grafico_de_proporcoes_bibliograficas'):
            gProporcoes = GraficoDeProporcoes(self, self.obterParametro('global-diretorio_de_saida'))


    def imprimirListasCompletas(self):
        self.compilador.imprimirListasCompletas()

    def imprimirMatrizesDeFrequencia(self):
        self.compilador.imprimirMatrizesDeFrequencia()
        print("\n[VETOR DE CO-AUTORIA]")
        print((self.vetorDeCoAutoria))
        print("\n[MATRIZ DE FREQUENCIA NORMALIZADA]")
        print((self.matrizDeFrequenciaNormalizada))

    def numeroDeMembros(self):
        return len(self.listaDeMembros)

    def ordenarListaDeMembros(self, chave):
        self.listaDeMembros.sort(key=operator.attrgetter(chave))  # ordenamos por nome

    def imprimirListaDeParametros(self):
        for par in self.listaDeParametros:  # .keys():
            print(f"[PARAMETRO] {par[0]} = {par[1]}")
        print()

    def imprimirListaDeMembros(self):
        for membro in self.listaDeMembros:
            print (membro)
        print()

    def imprimirListaDeRotulos(self):
        print()
        for (i, r) in enumerate(self.listaDeRotulos):
            print(f"[ROTULO] {i+1}\t{r}")
    
    def imprimirListaDeTermos(self):
        print()
        for (i, t) in enumerate(self.listaDeTermos):
            print(f"[TERMO] {i+1}\t{t:40s}\t{self.dicionarioDeTermos[t]}")

    def atualizarParametro(self, parametro, valor):
        parametro = parametro.strip().lower()
        valor = valor.strip()

        for i in range(0, len(self.listaDeParametros)):
            if parametro == self.listaDeParametros[i][0]:
                self.listaDeParametros[i][1] = valor
                return
        print(("[AVISO IMPORTANTE] Nome de parametro desconhecido: ") + parametro)

    def obterParametro(self, parametro):
        for i in range(0, len(self.listaDeParametros)):
            if parametro == self.listaDeParametros[i][0]:
                if self.listaDeParametros[i][1].lower() == 'sim':
                    return 1
                if self.listaDeParametros[i][1].lower() == 'nao' or self.listaDeParametros[i][1].lower() == 'não':
                    return 0

                return self.listaDeParametros[i][1]

    def atribuirCoNoRotulo(self, indice, cor):
        self.listaDeRotulosCores[indice] = cor
    
    def carregarParametrosPadrao(self):
        self.listaDeParametros.append(['global-nome_do_grupo', ''])
        self.listaDeParametros.append(['global-arquivo_de_entrada', ''])
        self.listaDeParametros.append(['global-diretorio_de_saida', ''])
        self.listaDeParametros.append(['global-email_do_admin', ''])
        self.listaDeParametros.append(['global-idioma', 'PT'])
        self.listaDeParametros.append(['global-itens_desde_o_ano', ''])
        self.listaDeParametros.append(['global-itens_ate_o_ano', ''])  # hoje
        self.listaDeParametros.append(['global-itens_por_pagina', '5000'])
        self.listaDeParametros.append(['global-diretorio_de_armazenamento_de_cvs', './cache/'])

        self.listaDeParametros.append(['global-identificar_producoes_por_termos', 'nao'])
        self.listaDeParametros.append(['global-arquivo_de_termos_de_busca', ''])

        self.listaDeParametros.append(['relatorio-incluir_artigo_em_periodico', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_livro_publicado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_capitulo_de_livro_publicado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_texto_em_jornal_de_noticia', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_trabalho_completo_em_congresso', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_resumo_expandido_em_congresso', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_resumo_em_congresso', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_artigo_aceito_para_publicacao', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_apresentacao_de_trabalho', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_outro_tipo_de_producao_bibliografica', 'sim'])

        self.listaDeParametros.append(['relatorio-incluir_software_com_registro', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_software_sem_registro', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_produto_tecnologico', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_processo_ou_tecnica', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_trabalho_tecnico', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_outro_tipo_de_producao_tecnica', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_entrevista_mesas_e_comentarios', 'sim'])

        self.listaDeParametros.append(['relatorio-incluir_patente', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_programa_computador', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_desenho_industrial', 'sim'])

        self.listaDeParametros.append(['relatorio-incluir_producao_artistica', 'sim'])

        self.listaDeParametros.append(['relatorio-mostrar_orientacoes', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_pos_doutorado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_doutorado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_mestrado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_monografia_de_especializacao', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_tcc', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_iniciacao_cientifica', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_em_andamento_outro_tipo', 'sim'])

        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_pos_doutorado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_doutorado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_mestrado', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_monografia_de_especializacao', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_tcc', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_iniciacao_cientifica', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_orientacao_concluida_outro_tipo', 'sim'])

        self.listaDeParametros.append(['relatorio-incluir_projeto', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_premio', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_participacao_em_evento', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_organizacao_de_evento', 'sim'])
        self.listaDeParametros.append(['relatorio-incluir_internacionalizacao', 'nao'])

        self.listaDeParametros.append(['grafo-mostrar_grafo_de_colaboracoes', 'sim'])
        self.listaDeParametros.append(['grafo-mostrar_todos_os_nos_do_grafo', 'sim'])
        self.listaDeParametros.append(['grafo-considerar_rotulos_dos_membros_do_grupo', 'sim'])

        self.listaDeParametros.append(['grafo-incluir_artigo_em_periodico', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_livro_publicado', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_capitulo_de_livro_publicado', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_texto_em_jornal_de_noticia', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_trabalho_completo_em_congresso', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_resumo_expandido_em_congresso', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_resumo_em_congresso', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_artigo_aceito_para_publicacao', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_apresentacao_de_trabalho', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_outro_tipo_de_producao_bibliografica', 'sim'])

        self.listaDeParametros.append(['grafo-incluir_software_com_registro', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_software_sem_registro', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_produto_tecnologico', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_processo_ou_tecnica', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_trabalho_tecnico', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_outro_tipo_de_producao_tecnica', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_entrevista_mesas_e_comentarios', 'sim'])

        self.listaDeParametros.append(['grafo-incluir_patente', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_programa_computador', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_desenho_industrial', 'sim'])

        self.listaDeParametros.append(['grafo-incluir_producao_artistica', 'sim'])
        self.listaDeParametros.append(['grafo-incluir_grau_de_colaboracao', 'nao'])


        # metricas
        self.listaDeParametros.append(['relatorio-incluir_metricas', 'nao'])

    def identificar_lista_de_colaboradores_endogenos(self):
        self.colaboradores_endogenos = (list([]))
        for i in range(0, self.numeroDeMembros()):
            self.colaboradores_endogenos.append(list([]))
        for i in range(0, self.numeroDeMembros()):
            for j in range(0, self.numeroDeMembros()):
                if i!=j and self.matrizDeAdjacencia[i,j]>0:
                    self.colaboradores_endogenos[i].append( (j, self.matrizDeAdjacencia[i,j]) )
        
        #for i in range(0, self.numeroDeMembros()):
        #    print ( self.colaboradores_endogenos[i] )
