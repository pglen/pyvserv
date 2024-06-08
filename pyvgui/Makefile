# Makefile

.PHONY: docs

all:
	@echo "Targets: clean cleanall docs"

cleanall:
	@rm -rf ~/pyvclient/*

clean:
	@rm -f voters.p*
	@-find . -name "__pycache__" -exec rm -rf {} \;
	@-find . -name "*.pyc" -exec rm -rf {} \;

XPATH=PYTHONPATH=../pyvcommon:../../pyvcommon python3 -W ignore::DeprecationWarning `which pdoc` --force --html

docs:
	@echo Use Makefile in main directory for docs

	@#${XPATH} -o docs pyvpeople.py
	@#${XPATH} -o docs pyvservui.py
	@#${XPATH} -o docs pyvballot.py
	@#${XPATH} -o docs pyvvote.py
	@#${XPATH} -o docs pyvtally.py
	@#${XPATH} -o docs pyvcpanel.py

# EOF
