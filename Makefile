TEMPDIR := $(shell mktemp -d)

builddeb: clean
	cp -R debian/DEBIAN/ $(TEMPDIR)
	mkdir -p $(TEMPDIR)/usr/bin
	mkdir -p $(TEMPDIR)/usr/share/doc/email2pdf
	cp email2pdf $(TEMPDIR)/usr/bin
	cp README* $(TEMPDIR)/usr/share/doc/email2pdf
	cp LICENSE* $(TEMPDIR)/usr/share/doc/email2pdf
	cp getmailrc.sample $(TEMPDIR)/usr/share/doc/email2pdf
	sudo chown -R root:root $(TEMPDIR)
	sudo chmod -R 755 $(TEMPDIR)
	dpkg-deb --build $(TEMPDIR) .

unittest:
	./email2pdf_unittest

clean:
	rm -f *.deb
	rm -f *.log
