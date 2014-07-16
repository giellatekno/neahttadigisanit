module.Templates = @Templates =

  NotifyWindow: (text) ->
    _ = module.fakeGetText
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
    _ = module.fakeGetText
    makeLanguageOption = (options) ->
      options_block = []
      for data, i in options
        if i+1 == 1
          checked = "checked"
        else
          checked = ""

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
    _ = module.fakeGetText
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

