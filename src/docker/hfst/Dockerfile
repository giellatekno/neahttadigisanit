#
# HFST
#
FROM ubuntu:14.10
MAINTAINER Ryan Johnson <ryan.txanson@gmail.com>
# set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

RUN apt-get update
RUN apt-get install -y subversion build-essential wget
RUN apt-get install -y autoconf automake libtool flex bison g++ libreadline-dev libglib2.0-dev

# TODO: glibtoolize?

## automake 1.14 -- required for gtcore and langs builds
## RUN cd ~/ && wget http://ftp.gnu.org/gnu/automake/automake-1.14.tar.gz
## RUN cd ~/ && tar -zxvf automake-1.14.tar.gz
## RUN cd ~/automake-1.14/ && ./configure && make && make install

### # build HFST from head
### RUN cd ~/ && svn co http://svn.code.sf.net/p/hfst/code/trunk/hfst3
### RUN cd ~/hfst3/ && ./autogen.sh && \
###     ./configure --without-foma --enable-all-tools --with-unicode-handler=glib --with-lexc
### RUN cd ~/hfst3/ && . scripts/generate-cc-files.sh
### RUN cd ~/hfst3/ && make
### RUN cd ~/hfst3/ && make install

RUN cd ~/ && wget -O hfst-3.8.2.tar.gz "http://downloads.sourceforge.net/project/hfst/hfst/source/hfst-3.8.2.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fhfst%2Ffiles%2Fhfst%2Fsource%2F&ts=1425162646&use_mirror=tcpdiag" && \
    tar zxvf hfst-3.8.2.tar.gz && \
    cd hfst-3.8.2
RUN cd ~/hfst-3.8.2/ && ./configure --without-foma --enable-all-tools --with-unicode-handler=glib 
RUN cd ~/hfst-3.8.2/ && make 
RUN cd ~/hfst-3.8.2/ && make install
RUN cd ~/hfst-3.8.2/ && make distclean

RUN ldconfig

RUN apt-get clean

# TODO: rm temp build files?

# TODO: ? need to create some bash function / alias that will run commands via the image
#   function hfstdocker $1 {
#       eval "docker run -it --rm IMGNAME $1"
#   } 
