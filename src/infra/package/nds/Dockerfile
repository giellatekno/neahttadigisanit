FROM python:2.7
ENV PYTHONUNBUFFERED 1

# env setup
# TODO:
# RUN export LANGUAGE=en_US.UTF-8 \
#   && export LANG=en_US.UTF-8 \
#   && locale-gen --no-purge en_US.UTF-8 \
#   && update-locale LANG=en_US.UTF-8 \
#   && export LC_ALL=en_US.UTF-8

RUN apt-get update -y
RUN apt-get install -y subversion nodejs

RUN mkdir /code

ADD dock/ /code/
WORKDIR /code/

RUN virtualenv env
RUN . env/bin/activate && pip install nds-1.0.0.tar.gz
RUN svn co https://gtsvn.uit.no/langtech/trunk/apps/dicts/nds/src/neahtta/configs configs
RUN svn co https://gtsvn.uit.no/langtech/trunk/apps/dicts/nds/src/neahtta/language_specific_rules language_specific_rules
RUN svn co https://gtsvn.uit.no/langtech/trunk/apps/dicts/nds/src/neahtta/dicts dicts

RUN neahtta generate_secret > secret_key.do.not.check.in
RUN npm install uglify-js
RUN neahtta configs/itwewina.config.yaml.in generate_locales
RUN neahtta configs/itwewina.config.yaml.in serve



