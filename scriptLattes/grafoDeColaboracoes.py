#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import networkx as nx

class GrafoDeColaboracoes:
    def __init__(self, grupo):
        self.grupo = grupo

    def criar_grafo_com_pesos(self):
        # Atribui cores hexadecimais aos membros
        for membro in self.grupo.listaDeMembros:
            if len(self.grupo.listaDeRotulos) == 1:
                cor_fg, cor_bg = '#ffffff', '#33a02c'  # branco sobre verde escuro
            else:
                idx = self.grupo.listaDeRotulos.index(membro.rotulo)
                cor_fg, cor_bg = self.atribuir_cor_legal(idx)
            membro.rotuloCorFG = cor_fg  
            membro.rotuloCorBG = cor_bg  

        G = nx.Graph()
        n = self.grupo.numeroDeMembros()

        # Cria nós com atributos, cor hex e viz para compatibilidade GEXF
        for i, membro in enumerate(self.grupo.listaDeMembros):
            peso = int(self.grupo.vetorDeCoAutoria[i])
            if peso > 0 or self.grupo.obterParametro('grafo-mostrar_todos_os_nos_do_grafo'):
                label = f"{membro.nomeCompleto}"
                # Converte cor de fundo hex para RGB para viz
                hex_bg = membro.rotuloCorBG.lstrip('#')
                r = int(hex_bg[0:2], 16)
                g = int(hex_bg[2:4], 16)
                b = int(hex_bg[4:6], 16)
                viz_color = {'r': r, 'g': g, 'b': b, 'a': 1.0}

                G.add_node(
                    membro.idMembro,
                    label=label,
                    url=membro.url,
                    publicacoesEmCoautoria = peso,
                    atualizacaoCV=getattr(membro, 'atualizacaoCV', ''),
                    resumo=getattr(membro, 'textoResumo', ''),
                    rotulo=getattr(membro, 'rotulo', ''),
                    periodo=getattr(membro, 'periodo', ''),
                    nomePrimeiraGrandeArea=getattr(membro, 'nomePrimeiraGrandeArea', ''),
                    nomePrimeiraArea=getattr(membro, 'nomePrimeiraArea', ''),
                    instituicao=getattr(membro, 'instituicao', ''),
                    enderecoProfissional=getattr(membro, 'enderecoProfissional', ''),
                    artigosPeriodicos=len(membro.listaArtigoEmPeriodico),
                    artigosEventos=len(membro.listaTrabalhoCompletoEmCongresso),
                    capitulosDeLivros=len(membro.listaCapituloDeLivroPublicado),
                    livros=len(membro.listaLivroPublicado),
                    color=membro.rotuloCorBG,    # cor de fundo em hex para JS
                    fontColor=membro.rotuloCorFG, # cor do texto em hex para JS
                    viz={'color': viz_color}       # para exportação GEXF
                )

        # Arestas (colaborações ponderadas)
        for i in range(n):
            for j in range(i+1, n):
                peso = self.grupo.matrizDeAdjacencia[i, j]
                if peso > 0:
                    u = self.grupo.listaDeMembros[i].idMembro
                    v = self.grupo.listaDeMembros[j].idMembro
                    G.add_edge(u, v, weight=peso)

        # Calcula métricas dos vértices (exemplo: grau)
        for node in G.nodes():
            G.nodes[node]['degree'] = G.degree(node)
        
        # calcula layout
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=400, scale=0.7)
        for n, (x, y) in pos.items():
            G.nodes[n]['x']    = float(x)
            G.nodes[n]['y']    = float(y)
            G.nodes[n]['size'] = (G.degree[n] or 1 ) + 1

        # Gera o grafo e exporta para GEXF com cores viz e atributos extras
        arquivo = os.path.join(self.grupo.obterParametro('global-diretorio_de_saida'), 'grafo_de_colaboracoes.gexf')
        nx.write_gexf(G, arquivo)
        print(f"[INFO] Grafo salvo em: {arquivo}")
        
        return G

    def atribuir_cor_legal(self, indice):
        """
        Retorna (cor_fg, cor_bg) em formato hexadecimal para paleta qualitativa (12 cores).
        Texto sempre branco para contraste.
        """
        paleta_hex = [
            '#8dd3c7', '#fb8072', '#80b1d3', '#fdb462',
            '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd',
            '#ccebc5', '#ffed6f', '#ffffb3', '#bebada'
        ]
        cor_bg = paleta_hex[indice % len(paleta_hex)]
        cor_fg = '#ffffff'
        return cor_fg, cor_bg
