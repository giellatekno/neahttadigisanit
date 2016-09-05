#
# NDS: dev environment
#
FROM gt-nds/web:latest
MAINTAINER Ryan Johnson <ryan.txanson@gmail.com>

# set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  
RUN update-locale LANG=en_US.UTF-8 LC_MESSAGES=POSIX

RUN apt-get update
RUN apt-get install -y python-pip python-dev build-essential python-lxml libxml2-dev libxslt1-dev python-dev unzip git
# This causes X to be installed.
RUN apt-get install -y openjdk-7-jre-headless 
# default-jre
RUN apt-get clean

RUN useradd -ms /bin/bash neahtta

RUN mkdir /opt/smi/
RUN chmod -R g+rwx /opt/smi/
RUN chown -R neahtta:neahtta /opt/smi/

ENV HOME /home/neahtta
USER neahtta
WORKDIR /home/neahtta

RUN mkdir ~/.ssh/
RUN touch ~/.ssh/config

ADD environment /home/neahtta/environment
ADD neahtta_bashrc /home/neahtta/neahtta_bashrc
RUN touch .profile
RUN cat /home/neahtta/neahtta_bashrc >> .profile
RUN cat /home/neahtta/environment >> /home/neahtta/.profile

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

# set up gtsvn stuff

RUN mkdir ~/gtsvn/
RUN svn co https://victorio.uit.no/langtech/trunk/giella-core ~/gtsvn/giella-core
RUN cd ~/gtsvn/giella-core/ && ./autogen.sh && ./configure --prefix=$HOME && make && make install

RUN mkdir ~/saxon
RUN mkdir ~/lib
RUN wget "http://downloads.sourceforge.net/project/saxon/Saxon-HE/9.6/SaxonHE9-6-0-5J.zip?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fsaxon%2Ffiles%2FSaxon-HE%2F9.6%2F&ts=1428268045&use_mirror=softlayer-dal" -O ~/saxon/saxon9.zip
RUN cd ~/saxon/ && unzip saxon9.zip
RUN cd ~/lib/ && mv ../saxon/saxon9he.jar saxon9.jar
RUN cd ~/ && rm -rf ~/saxon/

# set up NDS environment
RUN mkdir -p ~/gtsvn/apps/dicts/ && cd ~/gtsvn/apps/dicts && svn co https://victorio.uit.no/langtech/trunk/apps/dicts/nds nds

WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/

# NB: gonna try without virtualenv
RUN pip install virtualenv --user
RUN pip install pip --upgrade --user
ENV PATH /home/neahtta/.local/bin:$PATH
RUN virtualenv --system-site-packages env
RUN . /home/neahtta/gtsvn/apps/dicts/nds/src/env/bin/activate && \
    pip install pip --upgrade
RUN . /home/neahtta/gtsvn/apps/dicts/nds/src/env/bin/activate && \
    pip install setuptools --upgrade
RUN . /home/neahtta/gtsvn/apps/dicts/nds/src/env/bin/activate && \
    pip install -r neahtta/requirements.txt

RUN npm install

WORKDIR /home/neahtta/
RUN mkdir -p ~/gtsvn/langs/
RUN mkdir -p ~/gtsvn/art/
RUN mkdir -p ~/gtsvn/words/dicts/

WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/neahtta/

# TODO: does this work? VOLUME ["/home/neahtta", "/opt/smi"]
