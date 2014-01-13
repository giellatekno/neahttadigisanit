// For Firefox: reenable buttons when back button is pressed
$(window).bind("unload", function() {
    $('input').attr('readonly', false);
    $('button').attr('disabled', false);
});

$(document).ready( function() {
    $('input[name="lookup"]').typeahead({
        items: 5,
        source: function (typeahead, query) {
            if (query.length > 1) {
                var _from = typeahead.$element.attr('data-language-from')
                    , _to = typeahead.$element.attr('data-language-to')
                    , url = '/autocomplete/' + _from + '/' + _to + '/'
                    ;
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

    // Korp search redirect
    $('.korp_search').click(function(evt) {
        var search_url = $(evt.target).attr('data-search-url')
          , search_del = $(evt.target).attr('data-search-delim')
          , user_input = $('input[type="text"]').val()
          ;

        if (user_input.search(' ') > -1) {
            user_input = user_input.split(' ').join(search_del);
        };
        var redirect_url = search_url.replace('USER_INPUT', user_input);
        window.location = redirect_url;
        return evt.preventDefault();
    });

    // Discourage submission if there is nothing to submit
    $('form').submit(function(evt) {
        var inputs = $(evt.target).find('input[type="text"]')
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
    });

    // $('.example_set button').click(function(evt) {
    // 	var target = $(evt.target).parents('.example_set')
    // 	                          .find('blockquote.examples') ;
    // 	console.log(target) ;
    // 	if (target.hasClass('hidden-phone')) {
    // 	    target.hide();
    // 	    target.removeClass('hidden-phone') ;
    // 	    target.slideDown() ;
    // 	} else {
    // 	    target.slideUp(400, function(){
    // 	        target.hide();
    // 	        target.addClass('hidden-phone') ;
    // 	    }) ;
    // 	}
    // });
});

