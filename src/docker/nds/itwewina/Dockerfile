#
# NDS: dev environment for itwewina
#

# TODO: major problem here is that all work performed on nds volume cannot be
# overwritten here: each step for some reason is reverted.

FROM gt-nds/nds:latest

VOLUME /home/neahtta
VOLUME /opt/smi

MAINTAINER Ryan Johnson <ryan.txanson@gmail.com>

ENV HOME /home/neahtta

USER root

# TODO: copy nds init.d service files


USER neahtta
WORKDIR /home/neahtta/

WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/
### RUN svn up
### 
### RUN . /home/neahtta/gtsvn/apps/dicts/nds/src/env/bin/activate && \
###     pip install -r neahtta/requirements.txt

# TODO: determine bare essentials to get NDS running, then remove language
# infra so this can be its own Dockerfile.

# Expose this to child containers

WORKDIR /home/neahtta/
RUN mkdir -p ~/gtsvn/langs
RUN mkdir -p ~/gtsvn/art/
RUN mkdir -p ~/gtsvn/words/dicts/

WORKDIR /home/neahtta/gtsvn/words/dicts/
RUN svn co https://victorio.uit.no/langtech/trunk/words/dicts/scripts /home/neahtta/gtsvn/words/dicts/scripts
### TODO: RUN svn co https://victorio.uit.no/langtech/trunk/words/dicts/crkeng /home/neahtta/gtsvn/words/dicts/crkeng

### TODO: WORKDIR /home/neahtta/gtsvn/langs/
### TODO: RUN svn co https://victorio.uit.no/langtech/trunk/langs/crk /home/neahtta/gtsvn/langs/crk
# TODO: find a way to install the credentials

### TODO: WORKDIR /home/neahtta/gtsvn/art/
### TODO: # SVN pass comes from environment file that's copied over
### TODO: RUN . ~/.profile && svn co https://victorio.uit.no/langtech/trunk/art/dicts dicts --username neahtta --password $SVN_PASS --non-interactive

# TODO: move to nds

### TODO: WORKDIR /home/neahtta/gtsvn/apps/dicts/nds/src/neahtta/
### TODO: 
### TODO: ENV GTHOME /home/neahtta/gtsvn/
### TODO: ENV GTCORE /home/neahtta/gtsvn/giella-core/

# environment variables aren't available when fab issues make
# RUN . ~/.profile && . ../env/bin/activate && fab no_svn_up itwewina compile

WORKDIR /home/neahtta/
RUN ls -lah ~/gtsvn/words/dicts/

