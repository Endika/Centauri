PYTHON = python
PIP = pip
DOCKER_COMPOSE = docker-compose

.PHONY: help install lint format build up down logs clean chat

help: ## Display the list of available commands
	@echo "Command list:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install necessary dependencies
	$(PIP) install -r requirements-dev.txt

lint: ## Run flake8 to check for style errors
	flake8 app

format: ## Format the code using black and isort
	black app --line-length=80
	isort app

test: ## Run all tests with pytest
	pytest --cov=app tests

build: ## Build the Docker Compose services
	$(DOCKER_COMPOSE) build

up: ## Start the Docker Compose services in detached mode
	$(DOCKER_COMPOSE) up -d

down: ## Stop and remove the Docker Compose services
	$(DOCKER_COMPOSE) down

logs: ## Display logs from Docker Compose services in real-time
	$(DOCKER_COMPOSE) logs -f

clean: ## Remove Python cache files and orphaned Docker volumes
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.pyc" -exec rm -r {} +
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

chat: ## Connect to the WebSocket server using wscat
	@if [ $$(docker ps -q -f name=centauri-client) ]; then \
		docker exec -it centauri-client wscat -c ws://centauri:8000/chat/; \
	else \
		echo "Error: The container 'centauri-client' is not running."; \
	fi
