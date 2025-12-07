#!/usr/bin/env make

.PHONY: help install-deps setup-chromedriver check-chrome install clean test

# Variáveis
PYTHON := python3
PIP := pip
VENV_DIR := venv
CHROMEDRIVER_URL_BASE := https://storage.googleapis.com/chrome-for-testing-public
CHROME_VERSION_FILE := .chrome_version

# Cores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(GREEN)scriptLattes Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: setup-venv install-deps setup-chromedriver ## Instalação completa (ambiente virtual + dependências + ChromeDriver)
	@echo "$(GREEN)✓ Instalação completa concluída!$(NC)"
	@echo ""
	@echo "$(YELLOW)Para usar o scriptLattes:$(NC)"
	@echo "  source $(VENV_DIR)/bin/activate"
	@echo "  python3 scriptLattes.py exemplo/teste-01.config"

setup-venv: ## Cria e configura o ambiente virtual Python
	@echo "$(YELLOW)Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✓ Ambiente virtual criado em $(VENV_DIR)$(NC)"

install-deps: ## Instala as dependências Python
	@echo "$(YELLOW)Instalando dependências Python...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)❌ Ambiente virtual não encontrado. Execute 'make setup-venv' primeiro.$(NC)"; \
		exit 1; \
	fi
	$(VENV_DIR)/bin/$(PIP) install --upgrade pip
	$(VENV_DIR)/bin/$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"

check-chrome: ## Verifica a versão do Chrome instalada
	@echo "$(YELLOW)Verificando versão do Chrome...$(NC)"
	@CHROME_VERSION=$$(google-chrome --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1); \
	if [ -z "$$CHROME_VERSION" ]; then \
		CHROME_VERSION=$$(chromium --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1); \
	fi; \
	if [ -z "$$CHROME_VERSION" ]; then \
		echo "$(RED)❌ Chrome/Chromium não encontrado. Instale o Google Chrome ou Chromium.$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Chrome encontrado: $$CHROME_VERSION$(NC)"; \
		echo "$$CHROME_VERSION" > $(CHROME_VERSION_FILE); \
	fi

setup-chromedriver: check-chrome ## Baixa e instala a versão correta do ChromeDriver
	@echo "$(YELLOW)Configurando ChromeDriver...$(NC)"
	@CHROME_VERSION=$$(cat $(CHROME_VERSION_FILE)); \
	echo "Procurando ChromeDriver para Chrome $$CHROME_VERSION..."; \
	CHROMEDRIVER_VERSION=$$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | \
		jq -r ".versions[] | select(.version == \"$$CHROME_VERSION\") | .version" | head -1); \
	if [ -z "$$CHROMEDRIVER_VERSION" ]; then \
		echo "$(YELLOW)⚠️  Versão exata não encontrada. Procurando versão compatível...$(NC)"; \
		CHROME_MAJOR_MINOR=$$(echo $$CHROME_VERSION | cut -d. -f1-3); \
		CHROMEDRIVER_VERSION=$$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | \
			jq -r ".versions[] | select(.version | startswith(\"$$CHROME_MAJOR_MINOR\")) | .version" | tail -1); \
	fi; \
	if [ -z "$$CHROMEDRIVER_VERSION" ]; then \
		echo "$(RED)❌ Não foi possível encontrar ChromeDriver compatível para Chrome $$CHROME_VERSION$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)✓ Usando ChromeDriver versão: $$CHROMEDRIVER_VERSION$(NC)"; \
	DOWNLOAD_URL="$(CHROMEDRIVER_URL_BASE)/$$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"; \
	echo "Baixando de: $$DOWNLOAD_URL"; \
	wget -q "$$DOWNLOAD_URL" -O chromedriver-temp.zip; \
	if [ $$? -eq 0 ]; then \
		unzip -o chromedriver-temp.zip > /dev/null; \
		mv chromedriver-linux64/chromedriver chromedriver; \
		chmod +x chromedriver; \
		rm -rf chromedriver-linux64 chromedriver-temp.zip; \
		echo "$(GREEN)✓ ChromeDriver instalado com sucesso$(NC)"; \
		./chromedriver --version; \
	else \
		echo "$(RED)❌ Erro ao baixar ChromeDriver$(NC)"; \
		exit 1; \
	fi

test: ## Executa o exemplo de teste
	@echo "$(YELLOW)Executando teste com exemplo...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)❌ Ambiente virtual não encontrado. Execute 'make install' primeiro.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "chromedriver" ]; then \
		echo "$(RED)❌ ChromeDriver não encontrado. Execute 'make setup-chromedriver' primeiro.$(NC)"; \
		exit 1; \
	fi
	$(VENV_DIR)/bin/$(PYTHON) scriptLattes.py exemplo/teste-01.config

clean: ## Remove arquivos temporários e cache
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	rm -rf cache/*
	rm -rf exemplo/teste-01
	rm -f $(CHROME_VERSION_FILE)
	rm -f chromedriver-temp.zip
	@echo "$(GREEN)✓ Cache limpo$(NC)"

clean-all: clean ## Remove tudo (incluindo ambiente virtual)
	@echo "$(YELLOW)Removendo ambiente virtual...$(NC)"
	rm -rf $(VENV_DIR)
	rm -f chromedriver
	@echo "$(GREEN)✓ Limpeza completa concluída$(NC)"

update-chromedriver: setup-chromedriver ## Atualiza o ChromeDriver para a versão mais recente compatível

# Comandos para desenvolvimento
dev-install: install ## Alias para install (desenvolvimento)

status: ## Mostra o status da instalação
	@echo "$(YELLOW)Status da instalação:$(NC)"
	@echo -n "Ambiente virtual: "
	@if [ -d "$(VENV_DIR)" ]; then echo "$(GREEN)✓ Instalado$(NC)"; else echo "$(RED)❌ Não instalado$(NC)"; fi
	@echo -n "ChromeDriver: "
	@if [ -f "chromedriver" ]; then echo "$(GREEN)✓ Instalado $$(./chromedriver --version 2>/dev/null | head -1)$(NC)"; else echo "$(RED)❌ Não instalado$(NC)"; fi
	@echo -n "Chrome/Chromium: "
	@CHROME_VERSION=$$(google-chrome --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1); \
	if [ -z "$$CHROME_VERSION" ]; then \
		CHROME_VERSION=$$(chromium --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1); \
	fi; \
	if [ -z "$$CHROME_VERSION" ]; then \
		echo "$(RED)❌ Não encontrado$(NC)"; \
	else \
		echo "$(GREEN)✓ $$CHROME_VERSION$(NC)"; \
	fi