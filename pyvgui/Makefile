# Makefile

.PHONY: docs

all:
	@echo "Targets: clean docs"

clean:
	rm -f voters.p*

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
