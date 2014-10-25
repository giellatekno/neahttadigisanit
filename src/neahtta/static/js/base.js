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

    var unblurable = false;

    if (!_im_listening) {
        $("#keyboard").mousedown(function() {
            window.click_in_keyboard = true;
        });

        $("#keyboard").bind('touchstart', function(){
            window.click_in_keyboard = true;
        })

        $('#keyboard a').click(function(_char){
            _im_listening = true;
            var _val = $(current_input).val()
              , _c   = $(_char.target).attr('data-char')
              ;
            $(current_input).val(_val + _c)
                                   .trigger("keyup")
                                   .focus()
                                   ;
            return false;
        });
    }

    $('#keyboard ul').css({width:(($('#keyboard ul li').length) * 40) + "px"});

    $(window).resize(function(o){
        // TODO: responsive
        if($(document).width() > 801) {

            var input_bottom_end = $(current_input).offset().top + $(current_input).height() + 15
              , input_left_end   = $(current_input).offset().left
              ;

            $('#keyboard').css({
                top: input_bottom_end,
                left: input_left_end,
            });

        } else {
            $('#keyboard').css({
                top: null,
                left: 0,
                bottom: 0,
                position: "fixed",
            });
        }

    });

    $("input").focus(function(o){
        $('#keyboard').fadeIn();

        window.current_input = o.target;

        // On desktops we position this floating under the input, so, determine
        // the input location
        if($(document).width() > 801) {

            var input_bottom_end = $(current_input).offset().top + $(current_input).height() + 15
              , input_left_end   = $(current_input).offset().left
              ;

            $('#keyboard').css({
                top: input_bottom_end,
                left: input_left_end,
            });

        }

    });

    $("input").blur(function(o) {
        if (window.click_in_keyboard) {
            window.click_in_keyboard = false;
        } else {
            // The keyboard is more in the way on desktop widths, so, need to hide
            // when not in use
            //
            if (!unblurable){
                $("#keyboard").fadeOut();
            }
        }

    });

});
