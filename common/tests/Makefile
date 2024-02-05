
test:

	@echo Diffs should be silent
	@python3 testdump.py > aa
	@diff -w testdump.org aa
	@python3 testwrapper.py > aa
	@diff testwrapper.org aa
	@python3 testpacker.py > aa
	@diff testpacker.org aa
	@rm -f aa

