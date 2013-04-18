<script type="text/javascript">
    // TODO: update
    // Language select
    // $(document).ready(function(){
    // 	var has_lang = DSt.get('nds-ui-lang');
    // 	if (has_lang) {
    // 	    $('body').prop('lang', has_lang);
    // 	}
    // 	$('#language_select a.lang').click( function(evt) {
    // 		var lang = $(evt.target) ;
    // 		var iso  = lang.attr('data-lang');
    // 		DSt.set('nds-ui-lang', iso);
    // 		$('body').prop('lang', iso);
    // 		return false;
    // 	});
    // });

    var _im_listening = false;
    $(document).ready(function(){
        $(window).resize(function(o){
            $('a.last').html(window.outerHeight);

        });
        $("input").focus(function(o){
            $('#keyboard').show();
            // $('#keyboard').css({top:window.outerHeight + "px"});
            var _h = window.outerHeight - $('#keyboard').height();
            $('#keyboard').css({top: _h-100})

            if (!_im_listening) {
                $('#keyboard a').click(function(_char){
                    _im_listening = true;
                    var _val = $(o.target).val()
                      , _c   = $(_char.target).attr('data-char')
                      ;
                    $(o.target).val(_val + _c)
                               .trigger("keyup")
                               .focus()
                               ;
                    return false;
                });
            }
        });
    });
</script>
