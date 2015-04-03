
hfst:
	cd hfst/ && docker build -t pyry/hfst .
# TODO:	
# cd hfst/ && docker export pyry/hfst > hfst.tar

# 
compact:
	docker export $(CONTAINER_ID) > hfst.tar
	cat hfst.tar | docker import - pyry/hfst:latest

nds:
	cd nds/ && docker build -t pyry/nds .

all: hfst \
	 nds

