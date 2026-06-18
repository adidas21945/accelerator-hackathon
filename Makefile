.PHONY: help verify smoke evals validate cheatsheet gifs
.DEFAULT_GOAL := help

help:  ## List targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed -E 's/:.*## / — /' | sort

verify:  ## No-model verification matrix (what CI runs)
	@bash tests/verify.sh

smoke:  ## Run every project offline on the local model
	@bash tests/smoke.sh

evals:  ## Run all project evals (needs local model; slow)
	@for d in projects/*/*/; do \
		[ -f "$$d/evals/evals.json" ] && echo "── $$d" && uv run python -m agentkit.evals "$$d"; \
	done

validate:  ## Validate every skill against the agentskills spec
	@for d in $$(find projects -name SKILL.md -exec dirname {} \;); do \
		uv run agentskills validate "$$d"; \
	done

cheatsheet:  ## Rebuild docs/cheat-sheet.pdf
	@uv run --with reportlab python tools/make_cheatsheet.py

gifs:  ## Re-record the README terminal GIFs (needs vhs + ffmpeg)
	@vhs tools/dungeon-mastah.tape && vhs tools/chief-of-stuff.tape
