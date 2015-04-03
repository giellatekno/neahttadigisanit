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
* `nds/`: the develoment environment for NDS, based off of the HFST docker.

TODO: nginx

## Installing Docker on Mac

### Basic terms

 * image - VM image
 * container - containers are 'cheap', easy to create one from an image, and
   they can be destroyed easily

### Basic commands

 * boot2docker

 * docker ps -a - show running containers
 * docker images - show images
 

### Getting started

## NDS Development


