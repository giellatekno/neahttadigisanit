.PHONY: clean-docker
clean-docker:
	docker rm $$(docker ps -a -q)
	docker ps -a -q | xargs docker stop
	docker rm $$(docker ps -a -q)
	docker images | grep '^<none'
	docker images | grep '^<none' | awk {'print $$3'} | xargs docker rmi

.PHONY: hfst
hfst:
	cd hfst/ && docker build -t gt-nds/hfst .

.PHONY: nds-web
nds-web:
	cd nds-web/ && docker build -t gt-nds/web . 

.PHONY: nds
nds:
	cd nds/ && docker build -t gt-nds/nds .

.PHONY: nds-itwewina
nds-itwewina:
	cd nds/itwewina/ && docker build -t gt-nds/nds-itwewina .

# 
compact:
	docker export $(CONTAINER_ID) > hfst.tar
	cat hfst.tar | docker import - gt-nds/hfst:latest

all: hfst \
	 nds-web \
	 nds \
	 nds-itwewina

