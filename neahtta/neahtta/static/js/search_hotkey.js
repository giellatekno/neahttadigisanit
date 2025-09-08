function handleKeyPress(event) {
    // should always have "event.key", but just to be sure..
    if (!event.key) return;

    if (event.key != "/" && event.key != "s" && event.key != "S") {
        return;
    }

    var input_el = document.querySelector("input[name=lookup]");
    if (input_el === null) {
        // page has no input[name=lookup], don't try to do anything else
        return;
    }

    var active_el = document.activeElement;
    if (input_el === active_el) {
        // input already active and in focus
        return;
    }

    input_el.focus();
    scroll_to_active_element();

    // don't write the /, s or S into the input
    event.preventDefault();
}

// from rust doc source
// unsure of supprt of activeElement.getBoundingClientRect(), window.scrollBy()
function scroll_to_active_element() {
    var rect = document.activeElement.getBoundingClientRect();
    if (window.innerHeight - rect.bottom < rect.height) {
        window.scrollBy(0, rect.height);
    }
}

$(document).ready(function() {
    document.addEventListener("keydown", handleKeyPress);
});
