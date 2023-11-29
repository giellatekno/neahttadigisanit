$(document).ready( function() {
  $('input[name="lookup"]').typeahead({
    items: 5,
    source: function (typeahead, query) {
      var _from = $(document).find('#neahttadigisanit').attr('action').split('/')[1]
        , _to   = $(document).find('#neahttadigisanit').attr('action').split('/')[2]
        , url = '/autocomplete/' + _from + '/' + _to + '/'
        ;
      if (query.length > 1) {
        return $.get(url, { lookup: query }, function (data) {
          return typeahead.process(data);
        });
      } else {
        return [] ;
      }
    }
  });

 $(document).find('#langpairs li a').click(function(obj) {
   console.log(obj);
   var elem    = $(obj.target).parent('a');
   var new_val = $(obj.target).attr('data-value') ||
                 $(elem).attr('data-value') ;
   var _from = new_val.split('-')[0]
     , _to   = new_val.split('-')[1]
     ;
   var _url   = "/" + (_from) + "/" + (_to) + "/"
     , _label = "" + (_from) + " → " + (_to)
     ;
   $(document).find('#neahttadigisanit button span.val_name').html(_label);
   var url_base = $(document).find('#neahttadigisanit').attr('data-url-base') || "";
   $(document).find('#neahttadigisanit').attr('action', url_base + _url);
 });

});
$(document).keypress(function(event) {
  // console.log(event.which);
  // alt+shift+ + or ¿
  if ( event.which == 191 ) {
     $('.debug-hidden').toggle();
   }
});
