module.Selection = class Selection

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
      return rangy.innerText(range.commonAncestorContainer)
    else
      return false

  getFirstRange: ->
    opts = $.fn.getCurrentDictOpts().settings

    # make the selection
    sel = rangy.getSelection()

    # moveStart requires a range instead

    if opts
      if opts.word_regex and opts.word_regex_opts
        sel = @expandByWordRegex sel

    full_text = @getParentFullText(sel)

    current_range_obj = (if sel.rangeCount then sel.getRangeAt(0) else null)
    # window.last_selection = sel
    window.selected_range = current_range_obj
    window.previous_contents = window.selected_range.commonAncestorContainer.innerHTML

    # TODO: track selection parent node-- if it is the same, it will change how
    # we index text, since indexes are recalculated when nodes are destroyed
    
    # TODO: how to access range in indexes of selected item? Apparently can
    # only do this relative to all text in the document.

    return [current_range_obj, full_text]
  
  cloneContents: (range) ->
    range.cloneContents().textContent

  getIndexes: () ->
    node = window.selected_range.commonAncestorContainer
    # get indexes relative to parent container if this node is a text node
    ranges = window.selected_range.toCharacterRange(node)
    return [ranges.start, ranges.end]

  getPartitionedSelection: () ->
    t = rangy.innerText(window.selected_range.startContainer)
    ind = @getIndexes()

    before = t.slice(0, ind[0])
    partition = t.slice(ind[0], ind[1])
    after = t.slice(ind[1])

    return [before, partition, after]

  getPreviousWords: (n=1) ->
    [before, _, _] = @getPartitionedSelection()

    # TODO: make sure word regex is set-- currently a bad practice to expect it to be
    #
    before = before.match(window.word_regex)
    if before
      selected_words = before.slice(before.length-n, before.length)
    else
      selected_words = []

    return selected_words

  getMultiwordEnvironment: (l=1, r=1) ->
    previous_words = @getPreviousWords l
    following_words = @getNextWords r

    # TODO: l/r
    last_word = previous_words.slice(-1)[0]
    first_word = following_words[0]

    return [last_word, "#LOOKUP#", first_word]

  getMultiwordPermutations: (l=1, r=1) ->
    mws = @getMultiwordEnvironment(l, r)
    word_delimiter = ' '

    t = window.selected_range.text()

    mwes = [t]

    if mws[0]
      mwes.push [mws[0], t].join(word_delimiter)
    if mws.slice(-1)[0]
      mwes.push [t, mws.slice(-1)[0]].join(word_delimiter)
    if mws[0] and mws.slice(-1)[0]
      mwes.push [mws[0], t, mws.slice(-1)[0]].join(word_delimiter)

    return mwes

  getNextWords: (n=1) ->
    [_, _, after] = @getPartitionedSelection()
    # TODO: make sure word regex is set-- currently a bad practice to expect it to be
    #
    after = after.match(window.word_regex)
    if after
      selected_words = after.slice(0, n)
    else
      selected_words = []
    return selected_words

  cleanRange: () ->
    if window.selected_range
      window.selected_range.commonAncestorContainer.normalize()
    return true

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
