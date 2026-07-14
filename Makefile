install:
	pip install -r requirements.txt

test:
	pytest

run:
	python src/etl/loader.py

format:
	black .

lint:
	flake8 src tests

clean:
	rm -rf __pycache__