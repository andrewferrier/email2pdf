TEMPDIR := $(shell mktemp -t tmp.XXXXXX -d)

builddeb: stylecheck
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

builddocker: buildpdfminer3k
	docker build -t andrewferrier/email2pdf .

rundocker_interactive: builddocker
	docker run -i -t andrewferrier/email2pdf /sbin/my_init -- bash -l

rundocker_unittest: builddocker
	docker run -i -t andrewferrier/email2pdf /sbin/my_init -- bash -c 'cd /tmp/email2pdf && make unittest'

unittest:
	python3 -m unittest discover

unittest_test:
	python3 -m unittest discover -f -v

stylecheck:
	flake8 --max-line-length=132 .

coverage:
	rm -r cover/
	nosetests tests/test_Direct.py --with-coverage --cover-package=email2pdf --cover-erase --cover-html
	open cover/email2pdf.html

clean:
	rm -f *.deb
	rm -f *.log

buildpdfminer3k:
	docker build -t "andrewferrier/pdfminer3k" docker/pdfminer3kdeb
	docker run -i -v ${PWD}:/pdfminer3k andrewferrier/pdfminer3k sh -c 'cp /tmp/python3-pdfminer3k*.deb /pdfminer3k'
