###

A jQuery plugin for allowing users to click to look up words
from Neahttadigisánit dictionary services.

###

Templates = module.Templates
Selection = module.Selection

# Wrap jQuery and add plugin functionality
jQuery(document).ready ($) ->

  _ = module.fakeGetText

  # TODO: generalized NDS API module
  # TODO: generalized reader module for handling requests

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

  # Global values set by the bookmarklet init script or manual inclusion
  API_HOST = window.NDS_API_HOST || window.API_HOST
  window.NDS_SHORT_NAME = getHostShortname(API_HOST)

  window.nds_exports = {}

  # Increment this whenever the bookmarklet code (_not this file_) has changed.
  # This way the plugin will notify users to update their bookmark.
  EXPECT_BOOKMARKLET_VERSION = '0.0.3'

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
  ## NDS Functionality
  ## 

  dictionary = new module.DictionaryAPI {
  	host: "//"
  }

  cleanTooltipResponse = (selection, response, opts) ->
    ###
        Clean response from tooltip $.post query, and display results
    ###

    string   = selection.string
    element  = selection.element
    range    = selection.range

    if opts.tooltip
      _wrapElement = $("""
      <a style="font-style: italic; border: 1px solid #CEE; padding: 0 2px" 
         class="tooltip_target">#{string}</a>
      """)[0]
      Selection.surroundRange(range, _wrapElement)

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

  lookupSelectEvent = (evt, string, element, range, opts, full_text) ->

    # TODO: what breaks here with spaces
    #
    result_elem = $(document).find(opts.formResults)

    # Remove punctuation, some browsers select it by default with double
    # click
    string = $.trim(string)
              .replace(/\b[-.,()&$#!\[\]{}"]+\B|\B[-.,()&$#!\[\]{}"]+\b/g, "")

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

    # Now why am I doing it this way? provide default pair from menu?
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

    # if full_text
    #   post_data.text_string = full_text
    
    # TODO: MWE option for including full text
    console.log range, full_text

    # TODO: partition on the selected word by the range
    ind = Selection.getIndexes()

    # TODO: move this to Selection module

    t = rangy.innerText(selected_range.startContainer)
    
    # This isn't actaully reproducing the selection with these indexes
    #

    previous_words = Selection.getPreviousWords(1)
    following_words = Selection.getNextWords(1)

    last_word = previous_words.slice(-1)[0]
    first_word = following_words[0]

    console.log [last_word, string, first_word]

    console.log "--"

    # TODO: also need to pass the indexes for the selected word

    url = "#{opts.api_host}/#{uri}?callback=?"

    # TODO: switch to actual post method, because GET will run out of space
    # fast.
    response_func = (response, textStatus) =>
      selection = {
        string: string
        element: element
        range: range
      }
      cleanTooltipResponse(selection, response, opts)

    # TODO: complete WTF, why is this coming out as a GET?
    $.post(url, post_data, response_func, "json")

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
          [range, full_text] = Selection.getFirstRange()
          string = Selection.cloneContents(range)
          if range and string
            lookupSelectEvent(evt, string, element, range, window.nds_opts, full_text)
          return false
        return true

      clean = (event) ->
        parents = []
        # TODO: any rangy cleaning operations
        # console.log "clean"
        # if window.last_selection
        #   console.log "last_selection"
        #   console.log window.last_selection
        #   console.log window.selected_range

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
