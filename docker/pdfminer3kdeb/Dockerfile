FROM debian:sid
ENV HOME /root
MAINTAINER Andrew Ferrier <andrew.ferrier@example.com>
RUN apt-get update && apt-get install -y \
        python3-pip \
        checkinstall
WORKDIR /tmp
RUN fakeroot checkinstall --pkgname=python3-pdfminer3k --pkgversion=0.1 -y --fstrans=no --install=no pip3 install pdfminer3k
