# scriptLattes


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

