# email2pdf

Script to convert emails to PDF from the command-line.

## Dependencies

* wkhtmltopdf - if on Ubuntu, install the .deb from http://wkhtmltopdf.org/
  rather than using apt-get to minimise the dependencies you need to install
  (in particular, to avoid needing a package manager).

* getmail - getmail is not strictly a dependency, but when it is combined with
  email2pdf, it can be used to retrieve new emails from a remote IMAP server
  and automatically convert them to PDFs locally. The attached
  getmailrc.sample file can be used as a starting point for your own
  getmailrc to do this. Note that the sample will need editing, of course -
  see the getmail documentation for more information on that. Also, it is
  configured by default to *delete* remote emails from the server once they
  are converted - be careful with that.
