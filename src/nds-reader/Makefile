# NB: cleaned up the build process. some of this will be roundabout, but at
# least it's not Cake. Can clean that up later and reduce the amount of similar
# targets built.

MODULES = ./node_modules/.bin

# Testing framework
MOCHA   = $(MODULES)/mocha --colors --reporter spec --compilers coffee:coffee-script/register

# Javascript compliation stuff
COFFEE  = $(MODULES)/coffee --compile --bare --print --map
UGLY    = $(MODULES)/uglifyjs
BOOK    = $(MODULES)/bookmarklet

bin/app.js bin/app.css:
	brunch build

bin/app.min.js: bin/app.js
	@$(UGLY) $^ > $@

tmp/jq.css: bin/app.css
	@echo "   COMPILING:   tmp/jq.css" 
	@cat $^ > $@

tmp/nds.js: $(COFFEES)
	@echo "   COMPILING:    nds.js"
	@$(COFFEE) $^ > $@

tmp/nds.with.deps.js: src/wrapper_start.js \
					  bin/app.js \
					  src/wrapper_end.js
	@echo "   BUILDING:     nds.with.deps.js"
	@cat $^ > $@

tmp/nds.with.deps.min.js: src/wrapper_start.js \
						  bin/app.min.js \
						  src/wrapper_end.js
	@echo "   BUILDING:     nds.with.deps.min.js"
	@cat $^ > $@

tmp/nds.with.deps.jq.js: lib/jquery-1.11.1.js \
						 tmp/nds.with.deps.js
	@echo "   CAT:         " $@
	@cat $^ > $@

tmp/jquery-1.11.1.min.js: lib/jquery-1.11.1.js
	@$(UGLY) $^ > $@

tmp/nds.with.deps.min.jq.js: tmp/jquery-1.11.1.min.js \
						 tmp/nds.with.deps.min.js
	@echo "   CAT:         " $@
	@cat $^ > $@

bin/standalone/neahttadigisanit.js: tmp/nds.with.deps.js
	@echo "   COPY:        " $@
	@cp $^ $@

bin/standalone/neahttadigisanit.min.js: tmp/nds.with.deps.min.js
	@echo "   COPY:        " $@
	@cp $^ $@

bin/standalone/neahttadigisanit.jquery.min.js: tmp/nds.with.deps.min.jq.js
	@echo "   COPY:        " $^
	@cp $^ $@

bin/standalone/neahttadigisanit.jquery.js: tmp/nds.with.deps.min.jq.js
	@echo "   COPY:        " $@
	@cp $^ $@

bin/standalone/neahttadigisanit.css: tmp/jq.css
	@echo "   COPY:        " $@
	@mkdir -p bin/standalone
	@cp $^ $@

# We build one with jquery and one without, to give the user the option of how
# they include it on their site.
.PHONY: standalone
standalone: bin/bookmarklet/jquery.neahttadigisanit.css \
			bin/standalone/neahttadigisanit.css \
			bin/standalone/neahttadigisanit.jquery.min.js \
			bin/standalone/neahttadigisanit.jquery.js \
			bin/standalone/neahttadigisanit.js \
			bin/standalone/neahttadigisanit.min.js
	@echo "   DONE:        " "STANDALONE"
	@echo " - "

standalone-install: bin/standalone/neahttadigisanit.css \
					bin/standalone/neahttadigisanit.jquery.min.js \
					bin/standalone/neahttadigisanit.min.js
	@echo "   INSTALL:     " "standalone"
	@cp bin/standalone/*.js ../neahtta/static/js/
	@cp bin/standalone/*.css ../neahtta/static/css/
	@echo "   DONE:        " "standalone"
	@echo " - "

bin/wordpress-neahttadigisanit.zip: src/wordpress \
				   		tmp/jq.css \
				   		tmp/nds.with.deps.min.jq.js
	@echo "   ... Copying css and js."
	@cp -R src/wordpress tmp/wordpress
	@cp tmp/jq.css tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.css
	@cp tmp/nds.with.deps.min.jq.js tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.js
	@echo "   ... Zipping"
	@cd tmp/wordpress && zip -r neahttadigisanit.zip neahttadigisanit/*
	@cp tmp/wordpress/neahttadigisanit.zip bin/wordpress-neahttadigisanit.zip

.PHONY: wordpress
wordpress: bin/wordpress-neahttadigisanit.zip
	@echo "   DONE:        " "wordpress"
	@echo " - "

tmp/neahttadigisanit.init.js: src/neahttadigisanit.init.js
	@cp $^ $@

tmp/neahttadigisanit.init.min.js: src/neahttadigisanit.init.js
	@$(UGLY) $^ > $@

bin/bookmarklet/bookmarklet.js: tmp/nds.with.deps.jq.js \
									tmp/neahttadigisanit.init.js
	@mkdir -p bin/bookmarklet
	@cat $^ > $@

bin/bookmarklet/bookmarklet.min.js: tmp/nds.with.deps.min.jq.js \
									tmp/neahttadigisanit.init.min.js
	@mkdir -p bin/bookmarklet
	@cat $^ > $@

bin/bookmarklet/jquery.neahttadigisanit.css: tmp/jq.css
	@mkdir -p bin/bookmarklet
	@cp $^ $@

bookmarklet: bin/bookmarklet/jquery.neahttadigisanit.css \
			 bin/bookmarklet/bookmarklet.js \
			 bin/bookmarklet/bookmarklet.min.js
	@echo "   DONE:        " "bookmarklet"
	@echo " - "

bookmarklet-install: bin/bookmarklet/jquery.neahttadigisanit.css \
					bin/bookmarklet/bookmarklet.min.js \
					bin/bookmarklet/bookmarklet.js
	@cp bin/bookmarklet/*.js ../neahtta/static/js/
	@cp bin/bookmarklet/*.css ../neahtta/static/css/
	@echo "    ... Installed"

# TODO: actual bookmark code, need to urlencode that and copy somewhere.
# NOTE: before or if this happens, check out the notes in neahtta/ on the
# bookmarklet, there are some specific needs not addressed here.
#
# bin/bookmarklet/bookmark.js: src/bookmark.js
# 	$(BOOK) $^ > $@
#
# need to first test output from bookmarklet.

test:
	@echo "Open the browser test page when this completes."
	$(MODULES)/coffee --compile --bare tests/

test-watch:
	$(MOCHA) -w tests/*.coffee src/*.coffee

.PHONY: install
install: standalone-install \
		 bookmarklet-install

.PHONY: all
all: standalone \
	 bookmarklet \
	 wordpress

.PHONY: clean
clean: 
	rm -rf tmp/* bin/*

