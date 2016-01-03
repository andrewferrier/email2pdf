FROM ubuntu:14.04
MAINTAINER Andrew Ferrier <andrew.ferrier@example.com>
RUN apt-get update && apt-get install -y git build-essential \
        checkinstall \
        fontconfig \
        gdebi-core \
        getmail4 \
        libfontconfig1 \
        libfreetype6 \
        libjpeg-turbo8 \
        libx11-6 \
        libxext6 \
        libxrender1 \
        python \
        python3-dateutil \
        python3-flake8 \
        python3-pip \
        python3-reportlab \
        wget \
        xfonts-75dpi \
        xfonts-base
WORKDIR /tmp
RUN wget http://mirrors.kernel.org/ubuntu/pool/universe/p/pypdf2/python3-pypdf2_1.23+git20141008-1_all.deb
RUN wget http://mirrors.kernel.org/ubuntu/pool/universe/f/freezegun/python3-freezegun_0.1.18-1_all.deb
RUN fakeroot checkinstall --pkgname=python3-pdfminer3k --pkgversion=0.1 -y --fstrans=no --install=no pip3 install pdfminer3k
RUN wget -O wkhtmltox.deb 'http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb'
RUN dpkg -i *.deb
RUN wget -O /etc/vim/vimrc.local https://raw.githubusercontent.com/tpope/vim-sensible/master/plugin/sensible.vim
COPY . /tmp/email2pdf/
COPY docker/email2pdf/getmail /etc/cron.d/
WORKDIR /tmp/email2pdf
RUN make builddeb_real && sh -c 'ls -1 /tmp/email2pdf/*.deb | xargs -L 1 gdebi -n' && cp /tmp/email2pdf/*.deb /tmp
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*
