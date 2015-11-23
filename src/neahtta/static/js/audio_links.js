
// https://github.com/scottschiller/SoundManager2/
//
// http://www.schillmania.com/projects/soundmanager2/doc/getstarted/#basic-inclusion


$(document).ready(function(){
    soundManager.setup({
      url: '/static/vendor/SoundManager2/swf/',
      flashVersion: 9, // optional: shiny features (default = 8)
      // optional: ignore Flash where possible, use 100% HTML5 mode
      // preferFlash: false,
      onready: function() {
        // Ready to use; soundManager.createSound() etc. can now be called.
        console.log("soundmanager ready");
      }
    });

    $('a.audio-link').click( function(btn){

       console.log("audio-link");
       console.log( $(btn).prop('href'))
       btn.preventDefault();
       sound_obj = soundManager.createSound({
         id: "dictionary-player",
         url: $(btn).prop('href'),
         // onfinish: finished_event
         // onerror: error_event
         // onplay: begin_event
         // whileloading: whileload_event
       });
       // sound_obj._a.playbackRate = opts.rate;

       sound_obj.play({position:0});
        
    });
});

// <script src="soundmanager2-nodebug-jsmin.js"></script>


