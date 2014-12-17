TEMPDIR := $(shell mktemp -d)

builddeb:
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

unittest:
	python3 -m unittest discover

clean:
	rm -f *.deb
	rm -f *.log
