# email2pdf

email2pdf is a Python script to convert emails to PDF from the command-line.
email2pdf acts in place of a [mail delivery
agent](http://en.wikipedia.org/wiki/Mail_delivery_agent) - it won't retrieve
emails for you, but it will take them from standard input as an MDA will and
'deliver' them to PDF files. Type `email2pdf --help` for more information on
usage and options available.

## Dependencies

* [wkhtmltopdf](http://wkhtmltopdf.org/) - if on Ubuntu, install the `.deb`
  from http://wkhtmltopdf.org/ rather than using apt-get to minimise the
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

* Others - there are some other Python library dependencies. The Debian
  packaging (see below) will set the dependencies on the package
  appropriately. For OS X, please install dependencies as shown in the
  'Developing & Hacking' section below.

## Building & Packaging

All the supplied build and packaging is based on a
[Makefile](https://github.com/andrewferrier/email2pdf/blob/master/Makefile).
You'll need `make` if you don't have it (`sudo apt-get install make` on
Ubuntu/Debian, `brew install make` on OS X).

### Debian

Some basic Debian packaging is included. Simply run `make builddeb` to build a
Debian package.

### Docker

There is some experimental packaging for [Docker](https://www.docker.com/)
also. You can run the following `make` targets:

* `builddocker` - build a Docker image.

* `rundocker_interactive` - build and start a Docker image, at the `bash`
  prompt.

* `rundocker_unittest` - build and start the Docker image, run the entire unit
  test suite, and exit.

## Developing & Hacking

### Unit Tests

All the unit tests are in the `tests/` directory. You can run them from the
Makefile using the `unittest` or `unittest_test` targets (the second is more
verbose, and stops on failing tests).

### Debian

* Install all the package dependencies listed in the
  [`control`](https://github.com/andrewferrier/email2pdf/blob/master/debian/DEBIAN/control)
  file.

### OSX

* Install [Homebrew](http://brew.sh/)
* `brew install python3`
* `brew install libmagic`
* `pip3 install reportlab python-magic pypdf2 beautifulsoup4`
