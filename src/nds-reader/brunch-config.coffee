# Some websites already using commonjs-require or requirejs will conflict with
# the local commonjs-require, so in the build process we need to make a
# no-conflict require definition.

# This is our own brand of commonjs-require-definition, which simply has
# 'require' replaced with ndsrequire

commonjsNoConflict = require('./commonjs-require-definition')

exports.config =
  modules:
    definition: (path, data) ->
      return commonjsNoConflict

    wrapper: (path, data) ->
      path = path.replace(/.(js|coffee)$/,'')
      console.log path
      if path == 'lib/rangy-core'
        path = 'rangy'
      if path == 'lib/rangy-textrange'
        path = 'rangy-textrange'
      # This is the one we don't want to wrap with require, but we wrap in a
      # closure anyway to get everything out of the global namespace, with the
      # exception that ndsrequire is included in the whole thing.
      if path == 'src/initialize'
        return """
(function (require) {
#{data}
})(ndsrequire);\n\n
"""
      # Otherwise, register as usual with our own commonjs, 
      return """\n\n
ndsrequire.register({"#{path}": function(exports, ndsrequire, module) {
  var require = ndsrequire;
  #{data}
}});\n\n
"""
    nameCleaner: (path) ->
      if path == 'lib/rangy-core.js'
        return 'rangy'
      if path == 'lib/rangy-textrange.js'
        return 'rangy-textrange'
      return path
  conventions:
    ignored: [
      "src/bookmark.js",
      # these must be ignored and later added to the bookmarklet
      "src/bookmarklet.init.js",
      "src/neahttadigisanit.init.js",
      /^src\/chrome/,
      /^src\/wordpress/,
      "lib/rangy-1.3",
      "lib/rangy-1.3.0-alpha.20140825",
    ]
  paths:
    public: "bin/"
    watched: [
      "src/css",
      "src/",
      "lib/"
    ]
  files:
    javascripts:
      joinTo:
        'app.js': /^(src|lib)/
      order:
        before: [
          "lib/bootstrap-dropdown.js",
          "lib/bootstrap-tooltip.js",
          "lib/bootstrap-popover.js",
          "lib/bootstrap-modal.js",
          # NB: modified version of DSt
          "src/DSt.js",
          "lib/underscore.js",
          "lib/semver.js",
          "lib/rangy-core.js",
          "lib/rangy-textrange.js",
          "src/application.coffee"
          "src/dictionary.coffee",
          "src/selection.coffee",
          "src/templates.coffee",
          "src/jquery.neahttadigisanit.coffee",
        ]
        after: [
          # problem here is probably that thing needs to be included in a way
          # that brunch doesn't necessarily allow for 
          "src/initialize.coffee",
        ]
    stylesheets:
      joinTo:
        'app.css': /^src\/css/
      order:
        before: "bootstrap.custom.css"
        after: "jquery.neahttadigisanit.css"

