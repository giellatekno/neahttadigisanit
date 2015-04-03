#
# NDS: dev environment
#
FROM pyry/hfst:latest
MAINTAINER Ryan Johnson <ryan.txanson@gmail.com>
# set the locale
# TODO: permanently?
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  
RUN update-locale LANG=en_US.UTF-8 LC_MESSAGES=POSIX

RUN apt-get install -y git

RUN apt-get install -y python-pip python-dev build-essential python-lxml libxml
RUN apt-get clean

RUN useradd -ms /bin/bash neahtta

ENV HOME /home/neahtta
USER neahtta

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

# set up gtsvn stuff
ENV PATH ~/.local/bin:$PATH
RUN pip install virtualenv

RUN mkdir ~/gtsvn/
RUN svn co https://victorio.uit.no/langtech/trunk/gtcore ~/gtsvn/gtcore
RUN cd ~/gtsvn/gtcore/ && ./autogen.sh && ./configure --prefix=$HOME && make && make install

# set up NDS environment
RUN mkdir -p ~/gtsvn/apps/dicts/ && cd ~/gtsvn/apps/dicts && svn co https://victorio.uit.no/langtech/trunk/apps/dicts/nds nds

WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/
RUN virtualenv --system-site-packages env
RUN . env/bin/activate
WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/neahtta/
RUN pip install -r requirements.txt



# RUN cd ~/ && svn co https://victorio.uit.no/langtech/trunk/langs ~/gtsvn/langs

RUN mkdir ~/gtsvn/langs
RUN cd ~/ && svn co https://victorio.uit.no/langtech/trunk/langs/sms ~/gtsvn/langs/sms

# Did everything up to here work? 
RUN cd ~/gtsvn/langs/sms && ./autogen.sh && ./configure --with-hfst --enable-twostep-intersect --enable-dicts
RUN cd ~/gtsvn/langs/sms && make
