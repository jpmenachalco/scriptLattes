# scriptLattes
O CNPq realiza um enérgico trabalho na integração de bases de currículos acadêmicos de instituições públicas e privadas em uma única plataforma denominada Lattes. Os chamados ``Currículos Lattes'' são considerados um padrão nacional de avaliação representando um histórico das atividades científicas / acadêmicas / profissionais de pesquisadores cadastrados. Os currículos Lattes foram projetados para mostrar informação pública, embora, individual de cada usuário cadastrado na plataforma. Muitas vezes, realizar uma compilação ou sumarização de produções bibliográficas para um grupo de usuários cadastrados de médio ou grande porte (e.g. grupo de professores, departamento de pós-graduação) realmente requer um grande esforço mecânico que muitas vezes é suscetível a falhas.

O scriptLattes é um script GNU-GPL desenvolvido para a extração e compilação automática de: (1) produções bibliográficas, (2) produções técnicas, (3) produções artísticas, (4) orientações, (5) projetos de pesquisa, (6) prêmios e títulos, e (7) grafo de colaborações de um conjunto de pesquisadores cadastrados na plataforma Lattes. Associações de Qualis para as produções acadêmicas publicadas em Congressos e Revistas também são considerados.

O scriptLattes baixa automaticamente os currículos Lattes em formato HTML (livremente disponíveis na rede) de um grupo de pessoas de interesse, compila as listas de produções, tratando apropriadamente as produções duplicadas e similares. São geradas páginas HTML com listas de produções e orientações separadas por tipo e colocadas em ordem cronológica invertida. Adicionalmente são criadas automaticamente vários grafos (redes) de co-autoria entre os membros do grupo de interesse e um mapa de geolocalização dos membros e alunos (de pós-doutorado, doutorado e mestrado) com orientação concluída. Os relatórios gerados permitem avaliar, analisar ou documentar a produção de grupos de pesquisa. Este projeto de software livre foi idealizado por Jesús P. Mena-Chalco e Roberto M. Cesar-Jr em 2005 (IME/USP).
## Pré-requisitos
- Certifique-se de ter o Python 3 instalado no seu computador. 
Se não tiver, você pode baixá-lo em [python.org](https://www.python.org/downloads/).
- Baixe o Chromedriver correspondente à versão do seu navegador. 
Você pode encontrá-lo em [Chromedriver](https://chromedriver.chromium.org/downloads).
- É necessário dar chmod 755 no chrome driver para ele funcionar adequadamente.

## Configuração do Ambiente Virtual
### Clone este repositório para o seu computador
```
git clone https://github.com/jpmenachalco/scriptLattes.git
```
### Navegue até o diretório do seu projeto
```
cd scriptLattes
```
### Crie um ambiente virtual
```
python -m venv venv
```
#### Ative o ambiente virtual no Windows
```
venv\Scripts\activate
```
#### Ative o ambiente virtual no Linux/Mac
```
source venv/bin/activate
```
## Instalação de Dependências

Instale as dependências do projeto usando o arquivo requirements.txt:
```
pip install -r requirements.txt
```
## Execução do Programa
1. Certifique-se de que o ambiente virtual está ativado.
2. Execute o programa:
```
python3 scriptLattes.py exemplo/teste-01.config
```

## Comunicação
- Temos uma área no Discord que pode ser útil para compartilhar dúvidas/sugestões [https://discord.gg/GKKJtU6NRD]
- Contato direto: [jesus.mena@ufabc.edu.br]

## Como referenciar este software
- J. P. Mena-Chalco e R. M. Cesar-Jr. scriptLattes: An open-source knowledge extraction system from the Lattes platform. Journal of the Brazilian Computer Society, vol. 15, n. 4, páginas 31--39, 2009. [http://dx.doi.org/10.1007/BF03194511]
- J. P. Mena-Chalco e R. M. Cesar-Jr. Prospecção de dados acadêmicos de currículos Lattes através de scriptLattes. Capítulo do livro Bibliometria e Cientometria: reflexões teóricas e interfaces São Carlos: Pedro & João, páginas 109-128, 2013. [http://dx.doi.org/10.13140/RG.2.1.5183.8561]

## Notas:
- O scriptLattes não está vinculado ao CNPq. A ferramenta é o resultado de um esforço (independente) realizado com o único intuito de auxiliar as tarefas mecânicas de compilação de informações cadastradas nos Currículos Lattes (publicamente disponíveis). Portanto, o CNPq não é responsável por nenhuma assessoria técnica sobre esta ferramenta.
- O repositorio antigo, no sourceforge não está sendo atualizado.


