# Use to build modules

.PHONY: test

git:
	git add .
	git commit -m auto
	git push


all:
	make -C bluepy

test:
	@make -C pyclient test





