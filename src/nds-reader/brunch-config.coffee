exports.config =
  modules:
    wrapper: (path, data) ->
      # This function wraps compiled code. All modules are wrapped in the
      # commonjs module registration

      path = path.replace(/.(js|coffee)$/,'')

      if path == 'lib/rangy-core'
        path = 'rangy'
      if path == 'lib/rangy-textrange'
        path = 'rangy-textrange'
      if path == 'src/wrapper_start' or path == 'src/wrapper_end'
        return data
      # This is the one we don't want to wrap with require, but we wrap in a
      # closure anyway to get everything out of the global namespace, with the
      # exception that ndsrequire is included in the whole thing.
      if path == 'src/initialize'
        return """
(function () {
#{data}
})();\n\n
"""
      # Otherwise, register as usual with our own commonjs, 
      return """\n\n
require.register({"#{path}": function(exports, require, module) {
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
      "src/wrapper_start.js"
      "src/wrapper_end.js"
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
          "src/wrapper_start.js"
          "lib/rangy-core.js",
          "lib/rangy-textrange.js",
          "lib/bootstrap-dropdown.js",
          "lib/bootstrap-tooltip.js",
          "lib/bootstrap-popover.js",
          "lib/bootstrap-modal.js",
          # NB: modified version of DSt
          "src/DSt.js",
          "lib/underscore.js",
          "lib/semver.js",
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
          "src/wrapper_end.js"
        ]
    stylesheets:
      joinTo:
        'app.css': /^src\/css/
      order:
        before: "bootstrap.custom.css"
        after: "jquery.neahttadigisanit.css"

