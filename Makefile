TEMPDIR := $(shell mktemp -t tmp.XXXXXX -d)

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
	docker build -t "email2pdf" .

rundocker_interactive: builddocker
	docker run -i -t email2pdf /sbin/my_init -- bash -l

rundocker_unittest: builddocker
	docker run -i -t email2pdf /sbin/my_init -- bash -c 'cd /tmp/email2pdf && make unittest'

unittest:
	python3 -m unittest discover

unittest_test:
	python3 -m unittest discover -f -v

clean:
	rm -f *.deb
	rm -f *.log
