// deliberately written so it can be built with --target=es5 in esbuild,
// to be able to support as many old systems as we can (and we have potentially
// at least some users of old systems (I have seen old internet explorer in the
// logs, for example).... so, that means:
// only "var", no classes, no template strings, no async, no "for of",
// no arrow functions, no fetch() - only XMLHttpRequest (but only the old parts!), 
// no element.classlist (use classname and do it yourself), no element.dataset
// (use element.getAttribute("data-xxx"))

var lang_from;
var lang_to;
var b;

function Autocomplete(anchor) {
    this.visible = false;
    this.anchor = anchor;
    this.element = document.createElement("ul");
    this.element.classList.add("typeahead", "dropdown-menu");

    this.search_note = this._create_search_note_element();

    document.body.append(this.element);
    this.anchor.addEventListener("input", this.on_input.bind(this));
    window.addEventListener("keydown", on_keydown.bind(this));
    window.addEventListener("click", on_window_click.bind(this));
    window.addEventListener("resize", this.show.bind(this));
}

function on_window_click(ev) {
    // if we click on the keyboard buttons, we don't want to close the
    // autosuggestions
    if (ev.target.tagName == "A" && ev.target.classname == "key") {
        // this is handled below, but crucially we don't hide() here
    } else if (ev.target.tagName == "input" && ev.target.getAttribute("name") == "lookup") {
        // clicked on input element, do nothing
    } else {
        // otherwise, hide the autosuggestions
        this.hide();
    }
}

function on_keydown(ev) {
    if (ev.keyCode == 27) {
        this.hide();
    }
}

Autocomplete.prototype = {
    constructor: Autocomplete,
    clear: function() {
        while (this.element.firstChild) {
            this.element.removeChild(this.element.firstChild);
        }
    },

    append_items: function(search_term, items) {
        var self = this;
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            // the i + 1 is tabindex, so will start at 2 (input element has
            // tabindex 1)
            var li = this._create_item(item, search_term.length, i + 2);
            li.addEventListener("click", function(ev) {
                self.anchor.value = ev.target.innerText;
                self.hide();
                self.anchor.focus();
                //window.location.href = `/${lang_from}/${lang_to}/?lookup=${word}`;
                
                // experimental web api
                //window.navigate(`/${lang_from}/${lang_to}/?lookup=${word}`);
            });
            this.element.append(li);
        }
    },

    // takes "obj", because it can be both an actual event,
    // or just the input element directly if calling it manually
    on_input: function on_input(obj) {
        var element = (obj instanceof Event) ? obj.target : obj;

        var text = element.value;

        this.clear();
        if (text.length >= 2) {
            var url = "/autocomplete/" + lang_from + "/" + lang_to + "/?lookup=" + text;
            var request = new XMLHttpRequest();

            var self = this;
            request.open("GET", url);
            request.onreadystatechange = function (ev) {
                if (request.readyState !== XMLHttpRequest.DONE) return;
                var items = JSON.parse(request.responseText);
                if (items.length === 0) {
                    self.hide();
                    return;
                }

                items = items.slice(0, 15);
                // when showing autocomplete suggestions, alter tabindexes
                // so that tab works intuitively
                self.anchor.tabIndex = 1;
                self.element.appendChild(self.search_note);
                self.append_items(text, items);
                self.show();
            };
            request.send();
        } else {
            this.hide();
        }
    },

    show: function() {
        this.visible = true;
        this.place();
    },

    hide: function() {
        this.anchor.tabIndex = 0;
        this.visible = false;
        this.place();
    },

    place: function() {
        if (!this.visible) {
            this.element.style = `display: none;`;
            return;
        }
        var rect = this.anchor.getBoundingClientRect();
        var top = rect.top + rect.height;
        var left;
        if (window.screen.width <= 400) {
            // super rudimentary responsive design, but it's better than
            // not doing anything
            left = 20;
        } else {
            left = rect.left;
        }
        this.element.style = `display: block; top: ${top}px; left: ${left}px;`
    },

    _create_item: function(text, highlight_length, index) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#";
        a.tabIndex = index;
        a.dataset.value = text;
        a.addEventListener("click", () => {
            this.hide();
        });

        var strong_el = document.createElement("strong");
        strong_el.innerText = text.slice(0, highlight_length);
        var text_node = document.createTextNode(text.slice(highlight_length));

        a.appendChild(strong_el);
        a.appendChild(text_node);
        li.append(a);

        return li;
    },

    _create_search_note_element: function() {
        var li = document.createElement("li");
        var a = document.createElement("a");
        var span = document.createElement("span");
        li.classList.add("search_note");
        a.href = "#";
        span.innerText = this.anchor.dataset.autocompleteText;
        a.appendChild(span);
        li.appendChild(a);
        return li;
    }
};

document.addEventListener("DOMContentLoaded", function() {
    var input_element = document.querySelector('input[name="lookup"]');
    lang_from = input_element.dataset.languageFrom;
    lang_to = input_element.dataset.languageTo;

    var ac = new Autocomplete(input_element);

    var keys = document.querySelectorAll("div#keyboard a.key");
    for (var i = 0; i < keys.length; i++) {
        var key_element = keys[i];
        key_element.addEventListener("click", function (ev) {
            // note: key_element in here will refer to the last element:
            // var variables doesn't "freeze" for each use inside of it.
            input_element.value += ev.target.getAttribute("data-char");
            input_element.focus();
            ac.on_input(input_element);
        });
    }
});
