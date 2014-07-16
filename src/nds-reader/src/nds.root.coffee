module = {}

module.fakeGetText = (string) ->
  ### Want to mark strings as requiring gettext somehow, so that
      a babel can find them.

      NB: Babel only has a javascript extractor, so, just compile this
      with cake: 

          cake clean
          cake build
          cake build-bookmarklet

      Then when you run pybabel's extract command, it will find the
      strings in the unminified source in static/js/.

      Internationalizations are downloaded and stored in localStorage
      on the first run of the plugin. Translations should degrade to
      english if they are missing, or the localization is not present.

      The system will not store multiple localizations at a time, so
      we assume the user does not really want to switch.
  ###
  
  if window.nds_opts.localization?
    localized = window.nds_opts.localization[string]
    if localized?
      if localized
        return localized
  return string
