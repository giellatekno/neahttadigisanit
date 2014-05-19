# NB: cleaning up the build process. some of this will be roundabout, but at
# least it's not Cake. Can clean that up later and reduce the amount of similar
# targets built.

MODULES = ./node_modules/.bin
COFFEE  = $(MODULES)/coffee --compile --bare --print
UGLY    = $(MODULES)/uglifyjs

# TODO: compare result of UGLY to result of Cakefile process to make sure that
# nothing is amiss
#   - parse
#   - ast_mangle
#   - ast_squeeze
#   gen_code

# compress = (callback) ->
#   util.print "\n Compressing... bin/jquery.neahttadigisanit.js\n"
#   all = (fs.readFileSync 'bin/jquery.neahttadigisanit.js').toString()
# 
#   ast = uglify.parser.parse all
#   out = fs.openSync "bin/jquery.neahttadigisanit.min.js", "w+"
# 
#   ast = uglify.uglify.ast_mangle ast
#   ast = uglify.uglify.ast_squeeze ast
# 
#   fs.writeSync out, uglify.uglify.gen_code(ast)
# 
#   util.print "\n Minified! to jquery.neahttadigisanit.min.js\n"

COFFEES = src/jquery.neahttadigisanit.coffee

JS_DEPS = src/libs/bootstrap-dropdown.js \
          src/libs/bootstrap-tooltip.js \
          src/libs/bootstrap-popover.js \
          src/libs/bootstrap-modal.js \
          src/libs/DSt.js \
          src/libs/semver.js \
          src/libs/rangy-core.js

STYLESHEETS = src/css/bootstrap.custom.css \
			  src/css/jquery.neahttadigisanit.css

tmp/jq.css: $(STYLESHEETS)
	cat $^ > $@

tmp/nds.js: $(COFFEES)
	$(COFFEE) $^ > $@

tmp/vendor.deps.js: $(JS_DEPS)
	cat $^ > $@

tmp/nds.with.deps.js: tmp/vendor.deps.js \
					  tmp/nds.js
	cat $^ > $@

tmp/nds.with.deps.jq.js: dev/jquery.1.7.2.js \
						 tmp/nds.with.deps.js
	cat $^ > $@

bin/standalone/neahttadigisanit.min.js: tmp/nds.with.deps.js
	@echo "   ... copying"
	cp $^ $@

bin/standalone/neahttadigisanit.jquery.min.js: tmp/nds.with.deps.jq.js
	@echo "   ... uglifying"
	$(UGLY) $^ > $@

bin/standalone/neahttadigisanit.css: tmp/jq.css
	@echo "   ... copying"
	mkdir -p bin/standalone
	cp $^ $@

# We build one with jquery and one without, to give the user the option of how
# they include it on their site.
.PHONY: standalone
standalone: bin/standalone/neahttadigisanit.css \
			bin/standalone/neahttadigisanit.jquery.min.js \
			bin/standalone/neahttadigisanit.min.js

standalone-install: bin/standalone/neahttadigisanit.css \
					bin/standalone/neahttadigisanit.jquery.min.js \
					bin/standalone/neahttadigisanit.min.js
	cp bin/standalone/*.js ../neahtta/static/js/
	cp bin/standalone/*.css ../neahtta/static/css/
	@echo "    ... Installed"

bin/wordpress-neahttadigisanit.zip: src/wordpress \
				   		tmp/jq.css \
				   		tmp/nds.with.deps.jq.js
	@echo "   ... Copying css and js."
	cp -R src/wordpress tmp/wordpress
	cp tmp/jq.css tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.css
	cp tmp/nds.with.deps.jq.js tmp/wordpress/neahttadigisanit/jquery.neahttadigisanit.js
	@echo "   ... Zipping"
	cd tmp/wordpress && zip -r neahttadigisanit.zip neahttadigisanit/*
	cp tmp/wordpress/neahttadigisanit.zip bin/wordpress-neahttadigisanit.zip

.PHONY: wordpress
wordpress: bin/wordpress-neahttadigisanit.zip

tmp/neahttadigisanit.init.min.js: src/neahttadigisanit.init.js
	$(UGLY) $^ > $@

bin/bookmarklet/bookmarklet.min.js: tmp/nds.with.deps.jq.js \
						tmp/neahttadigisanit.init.min.js
	mkdir -p bin/bookmarklet
	cat $^ > $@

bin/bookmarklet/jquery.neahttadigisanit.css: tmp/jq.css
	mkdir -p bin/bookmarklet
	cp $^ $@

bookmarklet: bin/bookmarklet/jquery.neahttadigisanit.css \
			 bin/bookmarklet/bookmarklet.min.js

bookmarklet-install: bin/bookmarklet/jquery.neahttadigisanit.css \
					bin/bookmarklet/bookmarklet.min.js
	cp bin/bookmarklet/*.js ../neahtta/static/js/
	cp bin/bookmarklet/*.css ../neahtta/static/css/
	@echo "    ... Installed"

# TODO: actual bookmark code, need to urlencode that and copy somewhere.
#
# bin/bookmark.js: src/bookmark.js
#
# it's tricky because only part of it is urlencoded, but not all of it.

.PHONY: install
install: standalone-install \
		 bookmarklet-install

.PHONY: all
all: standalone

.PHONY: clean
clean: 
	rm -rf tmp/* bin/*

