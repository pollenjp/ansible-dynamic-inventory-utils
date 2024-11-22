
.PHONY: pre-commit
pre-commit:
	${MAKE} lint
	${MAKE} fmt
	${MAKE} test

.PHONY: lint
lint:
	uv run ruff check
	uv run pyright

.PHONY: fmt
fmt:
	uv run ruff format

.PHONY: test
test:
	uv run pytest
