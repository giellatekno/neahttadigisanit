function readTests() {
    var projname = $('#test_palette').attr('data-projname');
    var test_store_key = projname + '-tests';

    function renderTestList() {
        // var example = [
        //     {id: "test_1", text: "mõõnnâd", link:
        //         "/detail/sms/fin/mõõnnâd.html"},
        //     {id: "test_2", text: "čuäcc", link: "/detail/sms/eng/čuäcc.html"},
        // ];
         
        function renderLi(t) {
            var li = $("<li class='item' />")
              , lw = $("<a class='fav' href='" + t.link + "'>" + t.text + "</a>")
              , ed = $("<a href='#' style='display: none;' class='edit'>(edit)</a>")
              , rm = $("<a href='#' style='display: none;' class='delete'>(delete)</a>")
              ;

            li.attr('id',  t.id);
            lw.href = t.link;
            lw.appendTo(li);
            ed.appendTo(li);
            rm.appendTo(li);

            return li;
        }

        var tests = DSt.get(test_store_key) || [];
        // var tests = DSt.get(test_store_key) || example;

        var test, i, len;

        var list = $('ul#test_list');
        list.find('li').remove();

        for (i = 0, len = tests.length; i < len; i++) {
          test = tests[i];
          list.append(renderLi(test));
        }
        return tests;
    }

    tests = renderTestList();

    $('#test_palette .add').click(function(o){
        $('#add_form').toggle();

    });
    $('#test_palette .edit_list').click(function(o){
        $('#test_list .edit').toggle();
        $('#test_list .delete').toggle();

    })

    // TODO: deletion link
    $('#test_list .delete').click(function(o){
        var container = $(o.target).parents('li');
        var fav = container.find('.fav');

        var link = fav.attr('href')
          , text = fav.text();

        var pop_i = false;

        for (i = 0, len = tests.length; i < len; i++) {
          test = tests[i];
          if (test.link == link && test.text == text) {
              var pop_i = i;
          }
        }

        if (pop_i) {
          tests.splice(pop_i, 1);
          DSt.set(test_store_key, tests);
        }

        renderTestList();
    });

    // TODO: edit link
    $('#test_list .edit').click(function(o){
        console.log(tests);
    });

    $('#add_form button[type=submit]').click(function(o){

        var text = $("input[name='text']").val()
          , link = $("input[name='link']").val()
          ;

        tests.push({
            text: text,
            link: link,
        });

        DSt.set(test_store_key, tests);

        $("input[name='text']").val('');
        $("input[name='link']").val('');

        $('#add_form').hide();

        renderTestList();

    });
}

$(document).ready(function(){
    if ( $("#test_palette") && window.location.hostname == "localhost" ) {

        $("#test_palette").show();

        $(".test_palette_toggle").click(function(o) {
            $("#test_palette #test_content").toggle();
            $("#test_palette .toggle_show").toggle();
            $("#test_palette .toggle_hide").toggle();
            // TODO: store visibility status in DSt
        });

        readTests();
    }
});

