$(document).ready(function(){

    var input_field = 'input[name="lookup"]'
      , submit_button = 'button[type="submit"]'
      , input_form = 'form'
      ; 

    // Unregister the submit event that prevents null submitting
    $(input_form).unbind('submit');

    // TODO: form submit method to convert current contents to keyword
    // if the user has clicked submit without adding a keyword
    function test_submit (e) {
        var items = $('input[name="lookup"]').tagsinput('items');
        var text_entered = $('input.tt-input').val();
        console.log(text_entered);

        if (items.length == 0 && text_entered.length > 0) {
            // convert text into a tag item
            $(input_field).tagsinput('add', text_entered);
            console.log('no items');
            e.preventDefault();
        }

        return true;
    }

    $(submit_button).click(test_submit);
    $('form').submit(test_submit);

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
        confirmKeys: [13, 32, 44],
        trimValue: true,
        typeaheadjs: {
            name: 'keywords',
            displayKey: 'name',
            valueKey: 'name',
            source: keywordnames.ttAdapter()
        }
    });

    // $(input_field).on('itemAdded', function(event) {
    //   // TODO: clear typeahead

    // });

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

});
