# Docker

Docker is a system for providing infrastructure by recipe within virtualized
environments (and depends on Virtualbox). This makes for more dependable and
consistent development and production environments, as these recipes can be
converted into images for deployment.

  https://www.docker.com/

HFST can be difficult to configure on various systems, so there is an HFST
Dockerfile here which makes that easy. It contains some commented lines for
using HFST from svn head.

This is also intended to provide a sort of living documentation of what it
takes to set up a system with these tools.

## What is here

* `hfst/`: version 3.8.2
* TODO: `nds-web/`: base system for all the web packages + HFST: nginx, etc.
* `nds/`: the develoment environment for NDS, based off of the `web` docker.
* `nds/PROJNAME/`: sub-packages for the bare minimum for each project

TODO: nginx

## Installing Docker on Mac

 * docker
 * boot2docker

1.) `boot2docker init` - installs and prepares host VM that contains all the containers
2.) `boot2docker start` - start the VM

### Basic terms

 * image - VM image
 * container - containers are 'cheap', easy to create one from an image, and
   they can be destroyed easily
 * volume - volumes persist even if containers are deleted, volumes can be shared and reused across containers

### Basic commands

 * boot2docker
   * `boot2docker stop` - stop
   * `boot2docker delete` - remove the VM (sometimes it gets big, and you don't need it around)

 * docker ps -a - show running containers
 * docker images - show images
 
### Getting started

## NDS Development

Compiling all of the VMs images can take time, and will take up more space-- so
another option is to install some of the base images and use those to generate
the dev environment.

In this case, what we need is the `nds` image, from which we generate an
environment for a specific project. This image contains all other
prerequisites: `nginx`, and `giella-core` requirements (java, saxon, etc.).
Configuring a project thus, requires just checking out the dictionaries and
`langs` directories.

TODO: export e.g. itwewina to an image and try deploying that on gtweb


## Miscellany

I've attempted to separate some of the parts of development out into separate
docker images/`Dockerfile`s in order to track some of the prerequisites: HFST
can be hard to compile on a new system (or usually has been for me), because
there are a number of dependencies. Keeping this separate from other things
like `Dockerfile` for nginx, and gt infrastructure seems reasonable to do just
in case other projects need to draw on HFST as a base. This also can function
as living documentation for installing these packages: the documentation can be
run and tested in Docker, and someone without knowledge of Docker could read
through it and build the systems outside of Docker, on their own machine.

