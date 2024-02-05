// For Firefox: reenable buttons when back button is pressed
$(window).bind("unload", function() {
    $('input').attr('readonly', false);
    $('button').attr('disabled', false);
});

$(document).ready( function() {
    // Select everything when the document loads
    // $('input[name="lookup"]').select();

    // Doublecheck focus-- need to retrigger the event because sometimes it
    // isn't properly trigggered 
    //
    if($(document).width() > 801) {
        setTimeout(function() {
            $('input[name="lookup"]').focus().select();
        }, 120);
    }

    var item_count = parseInt($('input[name="lookup"]').attr('data-items')) || 5;
    $('input[name="lookup"]').typeahead({
        items: item_count,
        source: function (typeahead, query) {
            if (query.length > 1) {
                var _from = typeahead.$element.attr('data-language-from')
                    , _to = typeahead.$element.attr('data-language-to')
                    , default_autocomplete = '/autocomplete/' + _from + '/' + _to + '/'
                    ;
                var url = $('input[name="lookup"]').attr('data-autocomplete-path') || default_autocomplete;
                return $.get(url, { lookup: query }, function (data) {
                    return typeahead.process(data);
                });
            } else {
                return [] ;
            }
        }
    });
    $('input').focus(function(evt) {
        $('input').attr('readonly', false);
        $('button').attr('disabled', false);
    });

    // Discourage submission if there is nothing to submit
    $('form').submit(function(evt) {
        var inputs = $(evt.target).find('input[type="text"]')
          , target = $(evt.target).find('button[type=submit][clicked=true]')
          , submit = $(evt.target).find('button[type="submit"]')
          ;
        for (_i = 0, _len = inputs.length; _i < _len; _i++) {
            i = inputs[_i];
            if ($(i).val().length === 0) {
                return false;
            } else {
                continue;
            }
        }

        inputs.prop("readonly", true);
        submit.prop("disabled", true);

        // Re-enable the form elements after a delay.
        setTimeout(function(){
            inputs.prop("readonly", false);
            submit.prop("disabled", false);
        }, 1000);

    });

});

// vim: set ts=4 sw=4 tw=0 syntax=javascript :
