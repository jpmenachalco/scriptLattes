#!/usr/bin/python
# encoding: utf-8
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


import numpy
import scipy
import tqdm


class AuthorRank:
    matriz = None
    vectorRank = None

    def __init__(self, matriz, iteracoes):
        self.matriz = matriz
        self.vectorRank = numpy.ones(matriz.shape[0], dtype=numpy.float32)
        #self.vectorRank = scipy.ones(matriz.shape[0], dtype=float)
        print("\n[CALCULANDO AUTHOR-RANK (PROCESSO ITERATIVO)]")
        with tqdm.tqdm(total=iteracoes) as progress_bar:
            for index in range(0, iteracoes):
                progress_bar.update(1)
                self.vectorRank = self.calcularRanks(self.vectorRank)

    def calcularRanks(self, vectorRank):
        vectorRankNovo = numpy.zeros(len(vectorRank), dtype=numpy.float32)
        #vectorRankNovo = scipy.zeros_like(self.vectorRank, dtype=float)
        d = 0.85  # dumping factor (fator de amortecimento)
        for i in range(0, len(vectorRank)):
            soma = 0
            for j in range(0, len(vectorRank)):
                soma += vectorRank[j] * self.matriz[j, i]
            vectorRankNovo[i] = (1 - d) + d * soma
        return vectorRankNovo
