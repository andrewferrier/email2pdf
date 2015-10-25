# email2pdf - Hacking

This document talks about hacking/developing on email2pdf - for more
information on email2pdf and how to use it, please see
[README.md](https://github.com/andrewferrier/email2pdf/blob/master/README.md).

In general, [bug reports/enhancement
requests](https://github.com/andrewferrier/email2pdf/issues) as well as [pull
requests](https://github.com/andrewferrier/email2pdf/pulls) are welcome;
please note the [license
conditions](https://github.com/andrewferrier/email2pdf/blob/master/LICENSE.txt).
If you are trying to report an issue, please try running email2pdf with the
`-vv` option to maximise the debugging output first.

## Building & Packaging

All the supplied build and packaging is based on a
[Makefile](https://github.com/andrewferrier/email2pdf/blob/master/Makefile).
You'll need `make` if you don't have it (`sudo apt-get install make` on
Ubuntu/Debian, `brew install make` on OS X).

## Design & Coding Principles

* Follow [PEP-8](https://www.python.org/dev/peps/pep-0008/). Running `make
  analysis` will check against this and run other static code analysis checks
  also.

* Try to keep `email2pdf` as "safe" as possible by default. Without supplying
  any potentially harmful command-line options, `email2pdf` will not ignore
  parts of the email it shouldn't, and will fail in the standard UNIX way with
  an error code if it has any significant doubts about the integrity of the
  email it's reading, or any other serious error occurs.

## Unit Tests

All the unit tests are in the `tests/` directory. You can run them from the
Makefile using the `unittest` or `unittest_test` targets (the second is more
verbose, and stops on failing tests).

All new code should be covered by a test. There is a code coverage checker
target in the Makefile - run `make coverage`. You'll need to have the
`coverage` and `nose` Python modules installed (`pip3 install coverage nose`)
to run them.

In addition to the standard dependencies from the [standard install
documentation](https://github.com/andrewferrier/email2pdf/blob/master/README.md),
there are some additional dependencies which will be needed to make the tests
work:

### OS X

Just run `pip3 install flake8 freezegun nosetests pdfminer3k reportlab`.

### Debian/Ubuntu

* `python3-freezegun` - only available in Ubuntu 14.10 onwards - see
  http://packages.ubuntu.com/search?keywords=python3-freezegun. If you are on
  an earlier version, you can download the `.deb` manually and install with
  `dpkg -i`.

* `python3-reportlab` - install with `apt-get install python3-reportlab`.

* `python3-pdfminer3k` (not a standard Debian/Ubuntu package, but there is a
  supplied Makefile target which will create it for you using a Docker
  container - run `make rundocker_getdebs`, then `dpkg -i` the package when
  you are done).

## Docker

There is some experimental packaging for [Docker](https://www.docker.com/)
also. Of course, you need to have Docker installed for this to work, which is
outside the scope of this document. You can run the following `make` targets:

* `rundocker_interactive` - build and start a Docker image, at the `bash`
  prompt. Can be used to interactively test email2pdf.

* `rundocker_testing` - build and start the Docker image, run the entire unit
  testing and style testing suites, and exit.

* `rundocker_getdebs` - build and start the Docker image, and copy out various
  `.debs`, including the `.deb` for email2pdf itself, and various dependencies
  that are harder to come by or need to be built manually.
