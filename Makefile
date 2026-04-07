.PHONY: install build test lint clean package-linux package-windows package-macos

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
	rm -rf dist/ build/ *.egg-info .pytest_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

package-linux:
	pyinstaller --name pith --onefile pith/cli/__init__.py

package-windows:
	pyinstaller --name pith --onefile pith/cli/__init__.py

package-macos:
	pyinstaller --name pith --onefile pith/cli/__init__.py
