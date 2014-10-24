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

    if (!_im_listening) {
        $('#keyboard a').click(function(_char){
            window.unblurable = true;
            _im_listening = true;
            var _val = $(current_input.target).val()
              , _c   = $(_char.target).attr('data-char')
              ;
            $(current_input.target).val(_val + _c)
                                   .trigger("keyup")
                                   .focus()
                                   ;
            window.unblurable = false;
            return false;
        });
    }
    $('#keyboard ul').css({width:(($('#keyboard ul li').length) * 40) + "px"});
    $("input").focus(function(o){
        $('#keyboard').fadeIn();
        window.current_input = o;

        // $('#keyboard').css({top:window.outerHeight + "px"});
        //
        // var _h = window.outerHeight - $('#keyboard').height();
        // $('#keyboard').css({top: _h-100})

    });
    // TODO: fade out when not in use
    // $("input").blur(function(o) {
    //     if (!unblurable){
    //         $("#keyboard").fadeOut();
    //     }
    // });
});
