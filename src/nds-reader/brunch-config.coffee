exports.config =
  modules:
    nameCleaner: (path) ->
      if path == 'lib/rangy-core.js'
        return 'rangy'
      if path == 'lib/rangy-textrange.js'
        return 'rangy-textrange'
      return path
  conventions:
    ignored: [
      "src/bookmark.js",
      /^src\/chrome/,
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
      before: [
        "lib/bootstrap-dropdown.js",
        "lib/bootstrap-tooltip.js",
        "lib/bootstrap-popover.js",
        "lib/bootstrap-modal.js",
        "lib/underscore.js",
        "lib/DSt.js",
        "lib/semver.js",
        "lib/rangy-core.js",
        "lib/rangy-textrange.js",
        # problem here is probably that thing needs to be included in a way
        # that brunch doesn't necessarily allow for 
        "src/application.coffee"
        "src/dictionary.coffee",
        "src/selection.coffee",
        "src/templates.coffee",
        "src/initialize.coffee",
        "src/jquery.neahttadigisanit.coffee",
      ]

