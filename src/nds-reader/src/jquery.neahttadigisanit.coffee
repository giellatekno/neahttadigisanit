###

A jQuery plugin for allowing users to click to look up words
from Neahttadigisánit dictionary services.

###

String::startsWith = (str) ->
  return this.slice(0, str.length) == str

String::endsWith = (str) ->
  return this.slice(-str.length) == str

compileBareRegex = (word_regex, str_list, filter=false) ->

  createWordChunk = (part) =>
    raw = part
  
    after = false
    before = false
    # inner = false
  
    if part.startsWith('%WORD%')
      after = true
    if part.endsWith('%WORD%')
      before = true
    # if not after and before and '%WORD%' in part
    #   inner = true
  
    extension = part.replace('%WORD%', '')
  
    return extension.trim()

  if filter
    filterBySide = (i) =>
      if filter == 'start'
        return i.startsWith('%WORD%')
      if filter == 'end'
        return i.endsWith('%WORD%')
      return false
    str_list = str_list.filter filterBySide

  regex_string = str_list.map(createWordChunk)
                         .join('|')

  return "(#{regex_string})"


compileRegex = (word_regex, str_list, filter=false) ->

  createWordChunk = (part) =>
    raw = part
  
    after = false
    before = false
    # inner = false
  
    if part.startsWith('%WORD%')
      after = true
    if part.endsWith('%WORD%')
      before = true
    # if not after and before and '%WORD%' in part
    #   inner = true
  
    extension = part.replace('%WORD%', '')
    wrapped = "(#{extension})?"
  
    if after
      return word_regex + wrapped
    if before
      return wrapped + word_regex

  if filter
    filterBySide = (i) =>
      if filter == 'start'
        return i.startsWith('%WORD%')
      if filter == 'end'
        return i.endsWith('%WORD%')
      return false
    str_list = str_list.filter filterBySide

  regex_string = str_list.map(createWordChunk)
                         .join(')|(')

  return "(#{regex_string})"

# Wrap jQuery and add plugin functionality
jQuery(document).ready ($) ->

  getHostShortname = (url_path) ->
    url = document.createElement('a')
    url.href = url_path
    host = url.hostname
    if host
      return host.split('.')[0]
    return false

  first = (somearray) ->
    if somearray.length > 0
      return somearray[0]
    else
      return false

  # A shortcut
  Templates = module.Templates
  _ = module.fakeGetText

  # Global values set by the bookmarklet init script or manual inclusion
  API_HOST = window.NDS_API_HOST || window.API_HOST
  window.NDS_SHORT_NAME = getHostShortname(API_HOST)

  window.nds_exports = {}

  # Increment this whenever the bookmarklet code (_not this file_) has changed.
  # This way the plugin will notify users to update their bookmark.
  EXPECT_BOOKMARKLET_VERSION = '0.0.3'

  # An object to store all the templates.
  #
  # TODO: switch to another file, and compile together-- maybe require.js?

  initSpinner = (imgPath) ->
    ###
        spinner popup in right corner; `spinner = initSpinner()` to
        create or find, then usual `spinner.show()` or `.hide()` as
        needed.
    ###
    spinnerExists = $(document).find('.spinner')
    if spinnerExists.length == 0
      spinner = $("""<img src="#{imgPath}" class="spinner" />""")
      $(document).find('body').append(spinner)
      return spinner
    return spinnerExists

  ## Some global ajax stuff
  ##
  ## 

  $.ajaxSetup
    type: "GET"
    timeout: 10 * 1000
    beforeSend: (args) ->
      spinner = initSpinner()
      spinner.show()
    complete: (args) ->
      spinner = initSpinner()
      spinner.hide()
    dataType: "json"
    cache: true
    error: () =>
      $(document).find('body').find('.errornav').remove()
      $(document).find('body').append Templates.ErrorBar {
        host: API_HOST
      }

  ##
  ## Some rangy helper functions 
  ## 

  expandMultiWords = (selection) ->
    # TODO: either list of words before works, or list of words after works--
    # apparently need to run expansion of selection in two rounds-- one for
    # left and one for right

    opts = $.fn.getCurrentDictOpts().settings

    # TODO: at least with the whole hdn multiword list this seems to be
    # overgenerating. need to reconsider how to build the regex

    multiword_opts = {}

    # compile regex and store it to some global variable
    if not window.regex_compiled
      #
      # TODO: haida still has issues with the whole expansion wordlist --
      # so far only words after work, and not all words provide a result.
      # gatáa.ang ñasaasdlä'ánggang
      #
      # TODO: compileRegex filter by before and after to make this into two
      # steps? 
      # regex_string = compileRegex(opts.word_regex, opts.multiwords)
      # TODO: what to do if the result of one of these is none?
      #
      # TODO: try selection.moveStart and selection.moveEnd, specifying accepted words as MWE list
      # moveStart('word', 1, multiwords_after_options)
      regex_string_ends = compileBareRegex(opts.word_regex, opts.multiwords, filter='start')
      regex_string_starts = compileBareRegex(opts.word_regex, opts.multiwords, filter='end')

      window.multiword_lookup_regex_start = new RegExp(regex_string_starts, 'g')
      window.multiword_lookup_regex_end = new RegExp(regex_string_ends, 'g')
      window.regex_compiled = true

    multiwords_start_options =
      wordOptions:
        wordRegex: window.multiword_lookup_regex_start
      trim: true
    multiwords_end_options =
      wordOptions:
        wordRegex: window.multiword_lookup_regex_end
      trim: true

    console.log "moving selection"
    console.log selection

    # NB: this works on range object only.
    selection.moveStart("word", 1, multiwords_start_options)
    selection.moveEnd("word", 1, multiwords_end_options)
    console.log selection

    return selection

  expandByWordRegex = (selection) ->
    opts = $.fn.getCurrentDictOpts().settings

    word_opts = {}

    word_regex = new RegExp(opts.word_regex, opts.word_regex_opts)
    word_opts.trim = true
    word_opts.wordOptions =
      wordRegex: word_regex

    selection.expand("word", word_opts)

    return selection

  getFirstRange = ->
    opts = $.fn.getCurrentDictOpts().settings

    # make the selection
    sel = rangy.getSelection()

    # moveStart requires a range instead

    if opts
      if opts.word_regex and opts.word_regex_opts
        console.log "words expand yes"
        sel = expandByWordRegex sel
      # if opts.multiword_lookups
      #   console.log "mwe yes"
      #   sel = expandMultiWords sel

    current_range_obj = (if sel.rangeCount then sel.getRangeAt(0) else null)
    if opts and current_range_obj
      if opts.multiword_lookups
        console.log "mwe yes"
        current_range_obj = expandMultiWords current_range_obj
    return current_range_obj
  
  cloneContents = (range) ->
    range.cloneContents().textContent
  
  surroundRange = (range, surrounder) ->
    if range
      if not range.canSurroundContents()
        # TODO: should be possible to recover from this sometimes, as
        # non-FF browsers do not have this issue
        return false
      try
        range.surroundContents surrounder
      catch ex
        if (ex instanceof rangy.RangeException \
            or Object::toString.call(ex) is "[object RangeException]") \
            and ex.code is 1
          alert """Unable to surround range because range partially selects a
                   non-text node. See DOM Level 2 Range spec for more
                   information.\n\n""" + ex
        else
          alert "Unexpected errror: " + ex

  ##
  ## NDS Functionality
  ## 

  cleanTooltipResponse = (selection, response, opts) ->
    ###
        Clean response from tooltip $.getJSON query, and display results
    ###

    string   = selection.string
    element  = selection.element
    range    = selection.range

    if opts.tooltip
      _wrapElement = $("""
      <a style="font-style: italic; border: 1px solid #CEE; padding: 0 2px" 
         class="tooltip_target">#{string}</a>
      """)[0]
      surroundRange(range, _wrapElement)

    # Compile result strings
    result_strings = []
    for result in response.result
      for lookup in result.lookups
        if lookup.right.length > 1
          clean_right = []
          for r, i in lookup.right
            clean_right.push "#{i+1}. #{r}"
          right = clean_right.join(', ')
        else
          right = lookup.right[0]

        result_string = "<em>#{lookup.left}</em> (#{lookup.pos}) &mdash; #{right}"
        result_strings.push(result_string)

    langpair = DSt.get(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair')
    [_f_from, _t_to] = langpair.split('-')

    _cp = first window.nds_opts.dictionaries.filter (e) =>
      e.from.iso == _f_from and e.to.iso == _t_to
    
    if _cp
      current_pair_names = "#{_cp.from.name} → #{_cp.to.name}"
    else
      current_pair_names = ""

    if result_strings.length == 0 or response.success == false
      if opts.tooltip
        _tooltipTitle = _('Unknown word')
        result_strings.push("<span class='tags'><em>#{_('You are using')} #{current_pair_names}</em></span>")
        if response.tags.length > 0
          _tooltipTitle = _('Meaning not found')

    if opts.tooltip
      if !_tooltipTitle
        _tooltipTitle = string
      
      _tooltipTarget = $(element).find('a.tooltip_target')

      _tooltipTarget.popover
        title: _tooltipTitle
        content: $("<p />").html(result_strings.join('<br />')).html()
        html: true
        placement: () =>
          if _tooltipTarget[0].offsetLeft < 125
            'right'
          else
            'bottom'
        trigger: 'hover'
      
      # Remove selection
      if window.getSelection
        # Chrome
        if window.getSelection().empty
          window.getSelection().empty()
        # Firefox
        else if window.getSelection().removeAllRanges
          window.getSelection().removeAllRanges()
      # IE
      else if document.selection
        document.selection.empty()
      # Done
      _tooltipTarget.popover('show')

  lookupSelectEvent = (evt, string, element, range, opts) ->

    # TODO: what breaks here with spaces
    #
    result_elem = $(document).find(opts.formResults)

    # Remove punctuation, some browsers select it by default with double
    # click
    string = $.trim(string)
              .replace(/\b[-.,()&$#!\[\]{}"]+\B|\B[-.,()&$#!\[\]{}"]+\b/g, "")

    # TODO: spaces allowed parameter set by existence of MWE list

    settings = $.fn.getCurrentDictOpts().settings
    if settings.multiword_lookups
      if (string.length > 120)
        console.log "DEBUG: string was too long."
        console.log string.length
        return false
    else
      if (string.length > 60) or (string.search(' ') > -1)
        console.log "DEBUG: string was too long or contained spaces."
        console.log string.length
        return false

    langpair = DSt.get(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair')
    # "aaa-bbb"
    [source_lang, target_lang] = langpair.split('-')
    lookup_string = string

    _cp = first window.nds_opts.dictionaries.filter (e) =>
      e.from.iso == source_lang and e.to.iso == target_lang
    
    if _cp?
      uri = _cp.uri
    else
      uri = false

    window.cp = _cp

    post_data =
      lookup: lookup_string
      lemmatize: true

    url = "#{opts.api_host}/#{uri}"

    $.getJSON(
      url + '?callback=?'
      post_data
      (response) =>
        selection = {
          string: string
          element: element
          range: range
        }
        cleanTooltipResponse(selection, response, opts)
    )
    return false

  ##
   # $(document).selectToLookup();
   #
   #
   ##

  $.fn.selectToLookup = (opts) ->
    opts = $.extend {}, $.fn.selectToLookup.options, opts
    window.nds_opts = opts
    spinner = initSpinner(opts.spinnerImg)

    if window.NDS_API_HOST || window.API_HOST
      window.API_HOST = window.NDS_API_HOST || window.API_HOST
    if nds_opts.api_host
      window.API_HOST = nds_opts.api_host

    window.NDS_SHORT_NAME = getHostShortname(nds_opts.api_host)

    # version notify
    newVersionNotify = () ->
      $.getJSON(
        nds_opts.api_host + '/read/update/json/' + '?callback=?'
        (response) ->
          $(document).find('body').append(
            Templates.NotifyWindow(response)
          )
          $(document).find('#notifications').modal({
            backdrop: true
            keyboard: true
          })
          $('#close_modal').click () ->
            $('#notifications').modal('hide')
            DSt.set(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair', null)
            DSt.set(NDS_SHORT_NAME + '-' + 'nds-languages', null)
            DSt.set(NDS_SHORT_NAME + '-' + 'nds-localization', null)
            DSt.set(NDS_SHORT_NAME + '-' + 'nds-stored-config', null)
            window.location.reload()
            return false
      )
      return false

    window.newVersionNotify = newVersionNotify

    ie8Notify = () ->
      $.getJSON(
        nds_opts.api_host + "/read/ie8_instructions/json/" + '?callback=?'
        (response) ->
          $(document).find('body').prepend(
            Templates.NotifyWindow(response)
          )
          $(document).find('#notifications').modal({
            backdrop: true
            keyboard: true
          })
          $('#close_modal').click () ->
            $('#notifications').modal('hide')
            DSt.set(NDS_SHORT_NAME + '-' + 'nds-ie8-dismissed', true)
            return false
      )
      return true

    window.ie8Notify = ie8Notify

    # This runs after either we get the response from the server about
    # language pairs and internationalization, or recover it from local
    # storage.
    initializeWithSettings = () ->
      # Delete temporary thing.
      delete window.lookup_regex

      if window.nds_opts.displayOptions
        $(document).find('body').append Templates.OptionsTab(window.nds_opts)
        window.optTab = $(document).find('#webdict_options')
        ### Over 9000?!! ###
        window.optTab.css('z-index', 9000)

      # Recall stored language pair from session
      previous_langpair = DSt.get(
        NDS_SHORT_NAME + '-' + 'digisanit-select-langpair'
      )
      if previous_langpair
        _select = "select[name='language_pair']"
        _opt = window.optTab.find(_select).val(previous_langpair)
      else
        _select = "select[name='language_pair']"
        _opt = window.optTab.find(_select).val()
        previous_langpair = DSt.set(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair', _opt)
      
      holdingOption = (evt) =>
        clean(evt)

        if evt.altKey
          element = evt.target
          within_options = $(element).parents('#webdict_options')
          if within_options.length > 0
            $(within_options[0]).find('#debug').show()
            return false
          range = getFirstRange()
          string = cloneContents(range)
          if range and string
            lookupSelectEvent(evt, string, element, range, window.nds_opts)
          return false
        return true

      clean = (event) ->
        parents = []
        $(document).find('a.tooltip_target').each () ->
          parents.push $(this).parent()
          $(this).popover('destroy')
          $(this).replaceWith(this.childNodes)

        $(document).find('a.tooltip_target').contents().unwrap()

      window.cleanTooltips = clean
      $(document).bind('click', holdingOption)

    storeConfigs = (response) ->
      # store in local storage
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-languages',    response.dictionaries)
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-localization', response.localization)
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-stored-config', "true")
      return true

    extendLanguageOpts = (response) =>
      window.r_test = response
      window.nds_opts.dictionaries = response.dictionaries
      window.nds_opts.localization = response.localization
      storeConfigs(response)
      return

    fetchConfigs = () ->
      url = "#{opts.api_host}/read/config/"
      $.getJSON(
        url + '?callback=?'
        extendLanguageOpts
      )

    extendLanguageOptsAndInit = (response) =>
      extendLanguageOpts(response)
      initializeWithSettings()

    recallLanguageOpts = () =>
      # Sometimes this ends up not getting parsed from JSON
      # automatically from DSt.get, even though .set properly stores it.
      locales = DSt.get(NDS_SHORT_NAME + '-' + 'nds-localization')
      if typeof locales == "string"
        locales = JSON.parse locales
      window.nds_opts.localization = locales

      dicts = DSt.get(NDS_SHORT_NAME + '-' + 'nds-languages')
      if typeof dicts == "string"
        dicts = JSON.parse dicts
      window.nds_opts.dictionaries = dicts

      initializeWithSettings()


    ##
    ## Check the version of the bookmark and compare with what the
    ## plugin desires, and also check for IE8. If either of these is
    ## true, then we display some notifications to the user that they
    ## need to change some settings or update.
    ##

    version_ok = false

    if window.NDS_BOOKMARK_VERSION?
      version_ok = semver.gte( window.NDS_BOOKMARK_VERSION
                             , EXPECT_BOOKMARKLET_VERSION
                             )
    else
      version_ok = true

    uagent = navigator.userAgent
    [old_ie, dismissed] = [false, false]
    if "MSIE 8.0" in uagent
      old_ie = true
      dismissed = DSt.get(NDS_SHORT_NAME + '-' + 'nds-ie8-dismissed')

    if version_ok
      if old_ie
        console.log "ie8 detected"
        if not dismissed
          ie8Notify()
      stored_config = DSt.get(NDS_SHORT_NAME + '-' + 'nds-stored-config')
      if stored_config?
        recallLanguageOpts()
      else
        url = "#{opts.api_host}/read/config/"
        $.getJSON(
          url + '?callback=?'
          extendLanguageOptsAndInit
        )
      return false
    else
      newVersionNotify()
      return false

    # TODO: one idea for how to handle lookups wtihout alt/option key
    #
    # else
    #   if string != ''
    #     window.optTab.find('.well').addClass('highlight')
    #     window.optTab.find('.well a.open').click (o) =>
    #       lookupSelectEvent(evt, string, element, index, opts)
    #       return false
    #   else
    #     window.optTab.find('.well').removeClass('highlight')

  $.fn.getOptsForDict = (_from, _to) ->
    for dict in window.nds_opts.dictionaries
      if dict.from.iso == _from and dict.to.iso == _to
        return dict

  $.fn.getCurrentDictOpts = () ->
    pair = DSt.get(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair')
    [_from, _to] = pair.split('-')
    $.fn.getOptsForDict _from, _to

  $.fn.selectToLookup.options =
    api_host: API_HOST
    formResults: "#results"
    spinnerImg: "/static/img/spinner.gif"
    sourceLanguage: "sme"
    langPairSelect: "#webdict_options *[name='language_pair']"
    tooltip: true
    # Provide a word regex to improve the selection system.
    languageWordOptions: false
    displayOptions: true
    dictionaries: [
      {
        from:
          iso: 'sme'
          name: 'nordsamisk'
        to:
          iso: 'nob'
          name: 'norsk'
        uri: '/lookup/sme/nob/'
      }
    ]

# End jQuery wrap
