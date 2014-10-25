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

    if($('#keyboard').length > 0) {

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

        (function() {

            // Do not run on desktop widths, they probably need another solution
            if ($(document).width() > 801) {
                return false;
            }

            // Determine whether all elements are visible:
            //  * run on an interval, because this is an expensive calculation for
            //    the dom to perform without a small delay
            //  * clear the function after a number of iterations
            //  * each time elements fall outside, double the height
            //  TODO: rerun on window resize?

            expand = false;
            outside_count = 1;
            position_fixed_attempts = 0;

            poll_i = setInterval(function() {
                position_fixed_attempts += 1;

                if (outside_count > 0) {

                    // How many elements are outside?
                    $('#keyboard ul li').each( function(i, elem) {
                        var doc_top = $(window).scrollTop();
                        var doc_bot = doc_top + $(window).height();

                        var elem_top = $(elem).offset().top;
                        var elem_bot = elem_top + $(elem).height();

                        if ((elem_bot <= doc_bot) && (elem_top >= doc_top)) {
                            expand = true;
                            outside_count += 1;
                        }
                    })

                    // Double height
                    if (expand) {
                        var h = $('#keyboard').height();
                        $('#keyboard').height(h*2);
                        outside_count = 0;
                    }
                }

                // Clear handler once we've run this several times
                if (position_fixed_attempts > 7) {
                    clearInterval(poll_i);
                }
            }, 200);

        })();

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

                var input_bottom_end = $(current_input).offset().top + $(current_input).height() + 20
                  , input_left_end   = $(current_input).offset().left
                  ;

                $('#keyboard').css({
                    top: input_bottom_end,
                    left: input_left_end,
                });

                $('.form-row').animate({
                    "padding-bottom": "35px",
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
                    $('.form-row').animate({
                        "padding-bottom": "0px",
                    });
                }
            }

        });
    }

});
