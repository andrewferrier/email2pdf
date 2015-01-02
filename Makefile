TEMPDIR := $(shell mktemp -t tmp.XXXXXX -d)
FLAKE8 := $(shell which flake8)

builddeb:
	sudo apt-get install build-essential
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

builddocker:
	docker build -t andrewferrier/email2pdf .

rundocker_interactive: builddocker
	docker run -i -t andrewferrier/email2pdf /sbin/my_init -- bash -l

rundocker_testing: builddocker
	docker run -t andrewferrier/email2pdf /sbin/my_init -- bash -c 'cd /tmp/email2pdf && make unittest && make stylecheck'

rundocker_getdebs: builddocker
	docker run -v ${PWD}:/debs andrewferrier/email2pdf sh -c 'cp /tmp/*.deb /debs'

unittest:
	python3 -m unittest discover

unittest_test:
	python3 -m unittest discover -f -v

stylecheck:
	# Debian version is badly packaged, make sure we are using Python 3.
	/usr/bin/env python3 $(FLAKE8) --max-line-length=132 .

coverage:
	rm -rf cover/
	nosetests tests/test_Direct*.py --with-coverage --cover-package=email2pdf --cover-erase --cover-html
	open cover/email2pdf.html

alltests: unittest stylecheck coverage
