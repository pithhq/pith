.PHONY: install build test lint clean build-linux build-mac build-windows appimage

install:
	pip install -e ".[dev]"

build:
	python -m build

test:
	pytest

lint:
	ruff check pith/ tests/
	black --check pith/ tests/

clean:
	rm -rf dist/ *.egg-info .pytest_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

build-linux:
	bash build/build.sh

build-mac:
	bash build/build.sh

build-windows:
	powershell -ExecutionPolicy Bypass -File build/build.ps1

appimage: build-linux
	bash build/make-appimage.sh
