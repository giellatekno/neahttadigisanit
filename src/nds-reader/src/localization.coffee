module.exports = fakeGetText = (string) ->
    ### Want to mark strings as requiring gettext somehow, so that
        a babel can find them.
  
        NB: Babel only has a javascript extractor, so, just compile the project
        to JS as normal, then when you run pybabel's extract command, it will
        find the strings in the unminified source in static/js/.
  
        Internationalizations are downloaded and stored in localStorage
        on the first run of the plugin. Translations should degrade to
        english if they are missing, or the localization is not present.
  
        The system will not store multiple localizations at a time, so
        we assume the user does not really want to switch.
    ###
    
    if NDS.options.localization?
      localized = NDS.options.localization[string]
      if localized?
        if localized
          return localized
    return string


