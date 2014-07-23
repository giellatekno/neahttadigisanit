module.Selection = @Selection =

  compileBareRegex: (word_regex, str_list, filter=false) ->
    # TODO: another option
    #   expand to include word +1 and -1, do multiple lookups, move selection
    #   to the one that matches.
    #
    # TODO: escape word list
    #
    escapeRegExp = (str) ->
      return str.replace(/([.*+?^${}()|\[\]\/\\])/g, "\\$1")
  
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
                           .map(escapeRegExp)
                           .join('|')
  
    return "(#{regex_string})"
  
  expandMultiWords: (selection) ->
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
      # TODO: try selection.moveStart and selection.moveEnd, specifying accepted words as MWE list
      # moveStart('word', 1, multiwords_after_options)
      #    - this didn't entirely seem to work, or the regex was compiled
      #    wrong-- plus it's a method on range, which takes other code changes
      #    elsewhere
      # 
      # TODO: also consider just one big regex including optional ends with the
      # multiword lists... that shouuuld be able to work.
      #
      regex_string_ends = @compileBareRegex(opts.word_regex, opts.multiwords, filter='start')
      regex_string_starts = @compileBareRegex(opts.word_regex, opts.multiwords, filter='end')

      window.multiword_lookup_regex_start = new RegExp(regex_string_starts, 'g')
      window.multiword_lookup_regex_end = new RegExp(regex_string_ends, 'g')
      window.multiword_word_regex = new RegExp(opts.word_regex, opts.word_regex_opts)
      window.regex_compiled = true

    multiwords_start_options =
      wordOptions:
        wordRegex: window.multiword_word_regex
        # wordRegex: window.multiword_lookup_regex_start
      trim: true
    multiwords_end_options =
      wordOptions:
        wordRegex: window.multiword_word_regex
        # wordRegex: window.multiword_lookup_regex_end
      trim: true

    console.log "moving selection"
    console.log "before"
    console.log selection

    # NB: this works on range object only.
    selection.expand("word", multiwords_start_options)
    selection.expand("word", multiwords_end_options)
    console.log "after"
    console.log selection

    return selection

  expandByWordRegex: (selection) ->
    # TODO: consider including before and after in the main lookup regex
    opts = $.fn.getCurrentDictOpts().settings

    word_opts = {}

    word_regex = new RegExp(opts.word_regex, opts.word_regex_opts)

    console.log opts.word_regex
    window.word_regex = opts.word_regex
    
    word_opts.trim = true
    word_opts.wordOptions =
      wordRegex: word_regex

    selection.expand("word", word_opts)

    return selection

  getFirstRange: ->
    opts = $.fn.getCurrentDictOpts().settings

    # make the selection
    sel = rangy.getSelection()

    # moveStart requires a range instead

    if opts
      if opts.word_regex and opts.word_regex_opts
        console.log "words expand yes"
        sel = @expandByWordRegex sel
      # if opts.multiword_lookups
      #   console.log "mwe yes"
      #   sel = expandMultiWords sel

    current_range_obj = (if sel.rangeCount then sel.getRangeAt(0) else null)
    if opts and current_range_obj
      if opts.multiword_lookups
        console.log "mwe yes"
        current_range_obj = @expandMultiWords current_range_obj
    return current_range_obj
  
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

