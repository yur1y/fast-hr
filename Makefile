.PHONY: help

PROVIDERS = ollama groq openai anthropic google vllm together
OBS_PROVIDERS = langfuse langsmith phoenix none

.SILENT:

help:
	@echo "TracePilot Switcher"
	@echo ""
	@echo "Usage:"
	@echo "  make use-llm-<provider>   Switch LLM provider"
	@echo "  make use-obs-<provider>   Switch observability provider"
	@echo "  make current              Show active providers"
	@echo "  make list                 List all providers"
	@echo ""
	@echo "LLM providers: ollama, groq, openai, anthropic, google, vllm, together"
	@echo "Obs providers: langfuse, langsmith, phoenix, none"

list:
	@echo "LLM providers:"
	@echo "  ollama      - Local (http://localhost:11434)"
	@echo "  groq        - Cloud, fast (OPENAI_API_KEY=gsk_...)"
	@echo "  openai      - Cloud (OPENAI_API_KEY=sk-...)"
	@echo "  anthropic   - Cloud (ANTHROPIC_API_KEY=sk-ant-...)"
	@echo "  google      - Cloud (GOOGLE_API_KEY=...)"
	@echo "  vllm        - Local OpenAI-compatible"
	@echo "  together    - Cloud (OPENAI_API_KEY=...)"
	@echo ""
	@echo "Observability providers:"
	@echo "  langfuse    - Cloud or self-hosted"
	@echo "  langsmith   - Cloud"
	@echo "  phoenix     - Self-hosted"
	@echo "  none        - No observability"

current:
	@if [ ! -f .env ]; then \
		echo "No .env file found. Run: make use-llm-ollama"; \
		exit 1; \
	fi
	@echo "Active config:"
	@grep -E "^(TP_LLM_PROVIDER|TP_OBSERVABILITY_PROVIDER|TP_OPENAI_BASE_URL|TP_OPENAI_MODEL)=" .env || true

use-llm-%:
	@cp -n .env.example .env 2>/dev/null || true
	@PROVIDER="$*"; \
	case $$PROVIDER in \
		ollama) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=ollama/' .env; \
			sed -i 's|^TP_OPENAI_BASE_URL=.*|TP_OPENAI_BASE_URL=http://localhost:11434/v1|' .env; \
			sed -i 's|^TP_OPENAI_MODEL=.*|TP_OPENAI_MODEL=qwen3:4b|' .env; \
			sed -i 's|^TP_OPENAI_API_KEY=.*|TP_OPENAI_API_KEY=ollama|' .env; \
			sed -i 's|^TP_OLLAMA_BASE_URL=.*|TP_OLLAMA_BASE_URL=http://localhost:11434|' .env; \
			sed -i 's|^TP_OLLAMA_MODEL=.*|TP_OLLAMA_MODEL=qwen3:4b|' .env; \
			sed -i 's|^TP_OLLAMA_NUM_CTX=.*|TP_OLLAMA_NUM_CTX=2048|' .env; \
			;; \
		groq) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=groq/' .env; \
			sed -i 's|^TP_OPENAI_BASE_URL=.*|TP_OPENAI_BASE_URL=https://api.groq.com/openai/v1|' .env; \
			sed -i 's|^TP_OPENAI_MODEL=.*|TP_OPENAI_MODEL=llama-3.3-70b-versatile|' .env; \
			;; \
		openai) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=openai/' .env; \
			sed -i 's|^TP_OPENAI_BASE_URL=.*|TP_OPENAI_BASE_URL=https://api.openai.com/v1|' .env; \
			sed -i 's|^TP_OPENAI_MODEL=.*|TP_OPENAI_MODEL=gpt-4o|' .env; \
			;; \
		anthropic) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=anthropic/' .env; \
			;; \
		google) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=google/' .env; \
			;; \
		vllm) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=vllm/' .env; \
			sed -i 's|^TP_OPENAI_BASE_URL=.*|TP_OPENAI_BASE_URL=http://localhost:8000/v1|' .env; \
			sed -i 's|^TP_OPENAI_MODEL=.*|TP_OPENAI_MODEL=meta-llama/Llama-2-7b-chat-hf|' .env; \
			;; \
		together) \
			sed -i 's/^TP_LLM_PROVIDER=.*/TP_LLM_PROVIDER=together/' .env; \
			sed -i 's|^TP_OPENAI_BASE_URL=.*|TP_OPENAI_BASE_URL=https://api.together.xyz/v1|' .env; \
			sed -i 's|^TP_OPENAI_MODEL=.*|TP_OPENAI_MODEL=meta-llama/Llama-2-7b-chat-hf|' .env; \
			;; \
		*) \
			echo "Unknown LLM provider: $$PROVIDER"; \
			exit 1; \
			;; \
	esac; \
	echo "Switched LLM to: $$PROVIDER"; \
	grep -E "^(TP_LLM_PROVIDER|TP_OPENAI_BASE_URL|TP_OPENAI_MODEL|TP_OPENAI_API_KEY|TP_OLLAMA_BASE_URL|TP_OLLAMA_MODEL|TP_OLLAMA_NUM_CTX)=" .env || true

use-obs-%:
	@cp -n .env.example .env 2>/dev/null || true
	@PROVIDER="$*"; \
	case $$PROVIDER in \
		langfuse) \
			sed -i 's/^TP_OBSERVABILITY_PROVIDER=.*/TP_OBSERVABILITY_PROVIDER=langfuse/' .env; \
			;; \
		langsmith) \
			sed -i 's/^TP_OBSERVABILITY_PROVIDER=.*/TP_OBSERVABILITY_PROVIDER=langsmith/' .env; \
			;; \
		phoenix) \
			sed -i 's/^TP_OBSERVABILITY_PROVIDER=.*/TP_OBSERVABILITY_PROVIDER=phoenix/' .env; \
			;; \
		none) \
			sed -i 's/^TP_OBSERVABILITY_PROVIDER=.*/TP_OBSERVABILITY_PROVIDER=none/' .env; \
			;; \
		*) \
			echo "Unknown observability provider: $$PROVIDER"; \
			exit 1; \
			;; \
	esac; \
	echo "Switched observability to: $$PROVIDER"; \
	grep -E "^(TP_OBSERVABILITY_PROVIDER)=" .env || true
