# ============================================================
# Makefile — Arc Fleet Campaign
# All common commands in one place. LLM-first dev friendly.
# Usage: make help
# ============================================================

PYTHON      := python3
PIP         := pip3
PROJECT_ID  := $(shell grep GCP_PROJECT_ID .env 2>/dev/null | cut -d= -f2 || echo arc-fleet-campaign)
REGION      := $(shell grep GCP_REGION .env 2>/dev/null | cut -d= -f2 || echo us-central1)
ZONE        := $(REGION)-a

.DEFAULT_GOAL := help

# ── HELP ─────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "Arc Fleet Campaign — Command Reference"
	@echo "======================================="
	@echo ""
	@echo "  SETUP"
	@echo "  make install          Install Python deps + Playwright"
	@echo "  make env              Copy .env.example → .env"
	@echo "  make wizard           Interactive credential setup"
	@echo "  make verify           Verify .env + module health"
	@echo ""
	@echo "  CAMPAIGNS"
	@echo "  make dry-run          Dry-run all campaigns (email)"
	@echo "  make dry-run-mkz      Dry-run MKZ only"
	@echo "  make health           Show all module health"
	@echo "  make list             List campaigns + stats"
	@echo ""
	@echo "  STANDUP"
	@echo "  make standup          Send standup reminder (all team)"
	@echo "  make standup-run      Run interactive standup"
	@echo ""
	@echo "  TESTS"
	@echo "  make test             Run full pytest suite"
	@echo "  make test-v           Verbose pytest"
	@echo "  make test-fast        Skip slow integration tests"
	@echo ""
	@echo "  SERVER"
	@echo "  make server           Start Flask on :8080"
	@echo "  make server-check     curl health check"
	@echo ""
	@echo "  GPU / GCP"
	@echo "  make gpu-list         Show GPU catalog + prices"
	@echo "  make gpu-create       Spin up T4 (TYPE=t4|v100|a100-40)"
	@echo "  make gpu-budget       Estimate \$$300 credit usage"
	@echo "  make gpu-local        Setup local V100 server instructions"
	@echo "  make gcp-setup        Print all GCP setup commands"
	@echo ""
	@echo "  UTILS"
	@echo "  make reset            Reset DB + logs"
	@echo "  make clean            Remove __pycache__, .pyc files"
	@echo "  make context          Print CLAUDE.md (paste to LLM)"
	@echo ""


# ── SETUP ────────────────────────────────────────────────────────────────────
.PHONY: install
install:
	$(PIP) install -r requirements.txt
	playwright install chromium
	@echo "✓ Dependencies installed"

.PHONY: env
env:
	@if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env from .env.example"; \
	else echo "⚠  .env already exists"; fi

.PHONY: wizard
wizard:
	$(PYTHON) -m config.loader --wizard

.PHONY: verify
verify:
	$(PYTHON) -m config.loader --verify
	$(PYTHON) -c "from modules import ModuleRegistry; r = ModuleRegistry(); print(r); [print(f'  {k}: {v.health_check()}') for k,v in r._modules.items()]"


# ── CAMPAIGNS ─────────────────────────────────────────────────────────────────
.PHONY: health
health:
	$(PYTHON) -c "from modules import ModuleRegistry; r = ModuleRegistry(); import json; print(json.dumps(r.health_report(), indent=2))"

.PHONY: list
list:
	$(PYTHON) cli.py --list

.PHONY: dry-run
dry-run:
	$(PYTHON) cli.py --vehicle all --module email --dry-run

.PHONY: dry-run-mkz
dry-run-mkz:
	$(PYTHON) cli.py --vehicle mkz --module email --dry-run

.PHONY: formfill-mkz
formfill-mkz:
	$(PYTHON) cli.py --vehicle mkz --module formfill


# ── STANDUP ──────────────────────────────────────────────────────────────────
.PHONY: standup
standup:
	$(PYTHON) -m standup.bot --notify

.PHONY: standup-run
standup-run:
	$(PYTHON) -m standup.bot --run

.PHONY: standup-schedule
standup-schedule:
	$(PYTHON) -m standup.bot --schedule


# ── TESTS ────────────────────────────────────────────────────────────────────
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v --tb=short

.PHONY: test-v
test-v:
	$(PYTHON) -m pytest tests/ -v --tb=long -s

.PHONY: test-fast
test-fast:
	$(PYTHON) -m pytest tests/ -v --tb=short -m "not slow"

.PHONY: test-campaigns
test-campaigns:
	$(PYTHON) -m pytest tests/test_campaigns.py -v

.PHONY: test-modules
test-modules:
	$(PYTHON) -m pytest tests/test_modules.py -v


# ── SERVER ───────────────────────────────────────────────────────────────────
.PHONY: server
server:
	$(PYTHON) app.py

.PHONY: server-check
server-check:
	curl -s http://localhost:8080/api/health | python3 -m json.tool


# ── GPU / GCP ────────────────────────────────────────────────────────────────
GPU_TYPE ?= t4

.PHONY: gpu-list
gpu-list:
	./scripts/gpu_setup.sh --list-gpus

.PHONY: gpu-budget
gpu-budget:
	./scripts/gpu_setup.sh --budget 300

.PHONY: gpu-create
gpu-create:
	./scripts/gpu_setup.sh --create $(GPU_TYPE)

.PHONY: gpu-local
gpu-local:
	./scripts/gpu_setup.sh --local-setup

.PHONY: gcp-setup
gcp-setup:
	$(PYTHON) -m config.loader --gcp-commands


# ── VOICE TEST ────────────────────────────────────────────────────────────────
.PHONY: voice-test
voice-test:
	./scripts/voice_test.sh --tts

.PHONY: voice-robot
voice-robot:
	./scripts/voice_test.sh --robot


# ── UTILS ────────────────────────────────────────────────────────────────────
.PHONY: reset
reset:
	rm -f data/tracker.db
	rm -rf logs/* screenshots/*
	@echo "✓ DB + logs cleared"

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cache cleared"

.PHONY: context
context:
	@cat CLAUDE.md

.PHONY: context-arch
context-arch:
	@cat ARCHITECTURE.md
