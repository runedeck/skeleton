.PHONY: help install validate worktree worktree-done

help:
	@echo "  make install    install check tools and activate hooks"
	@echo "  make validate   run commit-stage checks"
	@echo "  make worktree   create an agent worktree: make worktree BRANCH=change/x IDENTITY=<model-id> [HARNESS=<harness>]"
	@echo "  make worktree-done   remove a merged worktree or jj workspace: make worktree-done BRANCH=change/x"

install:
	git config core.hooksPath .githooks
	chmod +x .githooks/* scripts/* 2>/dev/null || true
	@if [ -d .jj ] && command -v jj >/dev/null 2>&1; then \
	    jj config set --repo aliases.push "[\"util\",\"exec\",\"--\",\"bash\",\"$$(git rev-parse --show-toplevel)/.githooks/jj-push\"]"; \
	    echo "jj detected: 'jj push' runs the pre-push checks, then 'jj git push'"; \
	elif [ -d .jj ]; then \
	    echo "warn: .jj/ present but jj not on PATH; 'jj push' checks are not wired"; \
	fi
	@bash scripts/install-tools

validate:
	@bash .githooks/pre-commit --all-files

# Create a worktree whose commits carry a listed model identity.
# HARNESS selects one identity when a model ID has multiple harness entries.
worktree:
	@[ -n "$(BRANCH)" ] && [ -n "$(IDENTITY)" ] \
	    || { echo "usage: make worktree BRANCH=change/x IDENTITY=<model-id> [HARNESS=<harness>]"; exit 2; }
	@set -e; \
	identities=$$(awk -v model='$(IDENTITY)' -v harness='$(HARNESS)' '\
	    /^[^ #]/ { in_authors = ($$0 == "authors:") } \
	    in_authors && /^    - / { \
	        identity = $$0; sub(/^    - /, "", identity); \
	        suffix = "@" harness ".noreply.nexus.local>"; \
	        if (index(identity, "(" model ") <") \
	            && (harness == "" || substr(identity, length(identity) - length(suffix) + 1) == suffix)) \
	            print identity; \
	    }' authors.yaml); \
	count=$$(printf '%s\n' "$$identities" | awk 'NF { count++ } END { print count + 0 }'); \
	[ "$$count" -gt 0 ] \
	    || { echo "identity '$(IDENTITY)' with harness '$(HARNESS)' is not in authors.yaml"; exit 1; }; \
	[ "$$count" -eq 1 ] \
	    || { echo "identity '$(IDENTITY)' is ambiguous; set HARNESS=<harness>"; exit 1; }; \
	identity=$$identities; \
	name=$$(printf '%s' "$(BRANCH)" | tr '/' '-'); \
	author=$${identity% <*}; \
	address=$${identity##*<}; address=$${address%>}; \
	if [ -d .jj ]; then \
	    jj workspace add --name "$$name" ".workspaces/$$name"; \
	    echo "jj workspace .workspaces/$$name for $(BRANCH)"; \
	    echo "author with: export JJ_USER='$$author' JJ_EMAIL='$$address'"; \
	    echo "push with the jj push alias after: jj bookmark create $(BRANCH)"; \
	else \
	    git config extensions.worktreeConfig true; \
	    git worktree add ".worktrees/$$name" -b "$(BRANCH)"; \
	    git -C ".worktrees/$$name" config --worktree user.name "$$author"; \
	    git -C ".worktrees/$$name" config --worktree user.email "$$address"; \
	    echo "worktree .worktrees/$$name on $(BRANCH) authors as $$identity"; \
	fi

# Remove a worktree whose branch holds no unmerged commits, then
# delete the branch. Landing the work includes this step.
worktree-done:
	@[ -n "$(BRANCH)" ] || { echo "usage: make worktree-done BRANCH=change/x"; exit 2; }
	@set -e; \
	name=$$(printf '%s' "$(BRANCH)" | tr '/' '-'); \
	if [ -d .jj ]; then \
	    path=".workspaces/$$name"; \
	    [ -d "$$path" ] || { echo "no workspace at $$path"; exit 1; }; \
	    unmerged=$$(jj log --no-graph -T 'change_id.short() ++ " "' -r "mutable() & ::$$name@ & ~empty() & ~::trunk()" 2>/dev/null); \
	    [ -z "$$unmerged" ] || { echo "workspace $$name holds unmerged changes: $$unmerged"; exit 1; }; \
	    jj workspace forget "$$name"; \
	    (command -v trash >/dev/null 2>&1 && trash "$$path") || rm -rf "$$path"; \
	    echo "removed workspace $$path"; \
	else \
	    path=".worktrees/$$name"; \
	    [ -d "$$path" ] || { echo "no worktree at $$path"; exit 1; }; \
	    dirty=$$(git -C "$$path" status --porcelain); \
	    [ -z "$$dirty" ] || { echo "the worktree at $$path is dirty; commit or discard first"; exit 1; }; \
	    git fetch origin; \
	    default=$$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo origin/main); \
	    count=$$(git rev-list --count "$$default..$(BRANCH)"); \
	    [ "$$count" -eq 0 ] || { echo "$(BRANCH) carries $$count commits that are not on $$default"; exit 1; }; \
	    git worktree remove "$$path"; \
	    git branch -d "$(BRANCH)"; \
	    echo "removed $$path and deleted $(BRANCH)"; \
	fi
