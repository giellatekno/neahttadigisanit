// TODO: update
//
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

// Note viewport sizing broken in Android 2.x see http://stackoverflow.com/questions/6601881/problem-with-meta-viewport-and-android
window.getViewport = function (elem) {    
    // http://www.quirksmode.org/mobile/tableViewport.html
    var isTouchDevice = true;
    
    var viewport = {
            left: window.pageXOffset || document.scrollLeft || 0,    
            top: window.pageYOffset || document.scrollTop || 0,
            width: window.innerWidth || document.clientWidth,
            height: window.innerHeight || document.clientHeight
    };
    // iOS *lies* about viewport size when keyboard is visible. See http://stackoverflow.com/questions/2593139/ipad-web-app-detect-virtual-keyboard-using-javascript-in-safari Input focus/blur can indicate, also scrollTop: 
    if (isTouchDevice && elem) {     
        // Fudge factor to allow for keyboard on iPad
        return {
            left: viewport.left,
            top: viewport.top,
            width: viewport.width,
            height: viewport.height * (viewport.height > viewport.width ? 0.66 : 0.45)  
        };
    }
    return viewport;
}

var _im_listening = false;
$(document).ready(function(){

    $(window).resize(function(o){
        $('a.last').html(window.outerHeight);

    });

    if($('[data-toggle=tooltip]').length > 0) {
        $('[data-toggle=tooltip]').tooltip();
    }
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
                if (_c) {
                    $(current_input).val(_val + _c)
                                           .trigger("keyup")
                                           .focus()
                                           ;
                }
                return false;
            });
        }

        $('#keyboard ul').css({width:(($('#keyboard ul li').length) * 40) + "px"});

        (function() {
            return false;

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

                // var input_bottom_end = $(current_input).offset().top + $(current_input).height() + 15
                //   , input_left_end   = $(current_input).offset().left
                //   ;

                // $('#keyboard').css({
                //     top: input_bottom_end,
                //     left: input_left_end,
                // });
                $('#keyboard').css({
                    top: null,
                    left: null,
                    bottom: null,
                    position: "inline",
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


        // TODO: resize event for detecting height changes on mobile
        // safari
        // TODO: orientationchange
        // TODO: android sends orientationchange before resize, iOS
        // sends resize before orientationchange

        function keyboard_focus (o) {

            // Test for on screen keyboard
            $(window).scrollTop(10);

            var keyboard_shown = getViewport(o.target).height < document.clientHeight ;
            $(window).scrollTop(0);

            window.current_input = o.target;

            // On desktops we position this floating under the input, so, determine
            // the input location
            if($(document).width() > 801) {

                var input_bottom_end = $(current_input).offset().top + $(current_input).height() + 20
                  , input_left_end   = $(current_input).offset().left
                  ;

                // $('#keyboard').css({
                //     top: input_bottom_end,
                //     left: input_left_end,
                // });

                // $('.form-row').animate({
                //     "padding-bottom": "35px",
                // });

            }

            if (keyboard_shown) {
                $('#keyboard').addClass(keyboard_shown? 'keyboard': 'nokeyboard ');
                var h = getViewport(o.target).height;
                $('#keyboard').css({
                    top: h - $('#keyboard').height() - 20,
                });
            } 

            // $('#keyboard').fadeIn();

        }


        if(localStorage) {
            $('form .input-append').addClass('input-prepend');
            var display_k = localStorage.getItem('nds-kbd-visible');
            if (display_k === "false") {
                $("#keyboard").hide();
                $("form").removeClass('keyboard-visible');
            } else if (display_k === "true") {
                $("form").addClass('keyboard-visible');
            }
        }

        $("#display_keyboard").click(function(o){
            o.preventDefault();

            var nds_kbd_visible = $('#keyboard').is(':visible');

            if (!nds_kbd_visible) {
                // $('form .input-append').removeClass('input-prepend');
                $("#keyboard").fadeIn();
                $("form").addClass('keyboard-visible');
                keyboard_focus(o);
                if(localStorage) {
                    localStorage.setItem('nds-kbd-visible', true);
                }
            } else {
                $("#keyboard").fadeOut();
                $("form").removeClass('keyboard-visible');
                // $('form #display_keyboard').fadeIn();
                if(localStorage) {
                    localStorage.setItem('nds-kbd-visible', false);
                }
            }

        });

        $("input").focus(function(o) {
            // Need a small delay for mobile keyboards to appear.
            setTimeout(function(){
                keyboard_focus(o);
            }, 100);
        });

        $("input").blur(function(o) {
            if (window.click_in_keyboard) {
                window.click_in_keyboard = false;
            } else {
                // The keyboard is more in the way on desktop widths, so, need to hide
                // when not in use
                //
                if (!unblurable){
                    // $("#keyboard").fadeOut();
                    // $('.form-row').animate({
                    //     "padding-bottom": "0px",
                    // });
                }
            }

        });

    }

});
