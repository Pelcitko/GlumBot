# Makefile pro základní operace s Poetry a spouštění programu
# Instaluje Poetry, pokud není nalezena v systému.
install-poetry:
	@if [ -z "$(shell which poetry 2>/dev/null)" ]; then \
		echo "Instalace Poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	else \
		echo "Poetry je již nainstalováno."; \
	fi

# Instaluje závislosti projektu
install: install-poetry
	poetry install

# Aktualizuje závislosti projektu
update:
	poetry update

# Spustí virtuální prostředí Poetry
shell:
	poetry shell

# Spustí hlavní skript programu
start:
	poetry run python src/main.py

# Kontroluje formátování kódu pomocí black a flake8
check:
	poetry run black --check . && poetry run flake8

# Formátuje kód pomocí black
format:
	poetry run black .

# Spustí testy projektu
test:
	poetry run pytest

# Odstraní virtuální prostředí a cache Poetry
clean:
	poetry env remove $(poetry env info -p) && rm -rf .pytest_cache

.PHONY: shell install update run check format test clean
