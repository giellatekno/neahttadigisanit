module.Selection = @Selection =
  # MWE attempts so far: 
  #  
  #  * selection.expand using regular expressions containing potential MWE
  #    surroundign material
  #
  #  * selection.move for arbitrary expansion based on word regexp and word
  #  units
  #
  #  * TODO: expand text to parent container to get whole sentence as a string, then
  #  determine based on selection range what w+1 and w-1 are-- skip rangy for
  #  expansion

  expandByWordRegex: (selection) ->
    # This expands text by word regexp, to include any characters that might
    # not be perceived as standard word characters by a browser.
    opts = $.fn.getCurrentDictOpts().settings

    word_opts = {}

    if not window.word_regex
      word_regex = new RegExp(opts.word_regex, opts.word_regex_opts)
      window.word_regex = word_regex
    else
      word_regex = window.word_regex

    word_opts.trim = true
    word_opts.wordOptions =
      wordRegex: word_regex

    selection.expand("word", word_opts)

    return selection
    
  getParentFullText: (selection) ->
    range = (if selection.rangeCount then selection.getRangeAt(0) else null)
    if range
      return range.commonAncestorContainer.wholeText
    else
      return false

  getFirstRange: ->
    opts = $.fn.getCurrentDictOpts().settings

    # make the selection
    sel = rangy.getSelection()

    # moveStart requires a range instead

    if opts
      if opts.word_regex and opts.word_regex_opts
        console.log "words expand yes"
        sel = @expandByWordRegex sel

    full_text = @getParentFullText(sel)

    current_range_obj = (if sel.rangeCount then sel.getRangeAt(0) else null)
    
    # TODO: how to access range in indexes of selected item? Apparently can
    # only do this relative to all text in the document.

    return [current_range_obj, full_text]
  
  cloneContents: (range) ->
    range.cloneContents().textContent
  
  surroundRange: (range, surrounder) ->
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

