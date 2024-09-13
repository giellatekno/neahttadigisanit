FROM debian:12.4

# This creates an image with the code, and hfst-toolchain
# This means that any update to the code, will have to create a new image,
# and get that restarted - for all instances

# As of right now, dictionaries are also compiled into the image
# I may want to have those outside, to ease the dictionary update process

# If dictionaries are outside, and mapped in, the nds script still needs
# to work outside

# flow to update dictionaries:
#   ssh <server>    (I have an alias gtdict=ssh <server>)
#   sudo su neahtta   (switch to user, venv will be activated)
#   cd neahttadigisanit  (move to project folder, this is the git repo)
#   nds update <project>    (pull new dict sources from github)
#   nds compile <project>   (compile dictionaries for project)
# ....
#   here we would do  nds restart <project>
#   and maybe we still can - it will restart the systemd service, which
#   just happens to run a podman image, instead of the raw command

# flow to update code:
#   ssh <server>
#   sudo su neahtta
#   cd neahttadigisanit
#   git pull
#  ...
#   here I would normally just restart, but before that, a new image needs to
#   be built
#   nds rebuild-image
#   nds restart <project>   (or "nds restart all" probably, because of code change)

# IDEALLY
#   Complete automation when updating dictionaries
#      git hook on github, that compiles dictionaries, and somehow gets them
#      copied to the server, and then somehow restarts the services affected
#      This could be a bit too many restarts, though.
#      - dictionaries should be served by the dictionaries websearch app
#      - it would be running on the same datacenter, so the api call wouldn't
#        be that slow -- hopefully.
#   Complete automation when updating code
#      git hook on github
#         that creates a new image, upload it to a container
#      registry on azure (acr)
#
#   How to achieve? How close can I get?

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    curl git \
    python3 python3-pip python3-venv \
    nodejs npm

RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash && apt-get update
RUN apt-get install -y --no-install-recommends hfst

# TEMP fkv
RUN apt-get -y install giella-fkv giella-fit giella-nob

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

ENV NDS_CONFIG=/nds/neahtta/configs/sanat.config.yaml

CMD [ "gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--name", "nds-test", "neahtta.neahtta:app" ]
