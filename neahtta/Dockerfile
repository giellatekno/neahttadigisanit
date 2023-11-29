FROM debian:12.4

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    curl git \
    python3 python3-pip python3-venv \
    nodejs npm

RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash && apt-get update
RUN apt-get install -y --no-install-recommends hfst

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN mkdir /nds
WORKDIR /nds
COPY pyproject.toml /nds/pyproject.toml

# this just installs dependencies (source code of app hasn't been copied in yet)
RUN pip3 install ".[pyhfst,server]"

# this copies in configurations, as well as compiled dicts
COPY neahtta /nds/neahtta

# now install the source code itself (already installed dependencies (above) are skipped)
RUN pip3 install ".[pyhfst,server]"

EXPOSE 5000

CMD [ "gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--name", "nds-test", "neahtta.neahtta:app" ]
