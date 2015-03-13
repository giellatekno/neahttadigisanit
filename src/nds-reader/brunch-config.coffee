exports.config =
  modules:
    #     wrapper: (path, data) ->
    #       if path == 'lib/rangy-core.js'
    #         path = 'rangy'
    #       if path == 'lib/rangy-textrange.js'
    #         path = 'rangy-textrange'
    #       # This is the one we don't want to wrap
    #       # if path == 'src/initialize.coffee'
    #       #   return data
    #       return """
    # require.register({#{path}: function(exports, require, module) {
    #   #{data}
    # }});\n\n
    #  """
    nameCleaner: (path) ->
      if path == 'lib/rangy-core.js'
        return 'rangy'
      if path == 'lib/rangy-textrange.js'
        return 'rangy-textrange'
      return path
  conventions:
    ignored: [
      "src/bookmark.js",
      "src/bookmarklet.init.js",
      /^src\/chrome/,
      /^src\/wordpress/,
      /^src\/css/,
      "lib/rangy-1.3",
      "lib/rangy-1.3.0-alpha.20140825",
    ]
  paths:
    public: "bin/"
    watched: [
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

