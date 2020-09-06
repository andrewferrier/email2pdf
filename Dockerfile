FROM debian
LABEL maintainer="Andrew Ferrier <andrew.ferrier@example.com>"
RUN apt-get update && apt-get install -y git build-essential \
        fontconfig \
        gdebi-core \
        getmail4 \
        libfontconfig1 \
        libfreetype6 \
        libjpeg62-turbo \
        libx11-6 \
        libxext6 \
        libxrender1 \
        python \
        python3-pip \
        wget \
        xfonts-75dpi \
        xfonts-base
WORKDIR /tmp
RUN wget -O wkhtmltox.deb 'https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb'
RUN dpkg -i *.deb
RUN mkdir /etc/vim && wget -O /etc/vim/vimrc.local https://raw.githubusercontent.com/tpope/vim-sensible/master/plugin/sensible.vim
COPY . /tmp/email2pdf/
COPY docker/email2pdf/getmail /etc/cron.d/
WORKDIR /tmp/email2pdf
RUN pip3 install -r requirements_hacking.txt
RUN make builddeb_real && sh -c 'ls -1 /tmp/email2pdf/*.deb | xargs -L 1 gdebi -n' && cp /tmp/email2pdf/*.deb /tmp
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*
