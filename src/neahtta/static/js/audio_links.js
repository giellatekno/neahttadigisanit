
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

    $('[data-audio-player]').click( function(btn){

       btn.preventDefault();

       audio = $(btn.target).attr('data-audio-target');
       console.log(audio);

       function finished_event() {
         soundManager.destroySound('dictionary-player');
         return true;
       }

       function get_player() {
         sound_obj = soundManager.createSound({
           id: "dictionary-player",
           url: '',
           onfinish: finished_event
           // onerror: error_event
           // onplay: begin_event
           // whileloading: whileload_event
         });
         // sound_obj._a.playbackRate = opts.rate;
         return sound_obj;

       }

       sound_obj = get_player();
       sound_obj.url = audio;

       sound_obj.play({position:0});
        
    });
});

// <script src="soundmanager2-nodebug-jsmin.js"></script>


