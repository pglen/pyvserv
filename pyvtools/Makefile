#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

.PHONY: docs

all:
	@echo "Type 'make help' for a list of targets"

help:
	@echo
	@echo "Targets:"
	@echo "	 make install    -- Install project "
	@echo "	 make pack       -- package project "
	@echo "	 make git        -- checkin project "
	@echo

install:
	@./install.py

pack:
	@./pack.sh

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push

XPATH=PYTHONPATH=pyvcommon:../pyvguicom/pyvguicom: pdoc --force --html
docs:
	@${XPATH} -o docs pyvgenkey.py
	@${XPATH} -o docs pyvgenkeys.py

clean:
	@rm -f aa bb cc pyvserv.deb
	@rm -rf build-tmp/*
	@rm -rf  dist/*
	@rm -rf  build/*

# End of Makefile
