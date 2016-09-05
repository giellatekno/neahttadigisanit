#
# HFST and sample gtsvn lang build
#
FROM ubuntu:12.04
MAINTAINER Ryan Johnson <ryan.txanson@gmail.com>
# set the locale
# TODO: permanently?
#    update-locale LANG=en_US.UTF-8 LC_MESSAGES=POSIX
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

# everything breaks otherwise
RUN apt-get update
# general dev stuff
RUN apt-get install -y subversion build-essential wget
# hfst specific
RUN apt-get install -y automake autoconf libtool flex bison g++ libreadline-dev libglib2.0-dev

# build HFST from head
# RUN svn co http://svn.code.sf.net/p/hfst/code/trunk/hfst3 && \
#    cd hfst3/ && \
#    ./autogen.sh && \
#    ./configure --without-foma --enable-all-tools --with-unicode-handler=glib --with-lexc && \
#    make && \
#    make install

## NB: best to separate these actions out into things that might fail, so you
## can go back and attach to each section to fix it

RUN cd ~/ && wget -O hfst-3.8.2.tar.gz "http://downloads.sourceforge.net/project/hfst/hfst/source/hfst-3.8.2.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fhfst%2Ffiles%2Fhfst%2Fsource%2F&ts=1425162646&use_mirror=tcpdiag" && \
    tar zxvf hfst-3.8.2.tar.gz && \
    cd hfst-3.8.2
RUN cd ~/hfst-3.8.2/ && ./configure --without-foma --enable-all-tools --with-unicode-handler=glib --with-lexc 
RUN cd ~/hfst-3.8.2/ && make 
RUN cd ~/hfst-3.8.2/ && make install

RUN ldconfig

##   # set up gtsvn stuff
##   
##   ## automake 1.14 -- required for giella-core and langs builds
##   RUN cd ~/ && wget http://ftp.gnu.org/gnu/automake/automake-1.14.tar.gz
##   RUN cd ~/ && tar -zxvf automake-1.14.tar.gz
##   RUN cd ~/automake-1.14/ && ./configure && make && make install
##   
##   RUN mkdir ~/gtsvn/
##   RUN cd ~/ && svn co https://victorio.uit.no/langtech/trunk/giella-core ~/gtsvn/giella-core
##   RUN cd ~/gtsvn/giella-core/ && ./autogen.sh && ./configure && make && make install
##   
##   RUN cd ~/ && svn co https://victorio.uit.no/langtech/trunk/langs ~/gtsvn/langs
##   
##   # Did everything up to here work? 
##   RUN cd ~/gtsvn/langs/sms && ./autogen.sh && ./configure --with-hfst --enable-twostep-intersect --enable-dicts
##   RUN cd ~/gtsvn/langs/sms && make

# RUN cd ~/ && svn co https://victorio.uit.no/langtech/trunk/words ~/gtsvn/words

# WORKDIR 

# TODO: need to create some bash function / alias that will run commands via the image
#   function hfstdocker $1 {
#       eval "docker run -it --rm IMGNAME $1"
#   } 

