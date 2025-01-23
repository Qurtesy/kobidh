test:
	python3 -m pytest test/all.py --log-cli-level=INFO
	
test-kobidh-debug:
	python3 -m pytest test/all.py --log-cli-level=DEBUG

.PHONY: test
