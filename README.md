# email2pdf

Python script to convert emails to PDF from the command-line. Type `email2pdf
--help` for more information on usage and options available.

## Dependencies

* [wkhtmltopdf](http://wkhtmltopdf.org/) - if on Ubuntu, install the `.deb` from
  http://wkhtmltopdf.org/ rather than using apt-get to minimise the
  dependencies you need to install (in particular, to avoid needing a package
  manager).

* [getmail](http://pyropus.ca/software/getmail/) - getmail is not strictly a
  dependency, but when it is combined with email2pdf, it can be used to
  retrieve new emails from a remote IMAP server and automatically convert them
  to PDFs locally. The
  [`getmailrc.sample`](https://github.com/andrewferrier/email2pdf/blob/master/getmailrc.sample)
  file in the repository can be used as a starting point for your own
  getmailrc to do this. Note that the sample will need editing, of course -
  see the getmail documentation for more information on that. Also, it is
  configured by default to *delete* remote emails from the server once they
  are converted - be careful with that. You might want to consider setting up
  your crontab something like this:

      @hourly getmail --verbose | logger

  This will ensure that getmail is invoked hourly to fetch email, and log its
  output to syslog.

## Building & Packaging for Debian

Some basic Debian packaging is included. Simply run `sudo apt-get install
build-essential && make builddeb` to build a Debian package.

## Developing & Hacking

### Debian

* Install all the package dependencies listed in the
  [`control`](https://github.com/andrewferrier/email2pdf/blob/master/debian/DEBIAN/control)
  file.

### OSX

* Install [Homebrew](http://brew.sh/)
* `brew install python3`
* `brew install libmagic`
* `pip3 install reportlab python-magic pypdf2`
