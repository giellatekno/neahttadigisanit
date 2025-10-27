var url = "https://api-giellalt.uit.no/tts/se/biret";
var cache = {};
function noop() {}

function audio_create(blob) {
    var audio = document.createElement("audio");

    if (!audio.canPlayType("audio/mpeg")) {
        console.error("browser can't play audio/mpeg");
        return null;
    }

    audio.setAttribute("autoplay", "");
    var source = document.createElement("source");
    var url = URL.createObjectURL(blob);
    source.setAttribute("type", "audio/mpeg");
    source.setAttribute("src", url);
    audio.appendChild(source);
    return audio;
}

function query_giellalt_api(opts) {
    var text = opts.text;
    var on_success = noop;
    var on_error = noop;

    if (typeof opts.on_success == "function")
        on_success = opts.on_success;
    if (typeof opts.on_error == "function")
        on_error = opts.on_error;

    var req = new XMLHttpRequest();
    req.responseType = "blob";

    req.onreadystatechange = function () {
        if (req.readyState != XMLHttpRequest.DONE) return;

        if (req.status == 200) {
            on_success(req.response);
        } else {
            on_error(1, req);
        }
    };

    req.open("POST", url);
    req.setRequestHeader("Content-Type", "application/json");

    try {
        req.send('{"text": "' + text + '"}');
    } catch (err) {
        console.error("Couldn't send request", err);
        on_error(2, err);
    }
}

function play_tts(text) {
    var cached = cache[text];
    if (cached) {
        cached.play();
        return;
    }

    query_giellalt_api({
        text: text,
        on_success: function (blob) {
            var audio = audio_create(blob);
            cache[text] = audio;
            document.body.appendChild(audio);
        },
        on_error: function (type, obj) {
            switch (type) {
                case 1:
                    console.error("status != 200");
                    console.error(obj);
                    break;
                case 2:
                    console.error("exception thrown in req.send():");
                    console.error(obj);
                    break;
            }
        },
    });
}

window.play_tts = play_tts;
