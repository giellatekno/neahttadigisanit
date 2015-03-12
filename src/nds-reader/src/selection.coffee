rangy = require 'rangy'

module.exports = class Selection

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

    console.log selection
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
    # index of current word, slicing is inaccurate.

    # TODO: make sure word regex is set-- currently a bad practice to expect it to be
    #
    before = before.match(window.word_regex)
    if before
      # selected_words = before.slice(before.length-n, before.length)
      selected_words = before.slice(parseInt("-#{n}"))
    else
      selected_words = []

    return selected_words

  getMultiwordEnvironment: (l=1, r=1, t="#LOOKUP#") ->
    previous_words = @getPreviousWords l
    following_words = @getNextWords r

    if previous_words.length > 0
      previous_words.push(t)
    else if previous_words.length == 0 and following_words.length > 0
      following_words.unshift(t)

    combinations = previous_words.zipPermutations(following_words)

    return combinations

  getMultiwordPermutations: (l=1, r=1) ->
    t = window.selected_range.text()
    mws = @getMultiwordEnvironment(l, r, t)
    word_delimiter = ' '

    joined = []

    for mw in mws
      _mw = mw.join(word_delimiter)
      if _mw.length > 0 and _mw.search(t) > -1
        joined.push(_mw)

    joined = _.uniq(joined)

    return joined

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
