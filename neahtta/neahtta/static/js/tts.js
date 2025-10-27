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

function show_spinner(button) {
    for (var i = 0; i < button.children.length; i++) {
        var child = button.children[i];
        var tagName = child.tagName.toUpperCase();
        console.debug("show_spinner(): loop! tagName=" + tagName);
        if (tagName == "SVG") {
            console.debug("show_spinner(): child tag is SVG");
            add_class(child, "hidden");
        } else if (tagName == "SPAN") {
            console.debug("show_spinner(): child tag is SPAN");
            remove_class(child, "hidden");
        }
    }
}

function hide_spinner(button_element) {
    for (var i = 0; i < button_element.children.length; i++) {
        var child_element = button_element.children[i];
        var tagName = child_element.tagName.toUpperCase();
        console.debug("hide_spinner(): loop! tagName=" + tagName);
        if (tagName == "SVG") {
            console.debug("hide_spinner(): child tag is SVG");
            remove_class(child_element, "hidden");
        } else if (tagName == "SPAN") {
            console.debug("hide_spinner(): child tag is SPAN");
            add_class(child_element, "hidden");
        }
    }
}

function add_class(element, klass) {
    console.debug("add_class()", element, klass);
    var classes = element.getAttribute("class").split(/ +/);
    if (!classes.includes(klass)) {
        console.debug("add_class(): adding..");
        classes.push(klass);
        element.setAttribute("class", classes.join(" "));
    } else {
        console.debug("add_class(): class '" + klass + "' already exist on the element");
    }
}

function remove_class(element, klass) {
    console.debug("remove_class()", element, klass);
    var classes = element.getAttribute("class").split(/ +/);
    var idx = classes.indexOf(klass);
    if (idx >= 0) {
        console.debug("remove_class(): removing");
        classes.splice(idx, 1);
        element.setAttribute("class", classes.join(" "));
    } else {
        console.debug("remove_class(): doesnt exist");
    }
}

function play_tts(event, text) {
    var cached = cache[text];
    if (cached) {
        cached.play();
        return;
    }

    var button_element = event.currentTarget;

    console.debug("play_tts()");
    console.debug(button_element);

    show_spinner(button_element);

    query_giellalt_api({
        text: text,
        on_success: function (blob) {
            console.debug("on_success() callback function");
            hide_spinner(button_element);
            var audio = audio_create(blob);
            cache[text] = audio;
            document.body.appendChild(audio);
        },
        on_error: function (type, obj) {
            console.debug("on_error() callback function");
            hide_spinner(event.target);
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
