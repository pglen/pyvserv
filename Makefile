# Use to build modules

.PHONY: test clean

all:
	@echo Targets: all git build build3 test clean deb cleankeys

git:
	git add .
	git commit -m auto
	git push

build:
	@make -C bluepy build

build3:
	@make -C bluepy build3

test:
	@make -C client test

hello:
	@make -C client hello

deb:  build build3
	./build-deb.sh

clean:
	@make -C client clean
	@make -C bluepy clean
	@make -C server clean
	@make -C common clean
	@rm -f aa bb cc pyvserv.deb
	@rm -rf ./build-tmp

cleankeys:
	@rm -rf ./data/keys

md5:













