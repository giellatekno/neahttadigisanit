
// https://github.com/scottschiller/SoundManager2/
//
// http://www.schillmania.com/projects/soundmanager2/doc/getstarted/#basic-inclusion


// TODO: add loading and playing icons 
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

       btn.preventDefault();

       audio = $(btn.target).attr('href');
       console.log(audio);

       function finished_event() {
         soundManager.destroySound('dictionary-player');
         return true;
       }

       sound_obj = soundManager.createSound({
         id: "dictionary-player",
         url: audio,
         onfinish: finished_event
         // onerror: error_event
         // onplay: begin_event
         // whileloading: whileload_event
       });
       // sound_obj._a.playbackRate = opts.rate;

       sound_obj.play({position:0});
        
    });
});

// <script src="soundmanager2-nodebug-jsmin.js"></script>


