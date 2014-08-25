module.DictionaryAPI = class DictionaryAPI

  constructor: (configs) ->
    @host = configs.host

  readConfig: (callback) ->
    # TODO: /read/config/, extend language opts.
    return false

  lookup: (source_lang, target_lang, string, callback=false) ->

    post_data =
      lookup: string
      lemmatize: true
      
    url = "#{@host}/lookup/#{source_lang}/#{target_lang}/" + '?callback=?'

    if not callback
      callback_func = (r) -> console.log r
    else
      callback_func = callback

    # TODO: convert this to a $.get or something to be able to supply expected
    # success/fail funcs
    #
    $.post(
      url + '?callback=?',
      post_data,
      callback_func
    )
