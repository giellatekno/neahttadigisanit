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

APP_FILES = $(JS_DEPS) \
			$(STYLESHEETS)

COMPILED_FILES = \
  bin/jquery.neahttadigisanit.css \
  bin/jquery.neahttadigisanit.js

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

#
## From the old standalone target

bin/neahttadigisanit.min.js: tmp/nds.with.deps.js
	@echo "   ... copying"
	cp $^ $@

bin/neahttadigisanit.jquery.min.js: tmp/nds.with.deps.jq.js
	@echo "   ... uglifying"
	$(UGLY) $^ > $@

bin/neahttadigisanit.css: tmp/jq.css
	@echo "   ... copying"
	cp $^ $@

# We build one with jquery and one without, to give the user the option of how
# they include it on their site.
.PHONY: standalone
standalone: bin/neahttadigisanit.css \
			bin/neahttadigisanit.jquery.min.js \
			bin/neahttadigisanit.min.js



# TODO: no longer actually building this.
# buildChrome = (callback) ->
#   pluginTargetDir = 'bin/chrome/'
#   # copy to bin/chrome/
# 
#   # copy compiled files compiledFiles
#   wrench.copyDirSyncRecursive('src/chrome', 'bin/chrome')
# 
#   # cp compiledFiles
#   for file in compiledFiles
#     _in = fs.readFileSync 'bin/' + file
#     fs.writeFileSync "bin/chrome/#{file}", _in
# 

# TODO: compile wordpress src files
bin/wordpress.zip: src/wordpress
	@echo "   ... Copying"
	cp -R src/wordpress tmp/wordpress
	@echo "   ... Zipping"
	zip bin/wordpress.zip tmp/wordpress

.PHONY: wordpress
wordpress: bin/wordpress.zip

# buildWordpress = (callback) ->
#   pluginTargetDir = 'bin/wordpress/'
# 
#   # copy compiled files compiledFiles
#   wrench.copyDirSyncRecursive('src/wordpress', 'bin/wordpress')
# 
#   # cp compiledFiles
#   for file in compiledFiles
#     _in = fs.readFileSync 'bin/' + file
#     fs.writeFileSync "bin/wordpress/neahttadigisanit/#{file}", _in

bookmarklet: bin/neahttadigisanit.init.min.js \
			 bin/jquery.neahttadigisanit.css \
			 bin/jquery.neahttadigisanit.js \
			 bin/jquery.neahttadigisanit.min.js \
			 bin/bookmarklet.min.js \
			 bin/bookmarklet.js

# buildBookmarklet = (callback) ->
#   # dev/jquery.1.7.2.js  (minified)
#   # bin/jquery.neahttadigisanit.min.js 
#   # src/bookmarklet.init.js (not minified)
#   #
#   # TODO: minify bookmark.js to ../static/js/bookmark.min.js
# 
#   util.print "\n Compressing... src/neahttadigisanit.init.js\n"
#   all = (fs.readFileSync 'src/neahttadigisanit.init.js').toString()
# 
#   ast = uglify.parser.parse all
#   out = fs.openSync "bin/neahttadigisanit.init.min.js", "w+"
# 
#   ast = uglify.uglify.ast_mangle ast
#   ast = uglify.uglify.ast_squeeze ast
# 
#   # fs.writeSync out, uglify.uglify.gen_code(ast)
#   fs.writeSync out, all
# 
#   util.print "\n Minified! to neahttadigisanit.init.min.js\n"
# 
#   _fs_nm = (fs.readFileSync 'dev/jquery.1.7.2.js').toString() +
#         (fs.readFileSync 'bin/jquery.neahttadigisanit.js').toString() +
#         (fs.readFileSync 'src/neahttadigisanit.init.js').toString()
#   out_nonmin = fs.openSync "bin/bookmarklet.js", "w+"
#   fs.writeSync out_nonmin, _fs_nm
# 
#   _fs = (fs.readFileSync 'dev/jquery.1.7.2.js').toString() +
#         (fs.readFileSync 'bin/jquery.neahttadigisanit.min.js').toString() +
#         (fs.readFileSync 'bin/neahttadigisanit.init.min.js').toString()
#   out = fs.openSync "bin/bookmarklet.min.js", "w+"
#   fs.writeSync out, _fs
# 
#   out = fs.openSync "../neahtta/static/js/bookmarklet.min.js", "w+"
#   fs.writeSync out, _fs
#   out = fs.openSync "../neahtta/static/js/bookmarklet.js", "w+"
#   fs.writeSync out, _fs_nm
#   util.print """\n Compiled to bin/bookmarklet.min.js and
#     ../static/js/bookmarklet.min.js\n"""
# 
#   _css = (fs.readFileSync 'bin/jquery.neahttadigisanit.css').toString()
#   _cssout = fs.openSync "../neahtta/static/css/jquery.neahttadigisanit.css", "w+"
#   fs.writeSync _cssout, _css
#   util.print "\n Copied CSS to ../static/css/jquery.neahttadigisanit.css\n"


# 
# 
# task 'watch', 'Watch prod source files and build changes', ->
#   invoke 'build'
#   util.log "Watching for changes in src"
# 
#   for file in appFiles then do (file) ->
#     fs.watchFile file, (curr, prev) ->
#       if +curr.mtime isnt +prev.mtime
#         util.log "Saw change in #{file}"
#         util.log 'Whoa. Saw a change. Building. Hold plz.'
#         invoke 'build'
 
# 
# task 'build-bookmarklet-debug', 'Compile the unminified plugin and jQuery to be downloaded by a bookmarklet', ->
#   buildBookmarkletDebug()
#   util.print "Bookmarklet compiled to bin/bookmarklet.min.js"
# 
.PHONY: install
install: install-standalone \
		 install-bookmarklet 

.PHONY: all
all: standalone

.PHONY: clean
clean: 
	rm -rf tmp/* bin/*

