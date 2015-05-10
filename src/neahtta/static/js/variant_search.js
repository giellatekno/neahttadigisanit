$(document).ready(function(){
    // Unregister the submit event that prevents null submitting
    $('form').unbind('submit');

    // TODO: form submit method to convert current contents to keyword
    // if the user has clicked submit without adding a keyword

    $('form').submit(function(e){
        var items = $('input[name="lookup"]').tagsinput('items');
        // how?
        var text_entered = true;

        if (items.length == 0 && text_entered) {
            // convert text into a tag item
            console.log('no items');
            e.preventDefault();
        }

    });

    var input_field = 'input[name="lookup"]';

    var keywordnames = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: $(input_field).attr('typeahead-source'),
            cache: false,
            transform: function(response) {
                return $.map(response.keywords, function(k) {
                    return { name: k }; });
            }
        }
    });

    keywordnames.initialize();

    // enable tags input on the input field
    $(input_field).tagsinput({
        allowDuplicates: false,
        // ENTER, comma, space
        confirmKeys: [13, 44],
        trimValue: true,
        typeaheadjs: {
            name: 'keywords',
            displayKey: 'name',
            valueKey: 'name',
            source: keywordnames.ttAdapter()
        }
    });

    // When an item is added, remove placeholder text.
    $('form input').on('itemAdded', function(event) {
        $('form input[placeholder]').attr('placeholder', null);
    });


    $('.search_options .add_keyword').click( function(evt){
        // Target is a bit weird, sometimes <span /> sometimes <a />
        var kw = $(evt.target).find('span').attr('data-keyword-value') ||
            $(evt.target).parents('[data-keyword-value]').attr('data-keyword-value');
        ;
        $(input_field).tagsinput('add', kw);

        setTimeout(function(){
            $('form').submit();
        }, 250);

    });

    // TODO: remove keyword triggers search as well.

    // TODO: do not immediately display autosuggest after adding a
    // keyword

});
