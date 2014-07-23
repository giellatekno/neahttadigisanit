# NB: cleaned up the build process. some of this will be roundabout, but at
# least it's not Cake. Can clean that up later and reduce the amount of similar
# targets built.

MODULES = ./node_modules/.bin
MOCHA   = $(MODULES)/mocha --colors --reporter spec --compilers coffee:coffee-script/register
COFFEE  = $(MODULES)/coffee --compile --bare --print --map
UGLY    = $(MODULES)/uglifyjs
BOOK    = $(MODULES)/bookmarklet

COFFEES = src/nds.root.coffee \
		  src/dictionary.coffee \
		  src/selection.coffee \
		  src/templates.coffee \
		  src/jquery.neahttadigisanit.coffee

# Things listed here will be concatenated into the vendor .js file 
#
# NB: jquery is purposefully lefto out because we want this to be optional for
# a later phase in the build.

JS_DEPS = src/libs/bootstrap-dropdown.js \
          src/libs/bootstrap-tooltip.js \
          src/libs/bootstrap-popover.js \
          src/libs/bootstrap-modal.js \
          src/libs/DSt.js \
          src/libs/semver.js \
          src/libs/rangy-core.js \
          src/libs/rangy-textrange.js

STYLESHEETS = src/css/bootstrap.custom.css \
			  src/css/jquery.neahttadigisanit.css

tmp/jq.css: $(STYLESHEETS)
	@echo "   COMPILING:   " $(STYLESHEETS)
	@cat $^ > $@

tmp/nds.js: $(COFFEES)
	@echo "   COMPILING:    nds.js"
	@$(COFFEE) $^ > $@

tmp/vendor.deps.js: $(JS_DEPS)
	@echo "   BUILDING:     vendor.deps.js"
	@cat $^ > $@

tmp/nds.with.deps.js: tmp/vendor.deps.js \
					  tmp/nds.js
	@echo "   BUILDING:     nds.with.deps.js"
	@cat $^ > $@

tmp/nds.with.deps.jq.js: dev/jquery.1.7.2.js \
						 tmp/nds.with.deps.js
	@echo "   CAT:         " $@
	@cat $^ > $@

bin/standalone/neahttadigisanit.min.js: tmp/nds.with.deps.js
	@echo "   COPY:        " $@
	@cp $^ $@

bin/standalone/neahttadigisanit.jquery.min.js: tmp/nds.with.deps.jq.js
	@echo "   COMPRESSING: " $^
	@$(UGLY) $^ > $@

bin/standalone/neahttadigisanit.jquery.js: tmp/nds.with.deps.jq.js
	@echo "   COPY:        " $@
	@cp $^ $@

bin/standalone/neahttadigisanit.css: tmp/jq.css
	@echo "   COPY:        " $@
	@mkdir -p bin/standalone
	@cp $^ $@

# We build one with jquery and one without, to give the user the option of how
# they include it on their site.
.PHONY: standalone
standalone: bin/standalone/neahttadigisanit.css \
			bin/standalone/neahttadigisanit.jquery.min.js \
			bin/standalone/neahttadigisanit.jquery.js \
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
				   		tmp/nds.with.deps.jq.js
	@echo "   ... Copying css and js."
	@cp -R src/wordpress tmp/wordpress
	@cp tmp/jq.css tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.css
	@cp tmp/nds.with.deps.jq.js tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.js
	@echo "   ... Zipping"
	@cd tmp/wordpress && zip -r neahttadigisanit.zip neahttadigisanit/*
	@cp tmp/wordpress/neahttadigisanit.zip bin/wordpress-neahttadigisanit.zip

.PHONY: wordpress
wordpress: bin/wordpress-neahttadigisanit.zip
	@echo "   DONE:        " "wordpress"
	@echo " - "

tmp/neahttadigisanit.init.min.js: src/neahttadigisanit.init.js
	@$(UGLY) $^ > $@

bin/bookmarklet/bookmarklet.min.js: tmp/nds.with.deps.jq.js \
						tmp/neahttadigisanit.init.min.js
	@mkdir -p bin/bookmarklet
	@cat $^ > $@

bin/bookmarklet/jquery.neahttadigisanit.css: tmp/jq.css
	@mkdir -p bin/bookmarklet
	@cp $^ $@

bookmarklet: bin/bookmarklet/jquery.neahttadigisanit.css \
			 bin/bookmarklet/bookmarklet.min.js
	@echo "   DONE:        " "bookmarklet"
	@echo " - "

bookmarklet-install: bin/bookmarklet/jquery.neahttadigisanit.css \
					bin/bookmarklet/bookmarklet.min.js
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

