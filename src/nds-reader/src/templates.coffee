_ = require './localization'

BSDropdown = require('../lib/bootstrap-dropdown')
BSModal = require('../lib/bootstrap-modal')
# popover requires tooltip
BSTooltip = require('../lib/bootstrap-tooltip')
BSPopover = require('../lib/bootstrap-popover')

module.exports = class Templates
 
  renderPopup: (response, selection) ->
    # TODO: make this a uniform template with logic separated.
    #
    # NB: overriding underscorejs here.

    first = (somearray) ->
      if somearray.length > 0
        return somearray[0]
      else
        return false

    opts = window.nds_opts
    string   = selection.string
    element  = selection.element
    range    = selection.range

    matches_differ_from_click = false
    longest_input = string

    _inputs = {}
    for r in response.result
      for l in r.lookups
        _inputs[l.input] = true
        # Track the longest input from MWE permutations, which is likely the
        # MWE match
        if l.input.length > longest_input.length
          longest_input = l.input
        # Determine whether the match results differ from the user-selected
        # word.
        if string != l.input
          matches_differ_from_click = true
    multiple_inputs = (if Object.keys(_inputs).length > 1 then true else false)

    # make a set of all the results after removing the input key, or lemmas->inputs
    # 

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

        if result_string not in result_strings
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

    # TODO: if there are multiple same result matches:
    #   user clicks: gatáa.ang, results for:
    #     - gatáa.ang
    #     - gatáa.ang ñasa'áa
    #   collapse to one result, display longest match in title
    
    if opts.tooltip
      if !_tooltipTitle
        _tooltipTitle = string
    
      # This probably only happens in MWE lookups where there are different
      # possible inputs generated.
      if _tooltipTitle != longest_input
        _tooltipTitle = "#{_tooltipTitle} &rarr; #{longest_input}"
      
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
    
  NotifyWindow: (text) ->
    # NB: overriding underscorejs here.
    return $("""
      <div class="modal hide fade" id="notifications">
          <div class="modal-header">
              <button
                  type="button"
                  class="close"
                  data-dismiss="modal"
                  aria-hidden="true">&times;</button>
              <h3>Neahttadigisánit</h3>
          </div>
          <div class="modal-body">#{text}</div>
          <div class="modal-footer">
              <a href="#" class="btn btn-primary" id="close_modal">
                Continue
              </a>
          </div>
      </div>
      """)
  
  OptionsTab: (opts) ->
    # NB: overriding underscorejs here.
    makeLanguageOption = (options) ->
      # Count groups available-- if there are more than one then we need to
      # display them
      #
      groups = (data.group for data, i in options).length > 1
      
      options_block = []

      if groups
        in_group = false
        # In order to make sure the new changes work with the old code, there
        # are no groups with members to iterate.  Thus, we add optgroup
        # whenever a group is detected, and end the tag when it goes away.
        #
        for data, i in options
          if data.group
            if not in_group
              options_block.push "</optgroup>"
            options_block.push """<optgroup label="#{data.group.self_name}">"""
            in_group = true

          options_block.push """
            <option value="#{data.from.iso}-#{data.to.iso}">
            #{data.from.name} → #{data.to.name}
            </option>
          """

        options_block.push "</optgroup>"

      else
        for data, i in options
          options_block.push """
            <option value="#{data.from.iso}-#{data.to.iso}">
            #{data.from.name} → #{data.to.name}
            </option>
          """
      return options_block.join('\n')
  
    el = $("""
    <div id="webdict_options">
      <div class="well">
      <a class="close" href="#" style="display: none;">&times;</a>
      <div class="trigger">
        <h1><a href="#" class="open">#{_("Á")}</a></h1>
      </div>

      <div class="option_panel" style="display: none;">
        <ul class="nav nav-pills">
          <li class="active">
            <a href="#" data-target="#options">#{ _("Options") }</a>
          </li>
          <li><a href="#" data-target="#help">#{ _("Help") }</a></li>
          <li><a href="#" data-target="#about">#{ _("About") }</a></li>
          <li style="display: none;" id="debug"><a href="#" data-target="#advanced">#{ _("Advanced") }</a></li>
        </ul>
        <div id="options" class="minipanel">
          <form class="">
            <label class="control-label" for="inputEmail">#{ _("Dictionary") }</label>
            <select type="radio"
                   name="language_pair">
            #{makeLanguageOption(opts.dictionaries)}
            </select>
            <br />
            <button type="submit" class="btn" id="save">#{_('Save')}</button>
          </form>
        </div>
        <div id="advanced" style="display: none;" class="minipanel">
          <br />
          <strong>Advanced settings</strong>
          <p>This deletes all stored settings, dictionary names, and translations of the application.</p>
          <a href="#" type="submit" class="btn btn-small" id="refresh_settings">#{_('Refresh settings')}</a>
          <br />
          <br />
          <strong>Hostname:</strong>
          <blockquote><pre>#{API_HOST}</pre></blockquote>
          <strong>Alerts:</strong>
          <p>Display an alert for debugging.</p>
          <a href="#" type="submit" class="btn btn-small" id="display_update_window">#{_('Update detected')}</a>
          <a href="#" type="submit" class="btn btn-small" id="display_ie8_warning_window">#{_('IE8 Warning')}</a>
          <br />
          <br />
        </div>
        <div id="help" style="display: none;" class="minipanel">
            <p>#{ _("In order to look up a word, hold down the <em>Alt</em> or <em>Option</em> (⌥) key, and doubleclick on a word. The service will contact the dictionary, and return a word after a short pause.") }</p>
            <p> </p>
            <p>#{ _('If you find a bug, or if the bookmark does not work on a specific page <a href="mailto:giellatekno@hum.uit.no">please contact us</a>. Tell us what page didn\'t work, or what you did when you discovered the problem.') }
            </p>
        </div>
        <div id="about" style="display: none;" class="minipanel">
            <p>#{ _("This tool was made by Giellatekno at UiT: The Arctic University of Norway.") }</p>

            <ul id="about-links" class="nav nav-tabs nav-stacked">
              <li><a href="http://sanit.oahpa.no/about/">#{ _("Read more") }</a></li>
              <li><a href="http://oahpa.no">#{ _("More tools") }</a></li>
            </ul>
        </div>
      </div>
    </div>
    """)
    
    el.find('ul.nav-pills a').click (evt) ->
      target_element = $(evt.target).attr('data-target')
      el.find('ul.nav-pills a').parent('li').removeClass('active')
      $(evt.target).parent('li').addClass('active')
      el.find('div.minipanel').hide()
      el.find(target_element).show()
      return false

    el.find('.trigger').click () ->
      optsp = el.find('div.option_panel')
      optsp.toggle()
      el.find('a.close').toggle()
      return false

    el.find('a.close').click () ->
      optsp = el.find('div.option_panel')
      optsp.toggle()
      el.find('a.close').toggle()
      return false
    
    el.find('button#save').click () ->
      optsp = el.find('div.option_panel')
      optsp.toggle()
      el.find('a.close').toggle()
      return false

    el.find('a#refresh_settings').click () ->
      DSt.set(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair', null)
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-languages', null)
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-localization', null)
      DSt.set(NDS_SHORT_NAME + '-' + 'nds-stored-config', null)
      el.find('#advanced').append $('<p />').html("Reload the plugin...")
      delete window.lookup_regex
      # window.location.reload()
      return false

    el.find('a#display_update_window').click () ->
      window.newVersionNotify()
      return false
    
    el.find('a#display_ie8_warning_window').click () ->
      window.ie8Notify()
      return false

    el.find('select[name="language_pair"]').change (e) ->
      store_val = $(e.target).val()
      DSt.set(NDS_SHORT_NAME + '-' + 'digisanit-select-langpair', store_val)
      delete window.lookup_regex
      return true

    el.find('form').submit () ->
      optsp = el.find('div.option_panel')
      optsp.toggle()
      el.find('a.close').toggle()
      return false
    
    return el

  ErrorBar: (args) ->
    # NB: overriding underscorejs here.
    host = args.host
    el = $("""
     <div id="nds_errors" class="errornav navbar-inverse navbar-fixed-bottom">
       <div class="navbar-inner">
         <div class="container">
           <p><strong>#{_("Error!")}</strong> #{_("Could not connect to dictionary server")} (host: #{host}).
              <a href="#" class="dismiss">#{_("Close")}</a>.</p>
         </div>
       </div>
     </div>
     """)
    el.find('a.dismiss').click () ->
      $('body .errornav').remove()
      return false
    return el

