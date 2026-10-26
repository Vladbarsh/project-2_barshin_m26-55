.PHONY: install run build publish lint

install:
	uv sync

run:
	uv run database

build:
	uv build

publish: build
	uvx twine check dist/*

lint:
	uv run ruff check .
