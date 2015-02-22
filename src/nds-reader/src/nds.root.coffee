### This is the initial coffeescript file that sets up the module
    and provides some prototype definitions, as well as the
    internationalization function which must be present for everything else.
###

Array::zipPermutations = (right_list) ->
  left_list = this

  leftPermutations = (sublist) ->
    perms = []
    for x of _.range(1, sublist.length+1)
      _i = -Math.abs(x)
      if x > 0
        perms.push sublist.slice(_i)
    perms.push(sublist)
    return perms

  rightPermutations = (sublist) ->
    perms = []
    for x of _.range(1, sublist.length+1)
      if x > 0
        perms.push sublist.slice(0, x)
    perms.push(sublist)
    return perms

  lefts = leftPermutations(left_list)
  rights = rightPermutations(right_list)

  combined = []
  for l in lefts
    combined.push l

  for l in lefts
    for r in rights
      combine = l.concat(r)
      combined.push combine

  for r in rights
    combined.push r

  # for c in combined
  #   console.log c.join(' ')

  return combined

String::startsWith = (str) ->
  return this.slice(0, str.length) == str

String::endsWith = (str) ->
  return this.slice(-str.length) == str

module = {}

module.Rangy = rangy

module.fakeGetText = (string) ->
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
  
  if window.nds_opts.localization?
    localized = window.nds_opts.localization[string]
    if localized?
      if localized
        return localized
  return string
