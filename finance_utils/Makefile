# Financial Analytics Hub Makefile
# Combined Stock & Forex Dashboard

# Load environment variables
include .env
export

# Project settings
PROJECT_NAME=financial-analytics-hub
PYTHON=/usr/local/bin/python3.13
PIP=pip3
FLASK_APP=app_combined.py
FLASK_PORT=5001

# Data source configuration
DATA_SOURCE_MODE=alpha_vantage
DISABLE_YAHOO_FINANCE=true

# LaTeX report settings
LATEX_OUTPUT_DIR=latex_reports
CONFIG_FILE=config.json

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
MAGENTA=\033[0;35m
CYAN=\033[0;36m
WHITE=\033[1;37m
NC=\033[0m # No Color

# Default target
.PHONY: help
help:
	@echo "$(CYAN)📊 Financial Analytics Hub - Combined Stock & Forex Dashboard$(NC)"
	@echo "$(WHITE)=================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo "$(GREEN)  setup$(NC)          - Install dependencies and setup environment"
	@echo "$(GREEN)  run$(NC)            - Run the Flask dashboard"
	@echo "$(GREEN)  dev$(NC)            - Run in development mode with hot reload"
	@echo "$(GREEN)  test$(NC)           - Run tests and data validation"
	@echo "$(GREEN)  test-api$(NC)       - Test Alpha Vantage API connection"
	@echo "$(GREEN)  test-forex$(NC)     - Run forex API tests"
	@echo "$(GREEN)  clean$(NC)          - Clean cache and temporary files"
	@echo "$(GREEN)  install$(NC)        - Install Python dependencies"
	@echo "$(GREEN)  status$(NC)         - Check API status and usage"
	@echo "$(GREEN)  reports$(NC)        - Generate sample reports"
	@echo "$(GREEN)  latex-report$(NC)   - Generate LaTeX PDF report"
	@echo "$(GREEN)  latex-favorites$(NC) - Generate report for favorite stocks"
	@echo "$(GREEN)  latex-sample$(NC)   - Generate sample LaTeX reports"
	@echo "$(GREEN)  latex-quick$(NC)    - Quick LaTeX report (no auto-open)"
	@echo "$(GREEN)  open-latest$(NC)    - Open most recent PDF report"
	@echo "$(GREEN)  show-config$(NC)    - Show favorite stocks configuration"
	@echo "$(GREEN)  cache-info$(NC)     - Show cache information"
	@echo "$(GREEN)  backup$(NC)         - Backup data and configuration"
	@echo "$(GREEN)  lint$(NC)           - Run code linting"
	@echo "$(GREEN)  docs$(NC)           - Generate documentation"
	@echo "$(GREEN)  docker-build$(NC)   - Build Docker image"
	@echo "$(GREEN)  docker-run$(NC)     - Run in Docker container"
	@echo ""
	@echo "$(BLUE)Environment:$(NC)"
	@echo "  API Key: $(ALPHA_VANTAGE_API_KEY)"
	@echo "  Port: $(FLASK_PORT)"
	@echo "  Cache: $(DATA_CACHE_DIR)"

# Setup environment
.PHONY: setup
setup:
	@echo "$(CYAN)🔧 Setting up Financial Analytics Hub...$(NC)"
	@$(MAKE) install
	@$(MAKE) create-dirs
	@$(MAKE) test-api
	@echo "$(GREEN)✅ Setup complete!$(NC)"

# Install dependencies
.PHONY: install
install:
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install flask plotly alpha-vantage pandas numpy python-dotenv
	@$(PIP) install requests matplotlib seaborn
	@$(PIP) install pytest flake8 black isort
	@echo "$(YELLOW)📄 Checking for LaTeX installation...$(NC)"
	@which pdflatex > /dev/null && echo "$(GREEN)✅ LaTeX found$(NC)" || echo "$(YELLOW)⚠️  LaTeX not found - install MacTeX for PDF generation$(NC)"
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

# Create necessary directories
.PHONY: create-dirs
create-dirs:
	@echo "$(BLUE)📁 Creating directories...$(NC)"
	@mkdir -p $(DATA_CACHE_DIR)
	@mkdir -p logs
	@mkdir -p reports
	@mkdir -p $(LATEX_OUTPUT_DIR)
	@mkdir -p static/css
	@mkdir -p static/js
	@mkdir -p static/img
	@echo "$(GREEN)✅ Directories created$(NC)"

# Run the Flask application
.PHONY: run
run:
	@echo "$(CYAN)🚀 Starting Financial Analytics Hub...$(NC)"
	@echo "$(YELLOW)Access at: http://localhost:$(FLASK_PORT)$(NC)"
	@ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) $(FLASK_APP)

# Run in development mode
.PHONY: dev
dev:
	@echo "$(CYAN)🔧 Starting in development mode...$(NC)"
	@echo "$(YELLOW)Access at: http://localhost:$(FLASK_PORT)$(NC)"
	@FLASK_ENV=development FLASK_DEBUG=True ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) $(FLASK_APP)

# Test API connection
.PHONY: test-api
test-api:
	@echo "$(BLUE)🧪 Testing Alpha Vantage API connection...$(NC)"
	@ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) -c "from alpha_vantage_adapter import AlphaVantageManager; manager = AlphaVantageManager(); manager.test_connection()"

# Run forex API tests
.PHONY: test-forex
test-forex:
	@echo "$(BLUE)🧪 Running forex API tests...$(NC)"
	@$(PYTHON) test_forex_api_comprehensive.py
	@echo "$(GREEN)✅ Forex API tests passed$(NC)"

# Run comprehensive tests
.PHONY: test
test:
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@$(MAKE) test-api
	@$(MAKE) test-forex
	@ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) alpha_vantage_adapter.py
	@echo "$(GREEN)✅ All tests passed$(NC)"

# Check API status
.PHONY: status
status:
	@echo "$(CYAN)📊 API Status Check$(NC)"
	@echo "$(WHITE)==================$(NC)"
	@echo "API Key: $(ALPHA_VANTAGE_API_KEY)"
	@echo "Rate Limit: $(RATE_LIMIT_DELAY) seconds"
	@echo "Daily Limit: $(DAILY_REQUEST_LIMIT) requests"
	@curl -s "http://localhost:$(FLASK_PORT)/api/status" | python3 -m json.tool 2>/dev/null || echo "$(RED)❌ Dashboard not running$(NC)"

# Generate reports
.PHONY: reports
reports:
	@echo "$(BLUE)📋 Generating sample reports...$(NC)"
	@mkdir -p reports
	@curl -s "http://localhost:$(FLASK_PORT)/api/generate_report" -o reports/sample_report_$(shell date +%Y%m%d_%H%M%S).json || echo "$(RED)❌ Dashboard not running$(NC)"
	@echo "$(GREEN)✅ Reports generated in reports/$(NC)"

# Generate LaTeX PDF report
.PHONY: latex-report
latex-report:
	@echo "$(BLUE)📄 Generating LaTeX PDF report...$(NC)"
	@mkdir -p $(LATEX_OUTPUT_DIR)
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) latex_report_generator.py --output $(LATEX_OUTPUT_DIR)
	@echo "$(GREEN)✅ LaTeX report generated in $(LATEX_OUTPUT_DIR)/$(NC)"

# Generate LaTeX report for favorite stocks
.PHONY: latex-favorites
latex-favorites:
	@echo "$(BLUE)📄 Generating LaTeX PDF report for favorite stocks...$(NC)"
	@echo "$(YELLOW)Favorite stocks: $$(cat $(CONFIG_FILE) | python3 -c "import sys, json; print(', '.join(json.load(sys.stdin)['favorite_stocks']))")"
	@mkdir -p $(LATEX_OUTPUT_DIR)
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) latex_report_generator.py --output $(LATEX_OUTPUT_DIR)
	@echo "$(GREEN)✅ Favorite stocks LaTeX report generated in $(LATEX_OUTPUT_DIR)/$(NC)"

# Generate sample LaTeX reports
.PHONY: latex-sample
latex-sample:
	@echo "$(BLUE)📄 Generating sample LaTeX reports...$(NC)"
	@mkdir -p $(LATEX_OUTPUT_DIR)
	@echo "$(YELLOW)Generating comprehensive report...$(NC)"
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) latex_report_generator.py AAPL MSFT --type comprehensive --output $(LATEX_OUTPUT_DIR)
	@echo "$(YELLOW)Generating technical analysis report...$(NC)"
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) latex_report_generator.py GOOGL TSLA --type technical --output $(LATEX_OUTPUT_DIR)
	@echo "$(YELLOW)Generating summary report...$(NC)"
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) latex_report_generator.py NVDA --type summary --output $(LATEX_OUTPUT_DIR)
	@echo "$(GREEN)✅ Sample LaTeX reports generated in $(LATEX_OUTPUT_DIR)/$(NC)"

# Generate quick LaTeX report (no auto-open)
.PHONY: latex-quick
latex-quick:
	@echo "$(BLUE)📄 Generating quick LaTeX report (no auto-open)...$(NC)"
	@mkdir -p $(LATEX_OUTPUT_DIR)
	@DATA_SOURCE_MODE=$(DATA_SOURCE_MODE) DISABLE_YAHOO_FINANCE=$(DISABLE_YAHOO_FINANCE) ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PYTHON) -c "from latex_report_generator import LatexReportGenerator; gen = LatexReportGenerator(auto_open=False); print('Report:', gen.generate_report(['AAPL']))"
	@echo "$(GREEN)✅ Quick LaTeX report generated in $(LATEX_OUTPUT_DIR)/$(NC)"

# Open most recent PDF report
.PHONY: open-latest
open-latest:
	@echo "$(BLUE)📖 Opening most recent PDF report...$(NC)"
	@LATEST_PDF=$$(find $(LATEX_OUTPUT_DIR) -name "*.pdf" -type f -exec ls -t {} + | head -1); \
	if [ -n "$$LATEST_PDF" ]; then \
		echo "Opening: $$LATEST_PDF"; \
		open "$$LATEST_PDF"; \
	else \
		echo "$(RED)❌ No PDF reports found in $(LATEX_OUTPUT_DIR)$(NC)"; \
	fi

# Show cache information
.PHONY: cache-info
cache-info:
	@echo "$(CYAN)📋 Cache Information$(NC)"
	@echo "$(WHITE)==================$(NC)"
	@echo "Cache directory: $(DATA_CACHE_DIR)"
	@echo "Cache files: $$(ls -1 $(DATA_CACHE_DIR)/*.pkl 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Total cache size: $$(du -sh $(DATA_CACHE_DIR) 2>/dev/null | cut -f1)"
	@echo "Latest cache files:"
	@ls -lt $(DATA_CACHE_DIR)/*.pkl 2>/dev/null | head -5 | while read line; do echo "  $$line"; done || echo "  No cache files found"

# Show configuration
.PHONY: show-config
show-config:
	@echo "$(CYAN)⚙️  Configuration$(NC)"
	@echo "$(WHITE)===============$(NC)"
	@echo "Config file: $(CONFIG_FILE)"
	@echo "Favorite stocks: $$(cat $(CONFIG_FILE) | python3 -c "import sys, json; print(', '.join(json.load(sys.stdin)['favorite_stocks']))")"
	@echo "Total favorite stocks: $$(cat $(CONFIG_FILE) | python3 -c "import sys, json; print(len(json.load(sys.stdin)['favorite_stocks']))")"

# Clean cache and temporary files
.PHONY: clean
clean:
	@echo "$(YELLOW)🧹 Cleaning cache and temporary files...$(NC)"
	@rm -rf $(DATA_CACHE_DIR)/*
	@rm -rf logs/*.log
	@rm -rf __pycache__
	@rm -rf *.pyc
	@rm -rf .pytest_cache
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

# Backup data and configuration
.PHONY: backup
backup:
	@echo "$(BLUE)💾 Creating backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		$(DATA_CACHE_DIR) reports .env *.py templates/ static/ || true
	@echo "$(GREEN)✅ Backup created in backups/$(NC)"

# Code linting
.PHONY: lint
lint:
	@echo "$(BLUE)🔍 Running code linting...$(NC)"
	@flake8 --max-line-length=88 --ignore=E203,W503 *.py || true
	@black --check --diff *.py || true
	@isort --check-only --diff *.py || true
	@echo "$(GREEN)✅ Linting complete$(NC)"

# Format code
.PHONY: format
format:
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@black *.py
	@isort *.py
	@echo "$(GREEN)✅ Code formatted$(NC)"

# Generate documentation
.PHONY: docs
docs:
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@mkdir -p docs
	@echo "# Stock Analysis Dashboard Documentation" > docs/README.md
	@echo "" >> docs/README.md
	@echo "## API Endpoints" >> docs/README.md
	@echo "- \`/\` - Main dashboard" >> docs/README.md
	@echo "- \`/stock/<symbol>\` - Individual stock analysis" >> docs/README.md
	@echo "- \`/api/stocks\` - List all stocks" >> docs/README.md
	@echo "- \`/api/stock/<symbol>\` - Get stock data" >> docs/README.md
	@echo "- \`/api/status\` - API status" >> docs/README.md
	@echo "- \`/reports\` - Generate reports" >> docs/README.md
	@echo "$(GREEN)✅ Documentation generated in docs/$(NC)"

# Docker build
.PHONY: docker-build
docker-build:
	@echo "$(BLUE)🐳 Building Docker image...$(NC)"
	@docker build -t $(PROJECT_NAME) .
	@echo "$(GREEN)✅ Docker image built$(NC)"

# Docker run
.PHONY: docker-run
docker-run:
	@echo "$(CYAN)🐳 Running Docker container...$(NC)"
	@docker run -p $(FLASK_PORT):$(FLASK_PORT) -e ALPHA_VANTAGE_API_KEY=$(ALPHA_VANTAGE_API_KEY) $(PROJECT_NAME)

# Install development dependencies
.PHONY: install-dev
install-dev:
	@echo "$(BLUE)🔧 Installing development dependencies...$(NC)"
	@$(PIP) install pytest pytest-cov black flake8 isort mypy
	@echo "$(GREEN)✅ Development dependencies installed$(NC)"

# Show project statistics
.PHONY: stats
stats:
	@echo "$(CYAN)📊 Project Statistics$(NC)"
	@echo "$(WHITE)==================$(NC)"
	@echo "Python files: $(shell find . -name "*.py" | wc -l)"
	@echo "HTML templates: $(shell find templates -name "*.html" | wc -l)"
	@echo "Total lines of code: $(shell find . -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "Cache size: $(shell du -sh $(DATA_CACHE_DIR) 2>/dev/null || echo '0B')"
	@echo "Log files: $(shell ls logs/*.log 2>/dev/null | wc -l)"

# Production deployment
.PHONY: deploy
deploy:
	@echo "$(MAGENTA)🚀 Preparing for production deployment...$(NC)"
	@echo "$(YELLOW)⚠️  This is a development version. For production:$(NC)"
	@echo "1. Use a production WSGI server (gunicorn, uWSGI)"
	@echo "2. Set up proper SSL certificates"
	@echo "3. Configure environment variables securely"
	@echo "4. Set up monitoring and logging"
	@echo "5. Use a production database"

# Quick start
.PHONY: quick-start
quick-start:
	@echo "$(CYAN)⚡ Quick Start$(NC)"
	@echo "$(WHITE)=============$(NC)"
	@$(MAKE) setup
	@$(MAKE) run

# Emergency stop
.PHONY: stop
stop:
	@echo "$(RED)🛑 Stopping all processes...$(NC)"
	@pkill -f "$(FLASK_APP)" || true
	@echo "$(GREEN)✅ Processes stopped$(NC)"

# Show logs
.PHONY: logs
logs:
	@echo "$(BLUE)📋 Recent logs:$(NC)"
	@tail -50 logs/app.log 2>/dev/null || echo "$(YELLOW)No logs found$(NC)"

# Health check
.PHONY: health
health:
	@echo "$(BLUE)🏥 Health check...$(NC)"
	@curl -s -f "http://localhost:$(FLASK_PORT)/api/status" > /dev/null && echo "$(GREEN)✅ Service is healthy$(NC)" || echo "$(RED)❌ Service is down$(NC)"
