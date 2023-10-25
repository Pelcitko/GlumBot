# Makefile pro základní operace s Poetry a spouštění programu

# Spustí virtuální prostředí Poetry
shell:
	poetry shell

# Instaluje závislosti projektu
install:
	poetry install

# Aktualizuje závislosti projektu
update:
	poetry update

# Spustí hlavní skript programu
start:
	poetry run python main.py

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
