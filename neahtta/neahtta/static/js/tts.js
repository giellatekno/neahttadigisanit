var TTS_API_ROOT = "https://api-giellalt.uit.no/tts";
var DEFAULT_SME_VOICE = "biret";

// api requires silly language codes :(
// (that it accepts them is fine, but they should not be required!)
function sillify_langcode(lang) {
    if (lang == "sme") return "se";
    return lang;
}

function get_api_url(lang, voice) {
    console.assert(is_nonempty_str(lang));
    console.assert(is_nonempty_str(voice));
    lang = sillify_langcode(lang);
    voice = voice.toLowerCase();
    return TTS_API_ROOT + "/" + lang + "/" + voice;
}

// key = "lang,voice,text", as a string, of course (all keys are strings in javascript objects (well, except Symbols).
// value = an object with key 'status', and maybe a correspondning object
var CACHE = {};

// The event handler on button click
function play_tts(event) {
    var button = event.currentTarget;
    var text = button.getAttribute("data-tts");
    console.assert(is_nonempty_str(text));
    var lang = button.getAttribute("data-lang");
    console.assert(is_nonempty_str(lang));
    var voice = localstorage_get_voice({ lang: lang });
    console.assert(is_nonempty_str(lang));
    var cached = cache_get({ lang, voice, text });

    if (!cached) {
        start_query(button, {
            spin: true,
            play_when_done: true,
            accept: determine_accept_request_header(),
        });
    } else if (cached.status == "fetched") {
        // will autoplay when added to the DOM
        console.debug("cached.status == \"fetched\", add audio to doc, will autoplay");
        document.body.appendChild(cached.audio);
        cached.status = "in_dom";
    } else if (cached.status == "in_dom") {
        console.debug("cached.status == \"in_dom\", so just play audio");
        cached.audio.play();
    } else if (cached.status == "pending") {
        show_spinner(button);
        var captured_event = event;
        cached.request.addEventListener("load", function () {
            play_tts(captured_event);
        });
    } else if (cached.status == "failed") {
        // nothing to do
        console.log("already failed");
    }
}

function query_giellalt_api(opts) {
    var text = get_arg(opts, "text", { validate: is_nonempty_str });
    var voice = get_arg(opts, "voice", { validate: is_nonempty_str, default: DEFAULT_SME_VOICE });
    var lang = get_arg(opts, "lang", { validate: is_nonempty_str });
    var timeout = get_arg(opts, "timeout", { default: 10 * 1000 });
    var accept = get_arg(opts, "accept", { validate: is_str });
    var cb_opts = { default: noop, validate: is_fn };
    var on_success = get_arg(opts, "on_success", cb_opts);
    var on_error = get_arg(opts, "on_error", cb_opts);
    var on_timeout = get_arg(opts, "on_timeout", cb_opts);

    var req = new XMLHttpRequest();
    req.responseType = "blob";

    req.onreadystatechange = function () {
        if (req.readyState != XMLHttpRequest.DONE) return;

        if (req.status == 200) {
            on_success(req);
        } else {
            on_error(1, req);
        }
    };

    var voice = localstorage_get_voice({ lang: lang });
    req.open("POST", get_api_url(lang, voice));
    req.timeout = timeout;
    req.ontimeout = on_timeout;
    req.setRequestHeader("Accept", accept);
    req.setRequestHeader("Content-Type", "application/json");

    try {
        req.send('{"text": "' + text + '"}');
    } catch (err) {
        console.error("Couldn't send request", err);
        on_error(2, err);
    }

    return req;
}

function start_query(button, opts) {
    var spin = get_arg(opts, "spin", { default: false });
    var play_when_done = get_arg(opts, "play_when_done", { default: false });
    var accept = get_arg(opts, "accept", { validate: is_nonempty_str });

    var text = button.getAttribute("data-tts");
    console.assert(is_nonempty_str(text), "button's data-tts attribute should be non-empty string, not " + text + " (" + type(text) + ")");
    var lang = button.getAttribute("data-lang");
    console.assert(is_nonempty_str(lang), "button's data-lang attribute should be non-empty string, not " + lang + " (" + type(lang) + ")");

    if (spin) {
        show_spinner(button);
    }

    var request = query_giellalt_api({
        text: text,
        accept: accept,
        lang: lang,
        on_success: function (request) {
            hide_spinner(button);
            var blob = request.response;
            var content_type = request.getResponseHeader("Content-Type");
            var audio = audio_create(blob, content_type);
            var voice = localstorage_get_voice({ lang: lang });
            if (play_when_done) {
                document.body.appendChild(audio);
                var value = { status: "in_dom", audio: audio };
                cache_set({ lang, voice, text, value });
            } else {
                var value = { status: "fetched", audio: audio };
                cache_set({ lang, voice, text, value });
            }
        },
        on_error: function (type, obj) {
            hide_spinner(button);
            add_class(button, "unavailable");
            var voice = localstorage_get_voice({ lang: lang });
            var value = { status: "failed", error: obj };
            cache_set({ lang, voice, text, value });
        },
        on_timeout: function () {
            hide_spinner(button);
            add_class(button, "unavailable");
            var voice = localstorage_get_voice({ lang: lang });
            var value = { status: "failed", error: "timeout" };
            cache_set({ lang, voice, text, value });
        },
    });

    var voice = localstorage_get_voice({ lang: lang });
    var value = { status: "pending", request: request };
    cache_set({ lang, voice, text, value });
}

function on_dom_content_loaded(event) {
    var accept_header = determine_accept_request_header();
    var all = document.querySelectorAll("button[data-tts]");
    for (var i = 0; i < all.length; i++) {
        var button = all[i];

        if (accept_header == null) {
            var text = button.getAttribute("data-tts");
            CACHE[text] = { status: "failed", error: "no-audio" };
            add_class(button, "unavailable");
        } else {
            //start_query(button, { accept: accept_header });
        }
    }
}

document.addEventListener("DOMContentLoaded", on_dom_content_loaded);
window.play_tts = play_tts;

function audio_create(blob, content_type) {
    var audio = document.createElement("audio");
    audio.setAttribute("autoplay", "");
    var source = document.createElement("source");
    var url = URL.createObjectURL(blob);
    source.setAttribute("type", content_type);
    source.setAttribute("src", url);
    audio.appendChild(source);
    return audio;
}

function determine_accept_request_header() {
    var audio = document.createElement("audio");
    var mpeg = audio.canPlayType("audio/mpeg");
    if (mpeg == "probably" || mpeg == "maybe") {
        return "audio/mpeg,audio/wav;q=0.9";
    } else {
        var wav = audio.canPlayType("audio/wav");
        return wav ? "audio/wav" : null;
    }
}

function show_spinner(button) {
    for (var i = 0; i < button.children.length; i++) {
        var child = button.children[i];
        var tagName = child.tagName.toUpperCase();
        if (tagName == "SVG") {
            add_class(child, "hidden");
        } else if (tagName == "SPAN") {
            remove_class(child, "hidden");
        }
    }
}

function hide_spinner(button) {
    for (var i = 0; i < button.children.length; i++) {
        var child = button.children[i];
        var tagName = child.tagName.toUpperCase();
        if (tagName == "SVG") {
            remove_class(child, "hidden");
        } else if (tagName == "SPAN") {
            add_class(child, "hidden");
        }
    }
}

function add_class(element, klass) {
    var classes = element.getAttribute("class").split(/ +/);
    if (!classes.includes(klass)) {
        classes.push(klass);
        element.setAttribute("class", classes.join(" "));
    }
}

function remove_class(element, klass) {
    console.assert(is_nonempty_str(klass));
    var classes = element.getAttribute("class").split(/ +/);
    var idx = classes.indexOf(klass);
    if (idx >= 0) {
        classes.splice(idx, 1);
        element.setAttribute("class", classes.join(" "));
    }
}

function set_voice(event) {
    var a_element = event.currentTarget;
    console.assert(a_element.tagName == "A");
    var lang = a_element.getAttribute("data-tts-lang");
    var voice = a_element.getAttribute("data-tts-voice");
    localstorage_set_voice({ lang: lang, voice: voice });
}

function on_open_tts_settings(event) {
    var lang = event.currentTarget.getAttribute("data-from-lang");
    var voice = localstorage_get_voice({ lang: lang });
    if (!voice) {
        voice = DEFAULT_SME_VOICE;
    }
    var all = document.querySelectorAll("a[data-tts-voice]");

    for (var i = 0; i < all.length; i++) {
        var current = all[i];
        var this_voice = current.getAttribute("data-tts-voice");
        var children = current.children;
        
        for (var j = 0; j < children.length; j++) {
            var child_node = children[j];
            if (child_node.tagName == "SPAN") {
                if (voice == this_voice) {
                    child_node.innerHTML = "&#x2713;";
                } else {
                    child_node.innerHTML = "";
                }
            }
        }
    }
}

function cache_get(opts) {
    console.debug("cache_get():" + JSON.stringify(opts));
    var lang = get_arg(opts, "lang", { validate: is_nonempty_str });
    var voice = get_arg(opts, "voice", { validate: is_nonempty_str });
    var text = get_arg(opts, "text", { validate: is_nonempty_str });
    var key = lang + "," + voice + "," + text;
    var hitormiss = (key in CACHE) ? "HIT" : "MISS";
    console.debug("cache_get(\"" + key + "\"): " + hitormiss);
    return CACHE[key];
}

function cache_set(opts) {
    var lang = get_arg(opts, "lang", { validate: is_nonempty_str });
    var voice = get_arg(opts, "voice", { validate: is_nonempty_str });
    var text = get_arg(opts, "text", { validate: is_nonempty_str });
    var value = get_arg(opts, "value", { validate: is_pojo });
    var key = lang + "," + voice + "," + text;
    console.debug("cache_set(\"" + key + "\", " + JSON.stringify(value) + ")");
    CACHE[key] = value;
}

function localstorage_get_voice(opts) {
    var lang = get_arg(opts, "lang", { validate: is_nonempty_str });
    console.debug("localstorage_get_voice(\"" + lang + "\")");
    var value = window.localStorage.getItem("tts-voice-" + lang);
    if (value == null) {
        localstorage_set_voice({ lang, voice: DEFAULT_SME_VOICE });
        return DEFAULT_SME_VOICE;
    }
    return value;
}

function localstorage_set_voice(opts) {
    var lang = get_arg(opts, "lang", { validate: is_nonempty_str });
    var voice = get_arg(opts, "voice", { validate: is_nonempty_str });
    console.debug("localstorage_set_voice(\"" + lang + "\", \"" + voice + "\")");
    window.localStorage.setItem("tts-voice-" + lang, voice);
}

window.set_voice = set_voice;
window.on_open_tts_settings = on_open_tts_settings;

function get_arg(opts, param_name, argopts) {
    if (!is_pojo(opts)) {
        throw Error("BAD INTERNAL CALL: get_arg(): argument 'opts': expected a pojo, found " + type(opts));
    }

    var validate = always_true;
    if (is_pojo(argopts) && ("validate" in argopts)) {
        var val = argopts.validate;
        if (!is_fn(val)) {
            throw Error("BAD INTERNAL CALL: 'validate' argopts must be a function");
        } else {
            validate = val;
        }
    }

    if (opts.hasOwnProperty(param_name)) {
        var value = opts[param_name];
        if (!validate(value)) {
            throw Error("param '" + param_name + "' failed validation: " + value);
        }

        return value;
    } else {
        if (!!argopts && argopts.hasOwnProperty("default")) {
            var value = argopts.default;
            if (!validate(value)) {
                throw Error("param '" + param_name + "' failed validation: " + value);
            }
            return value;
        } else {
            throw Error("argument '" + param_name + "' is required");
        }
    }
}


function type(obj) {
    if (obj === null) return "null";
    if (obj === undefined) return "undefined";
    return obj.constructor.name;
}
function is_str(val) { return typeof val == "string"; }
function is_fn(val) { return typeof val == "function"; }
function is_nonempty_str(val) { return is_str(val) && val.length > 0; }
function is_pojo(val) {
    if (typeof val != 'object') return false;
    if (val == null) return false;
    var proto = Object.getPrototypeOf(val);
    return proto == null || proto == Object.prototype;
}
function always_true() { return true; }
function noop() {}
