ROOTDIR :=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TEMPDIR := $(shell mktemp -t tmp.XXXXXX -d)
FLAKE8 := $(shell which flake8)

.PHONY: all builddeb clean test

clean:
	git clean -x -f

determineversion:
	$(eval GITDESCRIBE := $(shell git describe --dirty))
	sed 's/Version: .*/Version: $(GITDESCRIBE)/' debian/DEBIAN/control_template > debian/DEBIAN/control
	$(eval GITDESCRIBE_ABBREV := $(shell git describe --abbrev=0))
	sed 's/X\.Y/$(GITDESCRIBE_ABBREV)/' brew/email2pdf_template.rb > brew/email2pdf.rb
	sed 's/pkgver=X/pkgver=$(GITDESCRIBE_ABBREV)/' PKGBUILD_template > PKGBUILD

builddeb: determineversion builddeb_real

builddeb_real:
	dpkg -s build-essential || sudo apt-get install build-essential
	cp -R debian/DEBIAN/ $(TEMPDIR)
	mkdir -p $(TEMPDIR)/usr/bin
	mkdir -p $(TEMPDIR)/usr/share/doc/email2pdf
	cp email2pdf $(TEMPDIR)/usr/bin
	cp README* $(TEMPDIR)/usr/share/doc/email2pdf
	cp LICENSE* $(TEMPDIR)/usr/share/doc/email2pdf
	cp getmailrc.sample $(TEMPDIR)/usr/share/doc/email2pdf
	fakeroot chmod -R u=rwX,go=rX $(TEMPDIR)
	fakeroot chmod -R u+x $(TEMPDIR)/usr/bin
	fakeroot dpkg-deb --build $(TEMPDIR) .

buildarch: determineversion
	makepkg --skipinteg

unittest:
	python3 -m unittest discover

unittest_verbose:
	python3 -m unittest discover -f -v

install_osx_brew: determineversion
	brew install -f file://$(ROOTDIR)/brew/email2pdf.rb

reinstall_osx_brew: determineversion
	brew reinstall file://$(ROOTDIR)/brew/email2pdf.rb

analysis:
	# Debian version is badly packaged, make sure we are using Python 3.
	-/usr/bin/env python3 $(FLAKE8) --max-line-length=132 email2pdf tests/
	pylint -r n --disable=line-too-long --disable=missing-docstring --disable=locally-disabled email2pdf tests/

coverage:
	rm -rf cover/
	nosetests tests/Direct/*.py --with-coverage --cover-package=email2pdf,tests --cover-erase --cover-html --cover-branches
	open cover/index.html

.email2pdf.profile: email2pdf
	python3 -m cProfile -o .email2pdf.profile `which nosetests` .

profile: .email2pdf.profile
	python3 performance/printstats.py | less

test: unittest analysis coverage
