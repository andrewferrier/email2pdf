FROM phusion/baseimage:0.9.15
ENV HOME /root
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh
CMD ["/sbin/my_init"]
MAINTAINER Andrew Ferrier <andrew.ferrier@example.com>
RUN apt-get update && apt-get install -y git build-essential \
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
        wget
WORKDIR /tmp
RUN wget http://mirrors.kernel.org/ubuntu/pool/universe/p/pypdf2/python3-pypdf2_1.23+git20141008-1_all.deb && dpkg -i python3-pypdf2*.deb
RUN wget -O wkhtmltox.deb 'http://sourceforge.net/projects/wkhtmltopdf/files/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb/download?use_mirror=garr#' && dpkg -i wkhtmltox*.deb
COPY . /tmp/email2pdf/
COPY docker/email2pdf/getmail /etc/cron.d/
WORKDIR /tmp/email2pdf
RUN make builddeb && sh -c 'ls -1 /tmp/email2pdf/*.deb | xargs -L 1 gdebi -n'
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*
